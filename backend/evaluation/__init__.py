# backend/evaluation/__init__.py
"""
Backend Evaluation Domain Package
──────────────────────────────────
Exports answer evaluation models, evaluator, and orchestration service:
- EvaluationResult
- AnswerEvaluator
- EvaluationService
"""

from .answer_evaluator import AnswerEvaluator
from .evaluation_models import EvaluationResult
from .evaluation_service import EvaluationService

__all__ = [
    "EvaluationResult",
    "AnswerEvaluator",
    "EvaluationService",
]
