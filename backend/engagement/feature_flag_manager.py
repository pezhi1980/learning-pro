# backend/engagement/feature_flag_manager.py
"""
ROLE: ENGAGEMENT FEATURE FLAG MANAGER

Controls dynamic feature toggles for optional engagement subsystems:
enable_streaks, enable_xp, enable_achievements, enable_leaderboards, enable_social, enable_notifications.
"""

import logging
from backend.engagement.engagement_models import EngagementFeatureFlags

logger = logging.getLogger(__name__)


class EngagementFeatureFlagManager:
    """
    Manager maintaining engagement feature flag toggles.
    """

    def __init__(self):
        self._flags = EngagementFeatureFlags()

    def get_flags(self) -> EngagementFeatureFlags:
        return self._flags

    def update_flags(
        self,
        enable_streaks: bool = True,
        enable_xp: bool = True,
        enable_achievements: bool = True,
        enable_leaderboards: bool = True,
        enable_social: bool = True,
        enable_notifications: bool = True,
    ) -> EngagementFeatureFlags:

        self._flags = EngagementFeatureFlags(
            enable_streaks=enable_streaks,
            enable_xp=enable_xp,
            enable_achievements=enable_achievements,
            enable_leaderboards=enable_leaderboards,
            enable_social=enable_social,
            enable_notifications=enable_notifications,
        )
        logger.info("Engagement feature flags updated.")
        return self._flags

    def is_enabled(self, feature_name: str) -> bool:
        return getattr(self._flags, f"enable_{feature_name}", True)
