# backend/session/__init__.py
"""
ROLE: SESSION & PROGRESS SYSTEM PACKAGE

Provides complete Session Building, Daily Resumable Sessions, Progress & Completion Tracking,
and Educational Learning History Services.
"""

from .session_models import (
    ActivityType,
    SessionStatus,
    CompletionType,
    SessionActivity,
    DailyLearningSession,
    CompletionEvent,
    LearnerHistoryRecord,
    LearnerStats,
)
from .session_builder import SessionBuilder
from .daily_session_service import DailySessionService
from .learning_history_service import LearningHistoryService
from .progress_service import ProgressService

__all__ = [
    "ActivityType",
    "SessionStatus",
    "CompletionType",
    "SessionActivity",
    "DailyLearningSession",
    "CompletionEvent",
    "LearnerHistoryRecord",
    "LearnerStats",
    "SessionBuilder",
    "DailySessionService",
    "LearningHistoryService",
    "ProgressService",
]
