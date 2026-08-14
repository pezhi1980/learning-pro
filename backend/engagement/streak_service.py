# backend/engagement/streak_service.py
"""
ROLE: MEANINGFUL STREAK SERVICE

Defines and tracks meaningful learning streaks.
QUALIFICATION RULE: Requires completing at least 1 Daily Session OR answering >= 5 evaluated exercises in a calendar day.
MANDATORY RULE: Streaks do NOT award learner mastery or alter curriculum authority.
"""

import logging
from datetime import date, timedelta
from typing import Dict, Optional
from backend.engagement.engagement_models import StreakRecord

logger = logging.getLogger(__name__)


class StreakService:
    """
    Service calculating learner streaks based on legitimate learning milestones.
    """

    def __init__(self):
        self._streaks: Dict[str, StreakRecord] = {}

    def record_activity(
        self,
        learner_id: str,
        is_full_session: bool = False,
        exercises_count: int = 0,
        activity_date: Optional[date] = None,
    ) -> StreakRecord:
        """
        Records activity and evaluates if streak criteria is met.
        """
        today = activity_date or date.today()
        record = self._streaks.get(learner_id, StreakRecord(learner_id=learner_id))

        # Check qualification: full session OR >= 5 exercises
        qualifies = is_full_session or (exercises_count >= 5) or (record.qualifying_activities_today + exercises_count >= 5)

        if not qualifies:
            record.qualifying_activities_today += exercises_count
            self._streaks[learner_id] = record
            return record

        # Qualified for today!
        if record.last_learning_date == today:
            # Already credited today
            return record

        if record.last_learning_date == (today - timedelta(days=1)):
            # Consecutive day!
            record.current_streak += 1
        elif record.last_learning_date is None:
            # First day
            record.current_streak = 1
        else:
            # Gap > 1 day -> Streak broken, reset to 1
            logger.info(f"Streak break detected for learner '{learner_id}'. Previous streak={record.current_streak}.")
            record.current_streak = 1

        record.last_learning_date = today
        record.qualifying_activities_today = 0
        if record.current_streak > record.longest_streak:
            record.longest_streak = record.current_streak

        self._streaks[learner_id] = record
        logger.info(f"Learner '{learner_id}' streak updated: current={record.current_streak}, longest={record.longest_streak}.")
        return record

    def get_streak(self, learner_id: str) -> StreakRecord:
        return self._streaks.get(learner_id, StreakRecord(learner_id=learner_id))
