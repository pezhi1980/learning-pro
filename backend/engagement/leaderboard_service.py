# backend/engagement/leaderboard_service.py
"""
ROLE: PRIVACY-AWARE LEADERBOARD SERVICE

Ranks non-sensitive activity metrics (Weekly XP).
Enforces privacy/disable controls:
- Excludes learners with opt_out=True.
- Supports anonymized display names.
"""

import logging
from typing import Dict, List
from backend.engagement.engagement_models import LeaderboardEntry

logger = logging.getLogger(__name__)


class LeaderboardService:
    """
    Service generating privacy-aware activity leaderboards.
    """

    def __init__(self):
        self._entries: Dict[str, LeaderboardEntry] = {}

    def register_or_update_entry(
        self,
        learner_id: str,
        display_name: str,
        weekly_xp: int,
        opt_out: bool = False,
    ) -> LeaderboardEntry:

        entry = LeaderboardEntry(
            learner_id=learner_id,
            display_name=display_name if not opt_out else "Anonymous Learner",
            weekly_xp=weekly_xp,
            opt_out=opt_out,
        )
        self._entries[learner_id] = entry
        return entry

    def get_top_rankings(self, limit: int = 10) -> List[LeaderboardEntry]:
        """
        Returns sorted rankings filtering out opt_out learners.
        """
        eligible = [e for e in self._entries.values() if not e.opt_out]
        sorted_entries = sorted(eligible, key=lambda x: x.weekly_xp, reverse=True)

        for rank, entry in enumerate(sorted_entries, start=1):
            entry.rank = rank

        return sorted_entries[:limit]
