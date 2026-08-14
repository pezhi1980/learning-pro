# backend/writing/__init__.py
"""
ROLE: WRITING, FREE PRODUCTION, FEEDBACK & HINTS PACKAGE

Provides complete Writing System infrastructure:
- 5 Writing Practice Task Types (sentence_construction, short_answer, controlled_production, paragraph, extended_writing)
- Free Production Evaluation Engine (semantic non-exact matching)
- 3 Evaluation Modes (deterministic, advanced_evaluation_required, ai_assisted)
- 5-Dimension Structured Feedback System & Repair Connections
- Progressive Hint System (hint_1, hint_2, hint_3, answer_reveal)
"""

from .writing_models import (
    WritingTaskType,
    EvaluationMode,
    HintLevel,
    WritingSubmission,
    StructuredFeedback,
    WritingEvaluationResult,
    HintRequest,
    HintResponse,
)
from .free_production_evaluator import FreeProductionEvaluator
from .feedback_service import WritingFeedbackService
from .hint_service import ProgressiveHintService
from .writing_evaluator import WritingEvaluator
from .writing_service import WritingService

__all__ = [
    "WritingTaskType",
    "EvaluationMode",
    "HintLevel",
    "WritingSubmission",
    "StructuredFeedback",
    "WritingEvaluationResult",
    "HintRequest",
    "HintResponse",
    "FreeProductionEvaluator",
    "WritingFeedbackService",
    "ProgressiveHintService",
    "WritingEvaluator",
    "WritingService",
]
