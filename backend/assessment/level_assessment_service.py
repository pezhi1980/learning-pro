# backend/assessment/level_assessment_service.py
"""
ROLE: LEVEL ASSESSMENT SERVICE

Evaluates comprehensive level mastery for CEFR levels (A1, A2, B1, B2, C1, C2).
Produces:
- score
- coverage percentage
- strengths & weaknesses
- readiness recommendation (ready_to_advance, needs_repair, needs_review)
Does NOT label the result official CEFR certification claims.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from backend.assessment.assessment_models import (
    AssessmentQuestion,
    AssessmentSession,
    AssessmentSubmission,
    AssessmentType,
    DiagnosticDimension,
    LevelAssessmentReport,
    ReadinessRecommendation,
)
from backend.assessment.assessment_repository import AssessmentRepository
from backend.course import CourseRepository, CourseService
from backend.curriculum import CurriculumService


class LevelAssessmentService:
    """
    Orchestrates Level Assessments for A1-C2 levels.
    """

    def __init__(
        self,
        repository: Optional[AssessmentRepository] = None,
        curriculum_service: Optional[CurriculumService] = None,
        course_service: Optional[CourseService] = None,
    ):
        self.repository = repository or AssessmentRepository()
        self.curriculum_service = curriculum_service or CurriculumService()
        self.course_service = course_service or CourseService(
            repository=CourseRepository(curriculum_service=self.curriculum_service)
        )


    def create_level_assessment(self, learner_id: str, level_code: str) -> AssessmentSession:
        """
        Creates a Level Assessment session querying authorized PDF curriculum targets for the level.
        """
        grammar_items = self.curriculum_service.list_grammar_by_level(level_code)
        vocab_items = self.curriculum_service.list_vocabulary_by_level(level_code)

        questions: List[AssessmentQuestion] = []
        q_counter = 1

        # Select 5 grammar items
        for g_item in grammar_items[:5]:
            questions.append(
                AssessmentQuestion(
                    question_id=f"q_lvl_{level_code}_g_{q_counter}",
                    assessment_type=AssessmentType.level_assessment,
                    level_code=level_code,
                    prompt=f"[Level Assessment {level_code}] Grammar question for: {g_item.label or g_item.grammar_code}",
                    options=["Option A", "Option B", "Option C", "Option D"],
                    correct_answer="Option A",
                    grammar_target_id=g_item.source_item_id,
                    dimension=DiagnosticDimension.grammar,
                )
            )
            q_counter += 1

        # Select 5 vocabulary items
        for v_item in vocab_items[:5]:
            questions.append(
                AssessmentQuestion(
                    question_id=f"q_lvl_{level_code}_v_{q_counter}",
                    assessment_type=AssessmentType.level_assessment,
                    level_code=level_code,
                    prompt=f"[Level Assessment {level_code}] Vocabulary question for: '{v_item.lexeme}'",
                    options=["Option A", "Option B", "Option C", "Option D"],
                    correct_answer="Option A",
                    vocabulary_target_id=v_item.source_item_id,
                    vocabulary_sense_id=f"{v_item.source_item_id}:sense" if v_item.guideword else None,
                    dimension=DiagnosticDimension.vocab_recognition,
                )
            )
            q_counter += 1

        now = datetime.now(timezone.utc)
        session = AssessmentSession(
            session_id=f"sess_lvl_ass:{learner_id}:{level_code}:{int(now.timestamp())}",
            learner_id=learner_id,
            assessment_type=AssessmentType.level_assessment,
            target_level=level_code,
            questions=questions,
            is_completed=False,
            created_at=now,
        )

        self.repository.save_session(session)
        return session

    def evaluate_level_assessment(
        self, session_id: str, submissions: List[AssessmentSubmission]
    ) -> LevelAssessmentReport:
        """
        Evaluates a level assessment server-side, calculates coverage, strengths, weaknesses, and readiness recommendation.
        """
        session = self.repository.get_session(session_id)
        if not session:
            raise KeyError(f"Level assessment session '{session_id}' not found.")

        if session.is_completed:
            existing = self.repository.get_level_reports(session.learner_id)
            if existing:
                return existing[-1]

        sub_dict = {sub.question_id: sub.learner_answer for sub in submissions}
        session.submissions = sub_dict
        session.is_completed = True
        session.completed_at = datetime.now(timezone.utc)
        self.repository.save_session(session)

        correct_count = 0
        tested_target_set = set()

        for q in session.questions:
            if q.grammar_target_id:
                tested_target_set.add(q.grammar_target_id)
            if q.vocabulary_target_id:
                tested_target_set.add(q.vocabulary_target_id)

            ans = sub_dict.get(q.question_id, "").strip()
            if ans.lower() == q.correct_answer.lower():
                correct_count += 1

        total_questions = len(session.questions)
        score = round(correct_count / total_questions, 2) if total_questions > 0 else 0.0

        # Calculate coverage
        level_code = session.target_level or "A1"
        total_level_grammar = len(self.curriculum_service.list_grammar_by_level(level_code))
        total_level_vocab = len(self.curriculum_service.list_vocabulary_by_level(level_code))
        total_items_in_level = total_level_grammar + total_level_vocab

        coverage_percentage = (
            round((len(tested_target_set) / max(1, total_items_in_level)) * 100, 2)
            if total_items_in_level > 0
            else 100.0
        )

        strengths: List[str] = []
        weaknesses: List[str] = []

        if score >= 0.85:
            readiness = ReadinessRecommendation.ready_to_advance
            strengths.append(f"Strong overall mastery of CEFR {level_code} core structures.")
        elif score >= 0.70:
            readiness = ReadinessRecommendation.needs_review
            strengths.append(f"Satisfactory progress in CEFR {level_code}.")
            weaknesses.append("Targeted review recommended before advancing.")
        else:
            readiness = ReadinessRecommendation.needs_repair
            weaknesses.append(f"Core repair required for foundational CEFR {level_code} items.")

        report = LevelAssessmentReport(
            assessment_id=f"lvl_rep:{session.learner_id}:{level_code}:{int(datetime.now(timezone.utc).timestamp())}",
            learner_id=session.learner_id,
            level_code=level_code,
            score=score,
            coverage_percentage=coverage_percentage,
            strengths=strengths,
            weaknesses=weaknesses,
            readiness_recommendation=readiness,
        )

        self.repository.save_level_report(report)
        return report
