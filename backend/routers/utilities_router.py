# backend/routers/utilities_router.py
"""
ROLE: LEARNER UTILITIES & SETTINGS REST API ROUTER

Exposes FastAPI REST endpoints for:
- Authorized Curriculum search
- Course exploration hierarchy browsing
- Bookmarks & Save for Later management
- Learning history activity lookup
- Persistent learner settings & UI preferences
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from backend.security import AccessControlContext, AuthorizationService
from backend.utilities import (
    BookmarkService,
    CourseExplorationService,
    CurriculumSearchEngine,
    LearnerSettings,
    LearningHistoryService,
    UserSettingsService,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/utilities", tags=["Learner Utilities & Settings"])

search_engine = CurriculumSearchEngine()
exploration_service = CourseExplorationService()
bookmark_service = BookmarkService()
history_service = LearningHistoryService()
settings_service = UserSettingsService()
authz_service = AuthorizationService()


class AddBookmarkPayload(BaseModel):
    item_type: str
    item_id: str
    title: str


class UpdateSettingsPayload(BaseModel):
    daily_goal_minutes: Optional[int] = None
    reminders_enabled: Optional[bool] = None
    reminder_time: Optional[str] = None
    audio_autoplay: Optional[bool] = None
    playback_speed: Optional[float] = None
    ui_theme: Optional[str] = None
    accessibility_high_contrast: Optional[bool] = None
    font_scale: Optional[float] = None


@router.get("/search")
async def search_curriculum_targets(
    query: str,
    level: Optional[str] = None,
    target_type: Optional[str] = None,
):
    return search_engine.search_curriculum(query=query, level=level, target_type=target_type)


@router.get("/explore/{level}")
async def explore_course_level(level: str):
    return exploration_service.explore_level_structure(level)


@router.post("/bookmarks/add")
async def add_bookmark(
    payload: AddBookmarkPayload,
    x_learner_id: str = Header("user_default_01"),
):
    return bookmark_service.add_bookmark(
        learner_id=x_learner_id,
        item_type=payload.item_type,
        item_id=payload.item_id,
        title=payload.title,
    )


@router.get("/bookmarks/{learner_id}")
async def get_learner_bookmarks(
    learner_id: str,
    x_requester_id: str = Header("user_default_01"),
    x_is_admin: bool = Header(False),
):
    ctx = AccessControlContext(requester_id=x_requester_id, is_admin=x_is_admin)
    try:
        authz_service.authorize_resource_access(ctx, resource_owner_id=learner_id, resource_type="bookmarks")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return bookmark_service.get_bookmarks(learner_id)


@router.get("/history/{learner_id}")
async def get_learning_history(
    learner_id: str,
    x_requester_id: str = Header("user_default_01"),
    x_is_admin: bool = Header(False),
):
    ctx = AccessControlContext(requester_id=x_requester_id, is_admin=x_is_admin)
    try:
        authz_service.authorize_resource_access(ctx, resource_owner_id=learner_id, resource_type="history")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return history_service.get_history(learner_id)


@router.get("/settings/{learner_id}")
async def get_learner_settings(
    learner_id: str,
    x_requester_id: str = Header("user_default_01"),
    x_is_admin: bool = Header(False),
):
    ctx = AccessControlContext(requester_id=x_requester_id, is_admin=x_is_admin)
    try:
        authz_service.authorize_resource_access(ctx, resource_owner_id=learner_id, resource_type="settings")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return settings_service.get_settings(learner_id)


@router.put("/settings/{learner_id}")
async def update_learner_settings(
    learner_id: str,
    payload: UpdateSettingsPayload,
    x_requester_id: str = Header("user_default_01"),
    x_is_admin: bool = Header(False),
):
    ctx = AccessControlContext(requester_id=x_requester_id, is_admin=x_is_admin)
    try:
        authz_service.authorize_resource_access(ctx, resource_owner_id=learner_id, resource_type="settings")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return settings_service.update_settings(learner_id, **payload.model_dump())
