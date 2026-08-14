# backend/evaluation/evaluation_models.py
"""
ROLE: EVALUATION MODELS

Defines structured models representing the evaluation result of a learner exercise submission.
Includes score, correctness, target traceability inherited from the exercise, error classification, and metadata.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class EvaluationResult(BaseModel):
    """
    Canonical output of exercise answer evaluation.
    """
    evaluation_id: str
    learner_id: str
    lesson_id: str
    exercise_id: str
    correct: bool
    score: float = Field(default=0.0, ge=0.0, le=1.0)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Inherited target traceability from ExerciseItem
    tested_grammar_codes: List[str] = Field(default_factory=list)
    tested_vocabulary_items: List[str] = Field(default_factory=list)
    tested_vocabulary_sense_ids: List[str] = Field(default_factory=list)
    target_learning_object_ids: List[str] = Field(default_factory=list)

    evaluation_method: str  # e.g., 'mcq_exact', 'fill_blank_deterministic', 'word_order_exact', 'requires_advanced_evaluation'
    learner_answer: str
    expected_answer: str
    error_codes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
