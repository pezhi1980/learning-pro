# backend/analytics/analytics_event_service.py
"""
ROLE: ANALYTICS EVENT SERVICE

Records and queries structured telemetry events across 8 event categories:
lesson_started, lesson_completed, exercise_answered, hint_used,
review_completed, repair_completed, session_abandoned, assessment_completed.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.analytics.analytics_models import AnalyticsEventRecord, AnalyticsEventType

logger = logging.getLogger(__name__)


class AnalyticsEventService:
    """
    Service logging and retrieving telemetry events for learning analytics.
    """

    def __init__(self):
        self._events: List[AnalyticsEventRecord] = []

    def log_event(
        self,
        event_type: AnalyticsEventType,
        learner_id: str,
        target_id: Optional[str] = None,
        lesson_id: Optional[str] = None,
        exercise_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
    ) -> AnalyticsEventRecord:

        now = datetime.now(timezone.utc)
        event_id = f"evt:{event_type.value}:{int(now.timestamp())}:{len(self._events) + 1}"

        record = AnalyticsEventRecord(
            event_id=event_id,
            event_type=event_type,
            learner_id=learner_id,
            target_id=target_id,
            lesson_id=lesson_id,
            exercise_id=exercise_id,
            payload=payload or {},
            timestamp=now,
        )

        self._events.append(record)
        logger.info(f"Analytics event logged [{event_type.value}] for learner '{learner_id}' (id={event_id}).")
        return record

    def get_events(
        self,
        learner_id: Optional[str] = None,
        event_type: Optional[AnalyticsEventType] = None,
        limit: int = 100,
    ) -> List[AnalyticsEventRecord]:

        results = self._events
        if learner_id:
            results = [e for e in results if e.learner_id == learner_id]
        if event_type:
            results = [e for e in results if e.event_type == event_type]

        return results[-limit:]
