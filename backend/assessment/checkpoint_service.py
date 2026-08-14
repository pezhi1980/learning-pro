# backend/assessment/checkpoint_service.py
"""
ROLE: CHECKPOINT ASSESSMENT SERVICE

Constructs and evaluates:
- Topic Checkpoints
- Unit Checkpoints
- Cumulative Checkpoints
Questions trace directly to tested authorized PDF targets. Server-side assessment state is authoritative.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from backend.assessment.assessment_models import (
    AssessmentQuestion,
    AssessmentSession,
    AssessmentSubmission,
    AssessmentType,
    CheckpointResult,
    DiagnosticDimension,
)
from backend.assessment.assessment_repository import AssessmentRepository
from backend.course import CourseService


class CheckpointService:
    """
    Manages Topic, Unit, and Cumulative Checkpoint Assessments.
    """

    def __init__(
        self,
        repository: Optional[AssessmentRepository] = None,
        course_service: Optional[CourseService] = None,
    ):
        self.repository = repository or AssessmentRepository()
        self.course_service = course_service or CourseService()

    def create_topic_checkpoint(self, learner_id: str, topic_id: str) -> AssessmentSession:
        """
        Creates a Checkpoint Assessment session for a specific Course Topic.
        """
        parts = topic_id.split(":")
        level_code = parts[1] if len(parts) >= 2 else "A1"
        level_obj = self.course_service.get_level(level_code)

        questions: List[AssessmentQuestion] = []
        q_counter = 1
        tested_target_ids: List[str] = []

        if level_obj:
            for unit in level_obj.units:
                for topic in unit.topics:
                    if topic.topic_id == topic_id:
                        for ml in topic.micro_lessons:
                            for g_id in ml.grammar_target_ids:
                                questions.append(
                                    AssessmentQuestion(
                                        question_id=f"q_chk_top_{topic_id}_g_{q_counter}",
                                        assessment_type=AssessmentType.checkpoint_topic,
                                        level_code=level_code,
                                        prompt=f"[Topic Checkpoint] Question for Grammar: {g_id}",
                                        options=["Option A", "Option B", "Option C", "Option D"],
                                        correct_answer="Option A",
                                        grammar_target_id=g_id,
                                        dimension=DiagnosticDimension.grammar,
                                    )
                                )
                                tested_target_ids.append(g_id)
                                q_counter += 1

        now = datetime.now(timezone.utc)
        session = AssessmentSession(
            session_id=f"sess_chk_top:{learner_id}:{topic_id}:{int(now.timestamp())}",
            learner_id=learner_id,
            assessment_type=AssessmentType.checkpoint_topic,
            target_level=level_code,
            target_id=topic_id,
            questions=questions,
            is_completed=False,
            created_at=now,
        )
        self.repository.save_session(session)
        return session

    def create_unit_checkpoint(self, learner_id: str, unit_id: str) -> AssessmentSession:
        """
        Creates a Checkpoint Assessment session for a full Course Unit.
        """
        parts = unit_id.split(":")
        level_code = parts[1] if len(parts) >= 2 else "A1"
        level_obj = self.course_service.get_level(level_code)

        questions: List[AssessmentQuestion] = []
        q_counter = 1

        if level_obj:
            for unit in level_obj.units:
                if unit.unit_id == unit_id:
                    for topic in unit.topics:
                        for ml in topic.micro_lessons:
                            for g_id in ml.grammar_target_ids[:1]:
                                questions.append(
                                    AssessmentQuestion(
                                        question_id=f"q_chk_u_{unit_id}_g_{q_counter}",
                                        assessment_type=AssessmentType.checkpoint_unit,
                                        level_code=level_code,
                                        prompt=f"[Unit Checkpoint] Checkpoint question for Grammar: {g_id}",
                                        options=["Option A", "Option B", "Option C", "Option D"],
                                        correct_answer="Option A",
                                        grammar_target_id=g_id,
                                        dimension=DiagnosticDimension.grammar,
                                    )
                                )
                                q_counter += 1

        now = datetime.now(timezone.utc)
        session = AssessmentSession(
            session_id=f"sess_chk_u:{learner_id}:{unit_id}:{int(now.timestamp())}",
            learner_id=learner_id,
            assessment_type=AssessmentType.checkpoint_unit,
            target_level=level_code,
            target_id=unit_id,
            questions=questions,
            is_completed=False,
            created_at=now,
        )
        self.repository.save_session(session)
        return session

    def create_cumulative_checkpoint(self, learner_id: str, level_code: str) -> AssessmentSession:
        """
        Creates a Cumulative Checkpoint Assessment session across a CEFR level.
        """
        all_nodes = self.course_service.repository.get_all_micro_lessons_in_level(level_code)
        questions: List[AssessmentQuestion] = []
        q_counter = 1

        for ml in all_nodes[:10]:
            for g_id in ml.grammar_target_ids:
                questions.append(
                    AssessmentQuestion(
                        question_id=f"q_chk_cum_{level_code}_g_{q_counter}",
                        assessment_type=AssessmentType.checkpoint_cumulative,
                        level_code=level_code,
                        prompt=f"[Cumulative Checkpoint] Question for Grammar target: {g_id}",
                        options=["Option A", "Option B", "Option C", "Option D"],
                        correct_answer="Option A",
                        grammar_target_id=g_id,
                        dimension=DiagnosticDimension.grammar,
                    )
                )
                q_counter += 1

        now = datetime.now(timezone.utc)
        session = AssessmentSession(
            session_id=f"sess_chk_cum:{learner_id}:{level_code}:{int(now.timestamp())}",
            learner_id=learner_id,
            assessment_type=AssessmentType.checkpoint_cumulative,
            target_level=level_code,
            target_id=f"cumulative:{level_code}",
            questions=questions,
            is_completed=False,
            created_at=now,
        )
        self.repository.save_session(session)
        return session

    def evaluate_checkpoint(
        self, session_id: str, submissions: List[AssessmentSubmission]
    ) -> CheckpointResult:
        """
        Evaluates a checkpoint test server-side and produces a CheckpointResult.
        """
        session = self.repository.get_session(session_id)
        if not session:
            raise KeyError(f"Checkpoint session '{session_id}' not found.")

        if session.is_completed:
            existing = self.repository.get_checkpoint_results(session.learner_id)
            if existing:
                return existing[-1]

        sub_dict = {sub.question_id: sub.learner_answer for sub in submissions}
        session.submissions = sub_dict
        session.is_completed = True
        session.completed_at = datetime.now(timezone.utc)
        self.repository.save_session(session)

        correct_count = 0
        tested_targets: List[str] = []

        for q in session.questions:
            if q.grammar_target_id:
                tested_targets.append(q.grammar_target_id)
            elif q.vocabulary_target_id:
                tested_targets.append(q.vocabulary_target_id)

            ans = sub_dict.get(q.question_id, "").strip()
            if ans.lower() == q.correct_answer.lower():
                correct_count += 1

        total_questions = len(session.questions)
        score = round(correct_count / total_questions, 2) if total_questions > 0 else 0.0
        passed = score >= 0.75

        result = CheckpointResult(
            assessment_id=f"chk_res:{session.learner_id}:{int(datetime.now(timezone.utc).timestamp())}",
            learner_id=session.learner_id,
            checkpoint_type=session.assessment_type,
            target_id=session.target_id or "checkpoint",
            score=score,
            passed=passed,
            tested_targets=tested_targets,
        )

        self.repository.save_checkpoint_result(result)
        return result
