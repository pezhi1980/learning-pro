# backend/learner/knowledge_models.py
"""
ROLE: LEARNER KNOWLEDGE MODEL

Defines learner domain state models for tracking what a specific learner currently knows.
Preserves strict independence between Grammar progress and Vocabulary progress,
and between different Senses of the same Vocabulary lexeme.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class LearningStatus(str, Enum):
    unseen = "unseen"
    introduced = "introduced"
    learning = "learning"
    strengthening = "strengthening"
    mastered = "mastered"
    review_due = "review_due"


class GrammarKnowledgeState(BaseModel):
    """
    Tracks a learner's knowledge state for a single authorized Grammar target.
    """
    learner_id: str
    learning_object_id: str
    grammar_code: str
    source_item_id: str

    # Mastery dimensions (0.0 to 1.0)
    understanding: float = Field(default=0.0, ge=0.0, le=1.0)
    controlled_use: float = Field(default=0.0, ge=0.0, le=1.0)
    production: float = Field(default=0.0, ge=0.0, le=1.0)
    stability: float = Field(default=0.0, ge=0.0, le=1.0)

    # Operational metadata
    attempt_count: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    consecutive_correct: int = 0
    consecutive_incorrect: int = 0
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    last_correct_at: Optional[datetime] = None
    last_incorrect_at: Optional[datetime] = None
    last_practiced_at: Optional[datetime] = None
    mastery_updated_at: Optional[datetime] = None
    review_due_at: Optional[datetime] = None

    @field_validator("understanding", "controlled_use", "production", "stability")
    @classmethod
    def validate_mastery_range(cls, v: float) -> float:
        if v < 0.0 or v > 1.0:
            raise ValueError("Mastery dimension value must be between 0.0 and 1.0 inclusive")
        return v

    @property
    def overall_mastery(self) -> float:
        return round((self.understanding * 0.3 + self.controlled_use * 0.4 + self.production * 0.3), 4)

    @property
    def status(self) -> LearningStatus:
        if self.attempt_count == 0:
            return LearningStatus.unseen
        now = datetime.now(timezone.utc)
        if self.review_due_at and self.review_due_at <= now:
            return LearningStatus.review_due
        m = self.overall_mastery
        if m >= 0.85 and self.stability >= 0.7:
            return LearningStatus.mastered
        elif m >= 0.6:
            return LearningStatus.strengthening
        elif m >= 0.2:
            return LearningStatus.learning
        return LearningStatus.introduced


class VocabularyKnowledgeState(BaseModel):
    """
    Tracks a learner's knowledge state for a single authorized Vocabulary target or Sense.
    """
    learner_id: str
    learning_object_id: str
    vocabulary_source_item_id: str
    lexeme: str
    vocabulary_sense_id: Optional[str] = None
    guideword: Optional[str] = None

    # Mastery dimensions (0.0 to 1.0)
    recognition: float = Field(default=0.0, ge=0.0, le=1.0)
    recall: float = Field(default=0.0, ge=0.0, le=1.0)
    usage: float = Field(default=0.0, ge=0.0, le=1.0)
    stability: float = Field(default=0.0, ge=0.0, le=1.0)

    # Operational metadata
    attempt_count: int = 0
    correct_count: int = 0
    incorrect_count: int = 0
    consecutive_correct: int = 0
    consecutive_incorrect: int = 0
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    last_correct_at: Optional[datetime] = None
    last_incorrect_at: Optional[datetime] = None
    last_practiced_at: Optional[datetime] = None
    mastery_updated_at: Optional[datetime] = None
    review_due_at: Optional[datetime] = None

    @field_validator("recognition", "recall", "usage", "stability")
    @classmethod
    def validate_mastery_range(cls, v: float) -> float:
        if v < 0.0 or v > 1.0:
            raise ValueError("Mastery dimension value must be between 0.0 and 1.0 inclusive")
        return v

    @property
    def overall_mastery(self) -> float:
        return round((self.recognition * 0.3 + self.recall * 0.4 + self.usage * 0.3), 4)

    @property
    def status(self) -> LearningStatus:
        if self.attempt_count == 0:
            return LearningStatus.unseen
        now = datetime.now(timezone.utc)
        if self.review_due_at and self.review_due_at <= now:
            return LearningStatus.review_due
        m = self.overall_mastery
        if m >= 0.85 and self.stability >= 0.7:
            return LearningStatus.mastered
        elif m >= 0.6:
            return LearningStatus.strengthening
        elif m >= 0.2:
            return LearningStatus.learning
        return LearningStatus.introduced


class LearnerErrorPattern(BaseModel):
    """
    Tracks recurring error patterns for a learner.
    """
    error_id: str
    learner_id: str
    error_code: str
    category: str  # e.g., 'grammar', 'vocabulary', 'sense_confusion', 'spelling'
    target_learning_object_id: str
    grammar_code: Optional[str] = None
    vocabulary_source_item_id: Optional[str] = None
    vocabulary_sense_id: Optional[str] = None
    occurrence_count: int = 1
    first_seen_at: datetime
    last_seen_at: datetime
    last_context: Optional[str] = None
    active: bool = True
    severity_score: float = Field(default=0.5, ge=0.0, le=1.0)
