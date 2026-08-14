# backend/engagement/__init__.py
"""
ROLE: ENGAGEMENT SYSTEMS PACKAGE

Provides engagement & motivation infrastructure:
- Notification Alert Service (review_due, reminder, unfinished, assessment_availability)
- Meaningful Streak Evaluation Service (qualification boundary: 1 session or 5 exercises)
- XP & Anti-Farming Deduplication Service
- Achievement Milestone & Badge Collection Service
- Privacy-Aware Weekly XP Leaderboard Service
- Social & Friend Connection Architecture Service
- Engagement Feature Flag Toggle Manager
"""

from .achievement_service import AchievementService
from .engagement_models import (
    AchievementBadge,
    EngagementFeatureFlags,
    FriendRelationship,
    LeaderboardEntry,
    NotificationRecord,
    NotificationTriggerType,
    StreakRecord,
    XPRecord,
)
from .feature_flag_manager import EngagementFeatureFlagManager
from .leaderboard_service import LeaderboardService
from .notification_service import NotificationService
from .social_service import SocialService
from .streak_service import StreakService
from .xp_service import XPService

__all__ = [
    "NotificationTriggerType",
    "NotificationRecord",
    "StreakRecord",
    "XPRecord",
    "AchievementBadge",
    "LeaderboardEntry",
    "FriendRelationship",
    "EngagementFeatureFlags",
    "NotificationService",
    "StreakService",
    "XPService",
    "AchievementService",
    "LeaderboardService",
    "SocialService",
    "EngagementFeatureFlagManager",
]
