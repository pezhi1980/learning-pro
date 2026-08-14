# backend/writing/writing_service.py
"""
ROLE: WRITING SERVICE

Orchestrates:
- 5 Writing Practice Task Types
- Free Production Evaluation & 3 Evaluation Modes
- 5-Dimension Structured Feedback System & Repair Connections
- Progressive Hint System (hint_1..3, answer_reveal)
- Evaluation result persistence and learner history lookup
"""

import logging
from typing import Dict, List, Optional

from backend.writing.free_production_evaluator import FreeProductionEvaluator
from backend.writing.hint_service import ProgressiveHintService
from backend.writing.writing_evaluator import WritingEvaluator
from backend.writing.writing_models import (
    HintRequest,
    HintResponse,
    WritingEvaluationResult,
    WritingSubmission,
)

logger = logging.getLogger(__name__)


class WritingService:
    """
    Core Writing & Free Production service managing task evaluation, feedback generation, and progressive hints.
    """

    def __init__(
        self,
        evaluator: Optional[WritingEvaluator] = None,
        hint_service: Optional[ProgressiveHintService] = None,
    ):
        self.evaluator = evaluator or WritingEvaluator()
        self.hint_service = hint_service or ProgressiveHintService()
        self._evaluations: Dict[str, List[WritingEvaluationResult]] = {}

    def evaluate_writing(self, submission: WritingSubmission) -> WritingEvaluationResult:
        """
        Evaluates a writing submission, generates structured feedback, and persists the evaluation result.
        """
        result = self.evaluator.evaluate_submission(submission)

        if submission.learner_id not in self._evaluations:
            self._evaluations[submission.learner_id] = []
        self._evaluations[submission.learner_id].append(result)

        return result

    def request_progressive_hint(self, request: HintRequest) -> HintResponse:
        """
        Requests a progressive hint or model answer reveal for a writing task.
        """
        return self.hint_service.get_progressive_hint(request)

    def get_learner_writing_history(self, learner_id: str) -> List[WritingEvaluationResult]:
        """
        Returns evaluation history for a specific learner.
        """
        return self._evaluations.get(learner_id, [])
