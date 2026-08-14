# backend/engagement/xp_service.py
"""
ROLE: XP & ANTI-FARMING SERVICE

Awards XP tied to legitimate learning behavior:
- session_complete (+50 XP)
- exercise_correct (+10 XP)
- review_complete (+25 XP)
- assessment_complete (+100 XP)

ANTI-FARMING SAFEGUARD: Deduplicates processed activity IDs.
Duplicate requests with the same activity_id yield 0 XP.
"""

import logging
from typing import Dict, Optional
from backend.engagement.engagement_models import XPRecord

logger = logging.getLogger(__name__)

XP_REWARDS: Dict[str, int] = {
    "session_complete": 50,
    "exercise_correct": 10,
    "review_complete": 25,
    "assessment_complete": 100,
}


class XPService:
    """
    Service managing XP balances with anti-farming deduplication.
    """

    def __init__(self):
        self._xp_records: Dict[str, XPRecord] = {}

    def award_xp(
        self,
        learner_id: str,
        activity_id: str,
        activity_type: str = "exercise_correct",
        custom_amount: Optional[int] = None,
    ) -> XPRecord:

        record = self._xp_records.get(learner_id, XPRecord(learner_id=learner_id))

        # Anti-farming deduplication check
        if activity_id in record.processed_activity_ids:
            logger.warning(f"DUPLICATE XP FARMING PREVENTED for learner '{learner_id}' (activity_id='{activity_id}'). 0 XP awarded.")
            return record

        amount = custom_amount if custom_amount is not None else XP_REWARDS.get(activity_type, 10)
        record.total_xp += amount
        record.weekly_xp += amount
        record.processed_activity_ids.append(activity_id)

        self._xp_records[learner_id] = record
        logger.info(f"Awarded {amount} XP to learner '{learner_id}' for '{activity_type}' (total={record.total_xp}).")
        return record

    def get_xp(self, learner_id: str) -> XPRecord:
        return self._xp_records.get(learner_id, XPRecord(learner_id=learner_id))
