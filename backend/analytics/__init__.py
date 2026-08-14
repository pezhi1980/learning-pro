# backend/analytics/__init__.py
"""
ROLE: ANALYTICS & CONTENT QUALITY PACKAGE

Provides learning telemetry, performance metrics, and content quality analytics:
- 8 Analytics Event Types (lesson_started, lesson_completed, exercise_answered, hint_used, review_completed, repair_completed, session_abandoned, assessment_completed)
- Learning Analytics Engine (accuracy, completion, retention, drop-off, difficult targets)
- Content Quality Analytics Service (abnormally high failure, high abandonment, frequent reports, repeated regeneration)
- User Content Issue Reporting Service (6 report categories with source traceability)
"""

from .analytics_event_service import AnalyticsEventService
from .analytics_models import (
    AnalyticsEventRecord,
    AnalyticsEventType,
    ContentQualitySignalRecord,
    ReportType,
    UserReportRecord,
)
from .content_quality_analytics_service import ContentQualityAnalyticsService
from .learning_analytics_engine import LearningAnalyticsEngine
from .user_report_service import UserReportService

__all__ = [
    "AnalyticsEventType",
    "ReportType",
    "AnalyticsEventRecord",
    "UserReportRecord",
    "ContentQualitySignalRecord",
    "AnalyticsEventService",
    "LearningAnalyticsEngine",
    "ContentQualityAnalyticsService",
    "UserReportService",
]
