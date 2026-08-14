# backend/routers/course_router.py
"""
ROLE: COURSE ARCHITECTURE ROUTER

Exposes FastAPI endpoints for Course Structure and Progression:
- GET /api/course/levels/{level_code}: Retrieve 4-tier course hierarchy for a CEFR level (A1-C2).
- GET /api/course/progress/{learner_id}/{level_code}: Calculate and retrieve level progress summary.
- POST /api/course/complete: Record completion of a micro lesson and update resume position.
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.course import (
    CourseLevel,
    CourseService,
    LearnerCourseProgress,
    LevelProgressSummary,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/course", tags=["Course Architecture"])

course_service = CourseService()


class CompletionRequest(BaseModel):
    learner_id: str
    micro_lesson_id: str


@router.get("/levels/{level_code}", response_model=CourseLevel)
async def get_course_level(level_code: str):
    """
    Retrieve full 4-tier course structure (Level -> Unit -> Topic -> Micro Lesson) for a CEFR level.
    """
    level_obj = course_service.get_level(level_code.upper())
    if not level_obj:
        raise HTTPException(
            status_code=404,
            detail=f"Level '{level_code}' not supported. Supported levels: A1, A2, B1, B2, C1, C2.",
        )
    return level_obj


@router.get("/progress/{learner_id}/{level_code}", response_model=LevelProgressSummary)
async def get_level_progress(learner_id: str, level_code: str):
    """
    Calculate progress, unit/topic/lesson counts, percentage completed, and resume position for a learner.
    """
    if level_code.upper() not in course_service.list_supported_levels():
        raise HTTPException(
            status_code=404,
            detail=f"Level '{level_code}' not supported. Supported levels: A1, A2, B1, B2, C1, C2.",
        )
    return course_service.calculate_level_progress(learner_id, level_code.upper())


@router.post("/complete", response_model=LearnerCourseProgress)
async def record_micro_lesson_completion(req: CompletionRequest):
    """
    Record micro lesson completion, unlock downstream nodes, and update resume position.
    """
    ml_node = course_service.get_micro_lesson(req.micro_lesson_id)
    if not ml_node:
        raise HTTPException(
            status_code=404,
            detail=f"Micro lesson '{req.micro_lesson_id}' not found in course architecture.",
        )
    return course_service.record_micro_lesson_completion(req.learner_id, req.micro_lesson_id)
