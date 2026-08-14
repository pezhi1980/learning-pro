# backend/engagement/engagement_models.py
"""
ROLE: ENGAGEMENT SYSTEMS DATA MODELS

Defines structured Pydantic data models for:
- Notifications (review_due, learning_reminder, unfinished_session, assessment_availability)
- Streaks & Meaningful Activity qualification
- XP & Anti-Farming tracking
- Achievements & Milestone Badges
- Privacy-Aware Leaderboard Entries
- Social & Friend Relationships
- Engagement Feature Flags
"""

from datetime import date, datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class NotificationTriggerType(str, Enum):
    review_due = "review_due"
    learning_reminder = "learning_reminder"
    unfinished_session = "unfinished_session"
    assessment_availability = "assessment_availability"


class NotificationRecord(BaseModel):
    notification_id: str
    recipient_id: str
    trigger_type: NotificationTriggerType
    title: str
    message: str
    is_read: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class StreakRecord(BaseModel):
    learner_id: str
    current_streak: int = 0
    longest_streak: int = 0
    last_learning_date: Optional[date] = None
    qualifying_activities_today: int = 0


class XPRecord(BaseModel):
    learner_id: str
    total_xp: int = 0
    weekly_xp: int = 0
    processed_activity_ids: List[str] = Field(default_factory=list)


class AchievementBadge(BaseModel):
    badge_id: str
    title: str
    description: str
    unlocked_at: Optional[datetime] = None
    is_unlocked: bool = False


class LeaderboardEntry(BaseModel):
    learner_id: str
    display_name: str
    weekly_xp: int
    rank: int = 0
    opt_out: bool = False


class FriendRelationship(BaseModel):
    learner_id: str
    friend_id: str
    status: str = "accepted"  # "pending", "accepted"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EngagementFeatureFlags(BaseModel):
    enable_streaks: bool = True
    enable_xp: bool = True
    enable_achievements: bool = True
    enable_leaderboards: bool = True
    enable_social: bool = True
    enable_notifications: bool = True
