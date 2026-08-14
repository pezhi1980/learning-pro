# backend/evaluation/evaluation_service.py
"""
ROLE: EVALUATION SERVICE

Orchestrates answer evaluation, learner mastery updates, and error tracking in a closed loop.
Enforces submission idempotency so duplicate requests do not double-increment mastery.
"""

from typing import Optional
from backend.evaluation.answer_evaluator import AnswerEvaluator
from backend.evaluation.evaluation_models import EvaluationResult
from backend.learner.error_tracker import ErrorTracker
from backend.learner.learner_repository import LearnerRepository
from backend.learner.mastery_service import MasteryService
from backend.schemas.agent_output import ExerciseItem
from backend.session.learning_history_service import LearningHistoryService


class EvaluationService:
    """
    Central orchestration service for answer submissions, evaluation, and learner state updates.
    """

    def __init__(
        self,
        repository: Optional[LearnerRepository] = None,
        evaluator: Optional[AnswerEvaluator] = None,
        mastery_service: Optional[MasteryService] = None,
        error_tracker: Optional[ErrorTracker] = None,
        history_service: Optional[LearningHistoryService] = None,
    ):
        self.repository = repository or LearnerRepository()
        self.evaluator = evaluator or AnswerEvaluator()
        self.mastery_service = mastery_service or MasteryService(repository=self.repository)
        self.error_tracker = error_tracker or ErrorTracker(repository=self.repository)
        self.history_service = history_service or LearningHistoryService()


    def submit_answer(
        self,
        learner_id: str,
        lesson_id: str,
        exercise: ExerciseItem,
        learner_answer: str,
        submission_id: Optional[str] = None,
    ) -> EvaluationResult:
        """
        Processes a learner exercise answer submission:
        1. Checks idempotency (duplicate submission protection).
        2. Evaluates answer.
        3. Updates mastery states.
        4. Updates active error patterns.
        5. Returns EvaluationResult.
        """
        # Idempotency check
        if submission_id and self.repository.is_submission_processed(submission_id):
            eval_result = self.evaluator.evaluate_exercise(
                learner_id=learner_id,
                lesson_id=lesson_id,
                exercise=exercise,
                learner_answer=learner_answer,
                submission_id=submission_id,
            )
            eval_result.metadata["idempotent_duplicate"] = True
            return eval_result

        # Step 1: Evaluate
        eval_result = self.evaluator.evaluate_exercise(
            learner_id=learner_id,
            lesson_id=lesson_id,
            exercise=exercise,
            learner_answer=learner_answer,
            submission_id=submission_id,
        )

        # Step 2: Update Mastery & Error State
        self.mastery_service.process_evaluation_result(eval_result)
        self.error_tracker.process_evaluation_errors(eval_result)

        # Step 3: Record Educational Learning History
        ex_id = getattr(exercise, "id", getattr(exercise, "exercise_id", "ex_unknown"))
        self.history_service.record_history_entry(
            learner_id=learner_id,
            record_type="exercise",
            summary=f"Answered exercise '{ex_id}' - {'Correct' if eval_result.correct else 'Incorrect'}",
            details={
                "lesson_id": lesson_id,
                "exercise_id": ex_id,
                "correct": eval_result.correct,
                "score": eval_result.score,
                "submission_id": submission_id,
            },
        )


        # Step 4: Record Submission for Idempotency
        if submission_id:
            self.repository.record_submission(submission_id)

        return eval_result

