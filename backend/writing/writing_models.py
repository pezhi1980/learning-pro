# backend/writing/writing_models.py
"""
ROLE: WRITING, FREE PRODUCTION, FEEDBACK & HINT DATA MODELS

Defines structured data models for:
- 5 Writing Practice Task Types (sentence_construction, short_answer, controlled_production, paragraph, extended_writing)
- 3 Evaluation Modes (deterministic, advanced_evaluation_required, ai_assisted)
- 4 Progressive Hint Levels (hint_1, hint_2, hint_3, answer_reveal)
- Structured 5-Dimension Feedback (target_grammar, target_vocabulary, task_completion, clarity, organization)
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class WritingTaskType(str, Enum):
    sentence_construction = "sentence_construction"
    short_answer = "short_answer"
    controlled_production = "controlled_production"
    paragraph = "paragraph"
    extended_writing = "extended_writing"


class EvaluationMode(str, Enum):
    deterministic = "deterministic"
    advanced_evaluation_required = "advanced_evaluation_required"
    ai_assisted = "ai_assisted"


class HintLevel(str, Enum):
    hint_1 = "hint_1"
    hint_2 = "hint_2"
    hint_3 = "hint_3"
    answer_reveal = "answer_reveal"


class WritingSubmission(BaseModel):
    submission_id: str
    learner_id: str
    task_type: WritingTaskType
    prompt: str
    learner_text: str
    target_grammar_codes: List[str] = Field(default_factory=list)
    target_vocabulary_items: List[str] = Field(default_factory=list)
    target_vocabulary_sense_ids: List[str] = Field(default_factory=list)
    evaluation_mode: EvaluationMode = EvaluationMode.advanced_evaluation_required
    hints_used: List[HintLevel] = Field(default_factory=list)


class StructuredFeedback(BaseModel):
    target_grammar_feedback: Optional[str] = None
    target_vocabulary_feedback: Optional[str] = None
    task_completion_feedback: str
    clarity_feedback: str
    organization_feedback: Optional[str] = None
    repair_target_ids: List[str] = Field(default_factory=list)
    vocabulary_sense_clarification: Optional[str] = None


class WritingEvaluationResult(BaseModel):
    evaluation_id: str
    submission_id: str
    learner_id: str
    evaluation_mode: EvaluationMode
    is_correct: bool
    overall_score: float
    feedback: StructuredFeedback
    hints_used_count: int = 0
    answer_revealed: bool = False
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HintRequest(BaseModel):
    learner_id: str
    task_id: str
    prompt: str
    target_grammar_codes: List[str] = Field(default_factory=list)
    target_vocabulary_items: List[str] = Field(default_factory=list)
    requested_level: HintLevel


class HintResponse(BaseModel):
    task_id: str
    hint_level: HintLevel
    hint_text: str
    answer_revealed: bool = False
