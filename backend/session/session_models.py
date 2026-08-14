# backend/session/session_models.py
"""
ROLE: SESSION & LEARNING HISTORY DATA MODELS

Defines structured internal models for:
- Session Builder & Activity Configs
- Daily Learning Sessions & Lifecycle Statuses
- Completion Events (Micro Lesson, Topic, Unit, Level, Session)
- Educational Learner History & Aggregate Statistics
"""

from __future__ import annotations
from datetime import datetime, timezone

from enum import Enum
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class ActivityType(str, Enum):
    new_grammar = "new_grammar"
    new_vocabulary = "new_vocabulary"
    grammar_repair = "grammar_repair"
    vocabulary_repair = "vocabulary_repair"
    smart_review = "smart_review"
    mixed_practice = "mixed_practice"
    assessment = "assessment"


class SessionStatus(str, Enum):
    created = "created"
    in_progress = "in_progress"
    paused = "paused"
    completed = "completed"


class CompletionType(str, Enum):
    micro_lesson = "micro_lesson"
    topic = "topic"
    unit = "unit"
    level = "level"
    session = "session"


class SessionActivity(BaseModel):
    activity_id: str
    activity_type: ActivityType
    title: str
    order: int
    target_grammar_ids: List[str] = Field(default_factory=list)
    target_vocabulary_ids: List[str] = Field(default_factory=list)
    target_vocabulary_sense_ids: List[str] = Field(default_factory=list)
    allowed_grammar_ids: List[str] = Field(default_factory=list)
    allowed_vocabulary_ids: List[str] = Field(default_factory=list)
    is_completed: bool = False
    completed_at: Optional[datetime] = None
    estimated_duration_minutes: int = 5


class DailyLearningSession(BaseModel):
    session_id: str
    learner_id: str
    target_language: str = "en"
    native_language: str = "fa"
    requested_level: str = "A1"
    status: SessionStatus = SessionStatus.created
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    activities: List[SessionActivity] = Field(default_factory=list)
    current_activity_id: Optional[str] = None
    completed_activity_ids: List[str] = Field(default_factory=list)
    remaining_activity_ids: List[str] = Field(default_factory=list)
    total_estimated_duration_minutes: int = 15


class CompletionEvent(BaseModel):
    event_id: str
    learner_id: str
    completion_type: CompletionType
    target_id: str
    completed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LearnerHistoryRecord(BaseModel):
    record_id: str
    learner_id: str
    record_type: str  # "session", "lesson", "exercise", "review", "repair", "assessment", "completion"
    summary: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    details: Dict[str, Any] = Field(default_factory=dict)


class LearnerStats(BaseModel):
    learner_id: str
    total_sessions_completed: int = 0
    total_activities_completed: int = 0
    total_micro_lessons_completed: int = 0
    total_time_spent_minutes: int = 0
    last_active_at: Optional[datetime] = None
