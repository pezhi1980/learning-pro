# backend/assessment/assessment_models.py
"""
ROLE: ASSESSMENT DATA MODELS

Defines structured data models for:
- Placement Test sessions & recommended starting positions
- Diagnostic Assessment across 5 separate evidence dimensions (Grammar, Vocab Recognition, Recall, Usage, Sense)
- Topic, Unit, and Cumulative Checkpoints
- Level Assessments (A1-C2) with readiness recommendations (No official CEFR certification claims)
- Server-side authoritative assessment state & submission models
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class AssessmentType(str, Enum):
    placement = "placement"
    diagnostic = "diagnostic"
    checkpoint_topic = "checkpoint_topic"
    checkpoint_unit = "checkpoint_unit"
    checkpoint_cumulative = "checkpoint_cumulative"
    level_assessment = "level_assessment"


class DiagnosticDimension(str, Enum):
    grammar = "grammar"
    vocab_recognition = "vocab_recognition"
    vocab_recall = "vocab_recall"
    vocab_usage = "vocab_usage"
    vocab_sense = "vocab_sense"


class ReadinessRecommendation(str, Enum):
    ready_to_advance = "ready_to_advance"
    needs_repair = "needs_repair"
    needs_review = "needs_review"


class AssessmentQuestion(BaseModel):
    question_id: str
    assessment_type: AssessmentType
    level_code: str  # A1, A2, B1, B2, C1, C2
    prompt: str
    options: List[str] = Field(default_factory=list)
    correct_answer: str
    grammar_target_id: Optional[str] = None
    vocabulary_target_id: Optional[str] = None
    vocabulary_sense_id: Optional[str] = None
    dimension: DiagnosticDimension = DiagnosticDimension.grammar


class AssessmentSubmission(BaseModel):
    question_id: str
    learner_answer: str


class AssessmentSession(BaseModel):
    session_id: str
    learner_id: str
    assessment_type: AssessmentType
    target_level: Optional[str] = None  # A1, A2, B1, B2, C1, C2
    target_id: Optional[str] = None  # topic_id, unit_id, etc.
    questions: List[AssessmentQuestion] = Field(default_factory=list)
    submissions: Dict[str, str] = Field(default_factory=dict)  # question_id -> learner_answer
    is_completed: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class PlacementResult(BaseModel):
    assessment_id: str
    learner_id: str
    level_scores: Dict[str, float] = Field(default_factory=dict)
    confidence_score: float
    recommended_starting_level: str
    recommended_starting_unit_id: Optional[str] = None
    recommended_starting_micro_lesson_id: Optional[str] = None
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DiagnosticReport(BaseModel):
    assessment_id: str
    learner_id: str
    grammar_score: float
    vocab_recognition_score: float
    vocab_recall_score: float
    vocab_usage_score: float
    vocab_sense_score: float
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CheckpointResult(BaseModel):
    assessment_id: str
    learner_id: str
    checkpoint_type: AssessmentType
    target_id: str
    score: float
    passed: bool
    tested_targets: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LevelAssessmentReport(BaseModel):
    assessment_id: str
    learner_id: str
    level_code: str
    score: float
    coverage_percentage: float
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    readiness_recommendation: ReadinessRecommendation
    disclaimer: str = (
        "This assessment is for internal placement and progress tracking within Learning Lang Pro "
        "and does not constitute an official CEFR language certification."
    )
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
