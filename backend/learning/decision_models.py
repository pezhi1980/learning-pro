# backend/learning/decision_models.py
"""
ROLE: LEARNING DECISION MODELS

Defines structured models for learning decisions made by the Learning Decision Engine.
Decisions specify exactly what authorized curriculum targets the learner should study next.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field
from backend.schemas.agent_input import GenerationMode


class DecisionType(str, Enum):
    new_learning = "new_learning"
    grammar_repair = "grammar_repair"
    vocabulary_repair = "vocabulary_repair"
    smart_review = "smart_review"
    mixed_practice = "mixed_practice"
    continue_course = "continue_course"


class LearningDecision(BaseModel):
    """
    Structured output of the Learning Decision Engine specifying authorized targets for the next learning session.
    """
    decision_id: str
    learner_id: str
    decision_type: DecisionType
    generation_mode: GenerationMode
    target_language: str = "en"
    native_language: Optional[str] = "fa"

    # Selected authorized targets
    selected_target_grammar_ids: List[str] = Field(default_factory=list)
    selected_target_vocabulary_ids: List[str] = Field(default_factory=list)
    selected_target_vocabulary_sense_ids: List[str] = Field(default_factory=list)

    # Selected allowed supporting content (preferably learner-known)
    selected_allowed_grammar_ids: List[str] = Field(default_factory=list)
    selected_allowed_vocabulary_ids: List[str] = Field(default_factory=list)
    selected_allowed_vocabulary_sense_ids: List[str] = Field(default_factory=list)

    reason_codes: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
