# backend/assessment/diagnostic_service.py
"""
ROLE: DIAGNOSTIC ASSESSMENT SERVICE

Evaluates learner capabilities across 5 separate evidence dimensions:
- Grammar
- Vocabulary Recognition
- Vocabulary Recall
- Vocabulary Usage
- Vocabulary Sense
Feeds evidence into Learner Knowledge Model without overwriting learner state arbitrarily.
Preserves independence between Grammar & Vocabulary and distinct Vocabulary Senses.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from backend.assessment.assessment_models import (
    AssessmentQuestion,
    AssessmentSession,
    AssessmentSubmission,
    AssessmentType,
    DiagnosticDimension,
    DiagnosticReport,
)
from backend.assessment.assessment_repository import AssessmentRepository
from backend.curriculum import CurriculumService
from backend.learner import LearnerService, MasteryService


class DiagnosticService:
    """
    Orchestrates Diagnostic Assessments and produces 5-dimension diagnostic reports.
    """

    def __init__(
        self,
        repository: Optional[AssessmentRepository] = None,
        curriculum_service: Optional[CurriculumService] = None,
        learner_service: Optional[LearnerService] = None,
        mastery_service: Optional[MasteryService] = None,
    ):
        self.repository = repository or AssessmentRepository()
        self.curriculum_service = curriculum_service or CurriculumService()
        self.learner_service = learner_service or LearnerService()
        self.mastery_service = mastery_service or MasteryService(repository=self.learner_service.repository)

    def create_diagnostic_test(self, learner_id: str, level_code: str = "A1") -> AssessmentSession:
        """
        Creates a Diagnostic Assessment session with questions spanning all 5 dimensions.
        """
        grammar_items = self.curriculum_service.list_grammar_by_level(level_code)
        vocab_items = self.curriculum_service.list_vocabulary_by_level(level_code)

        questions: List[AssessmentQuestion] = []
        q_idx = 1

        # 1. Grammar Dimension
        for g_item in grammar_items[:3]:
            questions.append(
                AssessmentQuestion(
                    question_id=f"q_diag_{level_code}_g_{q_idx}",
                    assessment_type=AssessmentType.diagnostic,
                    level_code=level_code,
                    prompt=f"[Diagnostic - Grammar] Complete the sentence for target: {g_item.label or g_item.grammar_code}",
                    options=["Option A", "Option B", "Option C", "Option D"],
                    correct_answer="Option A",
                    grammar_target_id=g_item.source_item_id,
                    dimension=DiagnosticDimension.grammar,
                )
            )
            q_idx += 1

        # 2. Vocab Recognition Dimension
        for v_item in vocab_items[:2]:
            questions.append(
                AssessmentQuestion(
                    question_id=f"q_diag_{level_code}_rec_{q_idx}",
                    assessment_type=AssessmentType.diagnostic,
                    level_code=level_code,
                    prompt=f"[Diagnostic - Recognition] Recognize lexeme: '{v_item.lexeme}'",
                    options=["Option A", "Option B", "Option C", "Option D"],
                    correct_answer="Option A",
                    vocabulary_target_id=v_item.source_item_id,
                    dimension=DiagnosticDimension.vocab_recognition,
                )
            )
            q_idx += 1

        # 3. Vocab Recall Dimension
        for v_item in vocab_items[2:4]:
            questions.append(
                AssessmentQuestion(
                    question_id=f"q_diag_{level_code}_rec_{q_idx}",
                    assessment_type=AssessmentType.diagnostic,
                    level_code=level_code,
                    prompt=f"[Diagnostic - Recall] Recall lexeme for definition: '{v_item.raw_text or v_item.lexeme}'",
                    options=["Option A", "Option B", "Option C", "Option D"],
                    correct_answer="Option A",
                    vocabulary_target_id=v_item.source_item_id,
                    dimension=DiagnosticDimension.vocab_recall,
                )
            )
            q_idx += 1

        # 4. Vocab Usage Dimension
        for v_item in vocab_items[4:6]:
            questions.append(
                AssessmentQuestion(
                    question_id=f"q_diag_{level_code}_use_{q_idx}",
                    assessment_type=AssessmentType.diagnostic,
                    level_code=level_code,
                    prompt=f"[Diagnostic - Usage] In context usage for: '{v_item.lexeme}'",
                    options=["Option A", "Option B", "Option C", "Option D"],
                    correct_answer="Option A",
                    vocabulary_target_id=v_item.source_item_id,
                    dimension=DiagnosticDimension.vocab_usage,
                )
            )
            q_idx += 1

        # 5. Vocab Sense Dimension
        for v_item in [v for v in vocab_items if v.guideword][:2]:
            questions.append(
                AssessmentQuestion(
                    question_id=f"q_diag_{level_code}_sns_{q_idx}",
                    assessment_type=AssessmentType.diagnostic,
                    level_code=level_code,
                    prompt=f"[Diagnostic - Sense ({v_item.guideword})] Meaning for: '{v_item.lexeme}'",
                    options=["Option A", "Option B", "Option C", "Option D"],
                    correct_answer="Option A",
                    vocabulary_target_id=v_item.source_item_id,
                    vocabulary_sense_id=f"{v_item.source_item_id}:sense",
                    dimension=DiagnosticDimension.vocab_sense,
                )
            )
            q_idx += 1

        now = datetime.now(timezone.utc)
        session = AssessmentSession(
            session_id=f"sess_diag:{learner_id}:{level_code}:{int(now.timestamp())}",
            learner_id=learner_id,
            assessment_type=AssessmentType.diagnostic,
            target_level=level_code,
            questions=questions,
            is_completed=False,
            created_at=now,
        )

        self.repository.save_session(session)
        return session

    def evaluate_diagnostic_test(
        self, session_id: str, submissions: List[AssessmentSubmission]
    ) -> DiagnosticReport:
        """
        Evaluates diagnostic assessment submissions server-side and produces 5-dimension report.
        """
        session = self.repository.get_session(session_id)
        if not session:
            raise KeyError(f"Diagnostic session '{session_id}' not found.")

        if session.is_completed:
            existing = self.repository.get_diagnostic_reports(session.learner_id)
            if existing:
                return existing[-1]

        sub_dict = {sub.question_id: sub.learner_answer for sub in submissions}
        session.submissions = sub_dict
        session.is_completed = True
        session.completed_at = datetime.now(timezone.utc)
        self.repository.save_session(session)

        # Track dimension counts
        dim_totals: Dict[DiagnosticDimension, int] = {d: 0 for d in DiagnosticDimension}
        dim_correct: Dict[DiagnosticDimension, int] = {d: 0 for d in DiagnosticDimension}

        for q in session.questions:
            dim_totals[q.dimension] += 1
            ans = sub_dict.get(q.question_id, "").strip()
            if ans.lower() == q.correct_answer.lower():
                dim_correct[q.dimension] += 1

        def calc_score(dim: DiagnosticDimension) -> float:
            tot = dim_totals[dim]
            corr = dim_correct[dim]
            return round(corr / tot, 2) if tot > 0 else 1.0

        grammar_score = calc_score(DiagnosticDimension.grammar)
        rec_score = calc_score(DiagnosticDimension.vocab_recognition)
        rec_call_score = calc_score(DiagnosticDimension.vocab_recall)
        usage_score = calc_score(DiagnosticDimension.vocab_usage)
        sense_score = calc_score(DiagnosticDimension.vocab_sense)

        strengths: List[str] = []
        weaknesses: List[str] = []

        dim_scores = {
            "Grammar Structure": grammar_score,
            "Vocabulary Recognition": rec_score,
            "Vocabulary Recall": rec_call_score,
            "Vocabulary Context Usage": usage_score,
            "Vocabulary Sense Precision": sense_score,
        }

        for label, sc in dim_scores.items():
            if sc >= 0.8:
                strengths.append(label)
            elif sc < 0.6:
                weaknesses.append(label)

        report = DiagnosticReport(
            assessment_id=f"diag_rep:{session.learner_id}:{int(datetime.now(timezone.utc).timestamp())}",
            learner_id=session.learner_id,
            grammar_score=grammar_score,
            vocab_recognition_score=rec_score,
            vocab_recall_score=rec_call_score,
            vocab_usage_score=usage_score,
            vocab_sense_score=sense_score,
            strengths=strengths,
            weaknesses=weaknesses,
        )

        self.repository.save_diagnostic_report(report)
        return report
