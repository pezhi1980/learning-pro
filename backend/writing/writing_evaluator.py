# backend/writing/writing_evaluator.py
"""
ROLE: UNIFIED WRITING EVALUATOR

Evaluates writing tasks across 3 modes:
1. deterministic
2. advanced_evaluation_required
3. ai_assisted
Enforces strict safeguards: AI evaluator must NEVER authorize curriculum, change source targets,
directly update learner mastery, or invent tested targets.
"""

import logging
from typing import Optional
from backend.writing.feedback_service import WritingFeedbackService
from backend.writing.free_production_evaluator import FreeProductionEvaluator
from backend.writing.writing_models import (
    EvaluationMode,
    StructuredFeedback,
    WritingEvaluationResult,
    WritingSubmission,
)

logger = logging.getLogger(__name__)


class WritingEvaluator:
    """
    Unified evaluator routing submissions based on EvaluationMode while enforcing curriculum safety rules.
    """

    def __init__(
        self,
        free_evaluator: Optional[FreeProductionEvaluator] = None,
        feedback_service: Optional[WritingFeedbackService] = None,
    ):
        self.free_evaluator = free_evaluator or FreeProductionEvaluator()
        self.feedback_service = feedback_service or WritingFeedbackService()

    def evaluate_submission(self, submission: WritingSubmission) -> WritingEvaluationResult:
        """
        Evaluates a writing submission using the specified EvaluationMode.
        """
        mode = submission.evaluation_mode

        if mode == EvaluationMode.deterministic:
            score, details = self._evaluate_deterministic(submission)
        elif mode == EvaluationMode.ai_assisted:
            score, details = self._evaluate_ai_assisted(submission)
        else:
            score, details = self.free_evaluator.evaluate_free_production(submission)

        is_correct = score >= 0.70

        # Generate 5-dimension structured feedback
        feedback = self.feedback_service.generate_feedback(submission, score, details)

        eval_id = f"eval_w_{submission.submission_id}"

        return WritingEvaluationResult(
            evaluation_id=eval_id,
            submission_id=submission.submission_id,
            learner_id=submission.learner_id,
            evaluation_mode=mode,
            is_correct=is_correct,
            overall_score=score,
            feedback=feedback,
            hints_used_count=len(submission.hints_used),
            answer_revealed=any(h.value == "answer_reveal" for h in submission.hints_used),
        )

    def _evaluate_deterministic(self, submission: WritingSubmission) -> tuple[float, dict]:
        """
        Evaluates closed/deterministic writing task (e.g. fill in blank or exact phrase).
        """
        text = submission.learner_text.strip().lower()
        if not text:
            return 0.0, {"reason": "Empty string"}

        # Match against target vocabulary items as exact required tokens
        target_tokens = [v.lower().strip() for v in submission.target_vocabulary_items]
        matches = sum(1 for tok in target_tokens if tok in text)

        score = (matches / len(target_tokens)) if target_tokens else (1.0 if len(text) > 2 else 0.0)
        return round(score, 2), {"total_words": len(text.split()), "min_words_required": 1, "vocab_matches": target_tokens}

    def _evaluate_ai_assisted(self, submission: WritingSubmission) -> tuple[float, dict]:
        """
        Mocked AI-assisted evaluation path (No live paid calls in tests).
        Enforces AI evaluator safeguards: does not mutate mastery or invent curriculum.
        """
        # Delegated to free_production_evaluator with simulated AI metadata
        score, details = self.free_evaluator.evaluate_free_production(submission)
        details["ai_evaluated"] = True
        return score, details
