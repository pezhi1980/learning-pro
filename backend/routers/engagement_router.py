# backend/routers/engagement_router.py
"""
ROLE: ENGAGEMENT SYSTEMS REST API ROUTER

Exposes FastAPI REST endpoints for:
- Streaks & meaningful activity lookup
- XP balance & anti-farming verification
- Achievement badge collection
- Privacy-aware weekly XP leaderboard
- Friend connections
- Engagement feature flags lookup
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from backend.engagement import (
    AchievementService,
    EngagementFeatureFlagManager,
    LeaderboardService,
    NotificationService,
    SocialService,
    StreakService,
    XPService,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/engagement", tags=["Engagement Systems"])

feature_flag_manager = EngagementFeatureFlagManager()
streak_service = StreakService()
xp_service = XPService()
achievement_service = AchievementService()
leaderboard_service = LeaderboardService()
social_service = SocialService()
notification_service = NotificationService()


class FriendRequestPayload(BaseModel):
    friend_id: str


@router.get("/flags")
async def get_engagement_feature_flags():
    return feature_flag_manager.get_flags()


@router.get("/streak/{learner_id}")
async def get_learner_streak(learner_id: str):
    if not feature_flag_manager.is_enabled("streaks"):
        raise HTTPException(status_code=403, detail="Streak feature is currently disabled.")
    return streak_service.get_streak(learner_id)


@router.get("/xp/{learner_id}")
async def get_learner_xp(learner_id: str):
    if not feature_flag_manager.is_enabled("xp"):
        raise HTTPException(status_code=403, detail="XP feature is currently disabled.")
    return xp_service.get_xp(learner_id)


@router.get("/achievements/{learner_id}")
async def get_learner_achievements(learner_id: str):
    if not feature_flag_manager.is_enabled("achievements"):
        raise HTTPException(status_code=403, detail="Achievements feature is currently disabled.")
    return achievement_service.get_unlocked_badges(learner_id)


@router.get("/leaderboard")
async def get_weekly_leaderboard():
    if not feature_flag_manager.is_enabled("leaderboards"):
        raise HTTPException(status_code=403, detail="Leaderboard feature is currently disabled.")
    return leaderboard_service.get_top_rankings()


@router.post("/friends/request")
async def send_friend_request(
    req: FriendRequestPayload,
    x_learner_id: str = Header("user_default_01"),
):
    if not feature_flag_manager.is_enabled("social"):
        raise HTTPException(status_code=403, detail="Social feature is currently disabled.")
    return social_service.send_friend_request(learner_id=x_learner_id, friend_id=req.friend_id)
