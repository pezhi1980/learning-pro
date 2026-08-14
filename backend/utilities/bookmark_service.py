# backend/utilities/bookmark_service.py
"""
ROLE: BOOKMARK & SAVE FOR LATER SERVICE

Allows saving/bookmarking lessons, topics, grammar targets, vocabulary items, and review targets.
MANDATORY RULE: Bookmarking MUST NOT alter learner mastery state or Curriculum authority.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from backend.utilities.utility_models import BookmarkItem

logger = logging.getLogger(__name__)


class BookmarkService:
    """
    Service managing learner bookmarks and saved items.
    """

    def __init__(self):
        self._bookmarks: Dict[str, List[BookmarkItem]] = {}

    def add_bookmark(
        self,
        learner_id: str,
        item_type: str,
        item_id: str,
        title: str,
    ) -> BookmarkItem:
        """
        Adds a bookmark. Does NOT modify learner mastery state.
        """
        now = datetime.now(timezone.utc)
        bm_id = f"bm:{item_type}:{int(now.timestamp())}:{item_id}"

        user_bms = self._bookmarks.get(learner_id, [])

        # Check existing duplicate
        for b in user_bms:
            if b.item_type == item_type and b.item_id == item_id:
                return b

        item = BookmarkItem(
            bookmark_id=bm_id,
            learner_id=learner_id,
            item_type=item_type,
            item_id=item_id,
            title=title,
            created_at=now,
        )

        user_bms.append(item)
        self._bookmarks[learner_id] = user_bms
        logger.info(f"Bookmark added [{item_type}] '{title}' for learner '{learner_id}'.")
        return item

    def remove_bookmark(self, learner_id: str, bookmark_id: str) -> bool:
        user_bms = self._bookmarks.get(learner_id, [])
        initial_count = len(user_bms)
        user_bms = [b for b in user_bms if b.bookmark_id != bookmark_id]
        self._bookmarks[learner_id] = user_bms
        return len(user_bms) < initial_count

    def get_bookmarks(self, learner_id: str) -> List[BookmarkItem]:
        return self._bookmarks.get(learner_id, [])
