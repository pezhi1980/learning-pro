# backend/analytics/analytics_models.py
"""
ROLE: ANALYTICS & CONTENT QUALITY DATA MODELS

Defines structured Pydantic models for:
- 8 Analytics Event Types (lesson_started, lesson_completed, exercise_answered, hint_used, review_completed, repair_completed, session_abandoned, assessment_completed)
- Learner Content Issue Reports across 6 categories (wrong_answer, unclear_explanation, unnatural_example, audio_problem, typo, technical_problem)
- Content Quality Signal records for automated suspicious content detection
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AnalyticsEventType(str, Enum):
    lesson_started = "lesson_started"
    lesson_completed = "lesson_completed"
    exercise_answered = "exercise_answered"
    hint_used = "hint_used"
    review_completed = "review_completed"
    repair_completed = "repair_completed"
    session_abandoned = "session_abandoned"
    assessment_completed = "assessment_completed"


class ReportType(str, Enum):
    wrong_answer = "wrong_answer"
    unclear_explanation = "unclear_explanation"
    unnatural_example = "unnatural_example"
    audio_problem = "audio_problem"
    typo = "typo"
    technical_problem = "technical_problem"


class AnalyticsEventRecord(BaseModel):
    event_id: str
    event_type: AnalyticsEventType
    learner_id: str
    target_id: Optional[str] = None
    lesson_id: Optional[str] = None
    exercise_id: Optional[str] = None
    payload: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class UserReportRecord(BaseModel):
    report_id: str
    learner_id: str
    report_type: ReportType
    description: str
    lesson_id: Optional[str] = None
    exercise_id: Optional[str] = None
    content_version: Optional[str] = None
    source_trace: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ContentQualitySignalRecord(BaseModel):
    content_id: str
    failure_rate: float = 0.0
    abandonment_rate: float = 0.0
    report_count: int = 0
    regeneration_count: int = 0
    suspicious_flags: List[str] = Field(default_factory=list)
    is_suspicious: bool = False
