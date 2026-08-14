# backend/engagement/achievement_service.py
"""
ROLE: ACHIEVEMENT & BADGE SERVICE

Evaluates learning milestones and awards achievement badges:
- first_lesson (Complete 1st lesson)
- streak_7 (Reach 7-day streak)
- vocab_50 (Master 50 vocabulary items)
- perfect_session (100% accuracy in a daily session)
- level_complete_a1 (Complete Level A1)

CORE RULE: Rewards are kept separate from learner mastery and curriculum authority.
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional
from backend.engagement.engagement_models import AchievementBadge

logger = logging.getLogger(__name__)

CATALOG_BADGES: Dict[str, Dict[str, str]] = {
    "first_lesson": {"title": "First Step", "description": "Completed your first learning lesson."},
    "streak_7": {"title": "Consistent Learner", "description": "Maintained a 7-day learning streak."},
    "vocab_50": {"title": "Vocabulary Builder", "description": "Practiced 50 vocabulary items."},
    "perfect_session": {"title": "Flawless Execution", "description": "Achieved 100% accuracy in a daily session."},
    "level_complete_a1": {"title": "A1 Graduate", "description": "Completed Level A1 Course Curriculum."},
}


class AchievementService:
    """
    Service managing achievement milestone evaluation and badge collection.
    """

    def __init__(self):
        self._unlocked: Dict[str, Dict[str, AchievementBadge]] = {}

    def evaluate_achievements(
        self,
        learner_id: str,
        total_lessons: int = 0,
        current_streak: int = 0,
        total_vocab: int = 0,
        is_perfect_session: bool = False,
        completed_level: Optional[str] = None,
    ) -> List[AchievementBadge]:

        learner_badges = self._unlocked.get(learner_id, {})
        newly_unlocked: List[AchievementBadge] = []
        now = datetime.now(timezone.utc)

        milestone_conditions = [
            ("first_lesson", total_lessons >= 1),
            ("streak_7", current_streak >= 7),
            ("vocab_50", total_vocab >= 50),
            ("perfect_session", is_perfect_session),
            ("level_complete_a1", completed_level == "A1"),
        ]

        for badge_id, condition in milestone_conditions:
            if condition and badge_id not in learner_badges:
                info = CATALOG_BADGES[badge_id]
                badge = AchievementBadge(
                    badge_id=badge_id,
                    title=info["title"],
                    description=info["description"],
                    unlocked_at=now,
                    is_unlocked=True,
                )
                learner_badges[badge_id] = badge
                newly_unlocked.append(badge)
                logger.info(f"BADGE UNLOCKED [{badge_id}] for learner '{learner_id}'.")

        self._unlocked[learner_id] = learner_badges
        return newly_unlocked

    def get_unlocked_badges(self, learner_id: str) -> List[AchievementBadge]:
        learner_badges = self._unlocked.get(learner_id, {})
        return list(learner_badges.values())
