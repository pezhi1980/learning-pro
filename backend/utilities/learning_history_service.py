# backend/utilities/learning_history_service.py
"""
ROLE: LEARNING HISTORY SERVICE

Logs and queries learner historical learning activity for UI display and history timelines.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.utilities.utility_models import LearningHistoryRecord

logger = logging.getLogger(__name__)


class LearningHistoryService:
    """
    Service tracking learner activity history.
    """

    def __init__(self):
        self._history: Dict[str, List[LearningHistoryRecord]] = {}

    def record_history(
        self,
        learner_id: str,
        activity_type: str,
        title: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> LearningHistoryRecord:

        now = datetime.now(timezone.utc)
        hid = f"hist:{activity_type}:{int(now.timestamp())}"

        record = LearningHistoryRecord(
            history_id=hid,
            learner_id=learner_id,
            activity_type=activity_type,
            title=title,
            details=details or {},
            timestamp=now,
        )

        user_hist = self._history.get(learner_id, [])
        user_hist.append(record)
        self._history[learner_id] = user_hist

        logger.info(f"Learning history recorded [{activity_type}] '{title}' for learner '{learner_id}'.")
        return record

    def get_history(self, learner_id: str, limit: int = 50) -> List[LearningHistoryRecord]:
        user_hist = self._history.get(learner_id, [])
        return user_hist[-limit:]
