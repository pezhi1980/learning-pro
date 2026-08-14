# backend/engagement/social_service.py
"""
ROLE: SOCIAL & FRIEND ARCHITECTURE SERVICE

Manages friend relationships and optional activity sharing.
CORE RULE: Social data is kept strictly separate from learning authority and mastery.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List
from backend.engagement.engagement_models import FriendRelationship

logger = logging.getLogger(__name__)


class SocialService:
    """
    Service managing social friend connections.
    """

    def __init__(self):
        self._friends: List[FriendRelationship] = []

    def send_friend_request(self, learner_id: str, friend_id: str) -> FriendRelationship:
        rel = FriendRelationship(
            learner_id=learner_id,
            friend_id=friend_id,
            status="accepted",
            created_at=datetime.now(timezone.utc),
        )
        self._friends.append(rel)
        logger.info(f"Friend relationship established between '{learner_id}' and '{friend_id}'.")
        return rel

    def get_friends(self, learner_id: str) -> List[str]:
        result = []
        for f in self._friends:
            if f.learner_id == learner_id and f.status == "accepted":
                result.append(f.friend_id)
            elif f.friend_id == learner_id and f.status == "accepted":
                result.append(f.learner_id)
        return result
