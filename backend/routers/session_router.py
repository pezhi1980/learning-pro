# backend/routers/session_router.py
"""
ROLE: SESSION & PROGRESS API ROUTER

Exposes FastAPI REST endpoints for Learner Daily Sessions, Resumable Session Lifecycles,
and Educational Learner History:
- POST /api/session/create: Build and persist a new Daily Learning Session from a LearningDecision.
- POST /api/session/{session_id}/start: Start a session.
- POST /api/session/{session_id}/pause: Pause an active session.
- POST /api/session/{session_id}/resume: Resume a paused session.
- POST /api/session/{session_id}/complete_activity: Mark an activity complete and advance session.
- POST /api/session/{session_id}/complete: Mark session complete.
- GET /api/session/history/{learner_id}: Retrieve educational learning history.
- GET /api/session/stats/{learner_id}: Retrieve aggregate learner statistics.
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from backend.learning import LearningDecision, LearningDecisionService
from backend.session import (
    DailyLearningSession,
    DailySessionService,
    LearnerHistoryRecord,
    LearnerStats,
    LearningHistoryService,
    ProgressService,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/session", tags=["Session & Progress"])

# Service singletons
decision_service = LearningDecisionService()
daily_session_service = DailySessionService()
history_service = LearningHistoryService()
progress_service = ProgressService(
    daily_session_service=daily_session_service,
    history_service=history_service,
)


class CreateSessionRequest(BaseModel):
    learner_id: str
    target_language: str = "en"
    native_language: str = "fa"
    requested_level: str = "A1"


class CompleteActivityRequest(BaseModel):
    activity_id: str


@router.post("/create", response_model=DailyLearningSession)
async def create_daily_session(req: CreateSessionRequest):
    """
    Executes LearningDecision Engine and builds a new structured Daily Learning Session.
    """
    decision = decision_service.determine_next_learning_decision(
        learner_id=req.learner_id,
        target_language=req.target_language,
        native_language=req.native_language,
        requested_level=req.requested_level,
    )
    return daily_session_service.create_session(decision)


@router.post("/{session_id}/start", response_model=DailyLearningSession)
async def start_session(session_id: str):
    try:
        return daily_session_service.start_session(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}/pause", response_model=DailyLearningSession)
async def pause_session(session_id: str):
    try:
        return daily_session_service.pause_session(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}/resume", response_model=DailyLearningSession)
async def resume_session(session_id: str):
    try:
        return daily_session_service.resume_session(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}/complete_activity", response_model=DailyLearningSession)
async def complete_activity(session_id: str, req: CompleteActivityRequest):
    try:
        return daily_session_service.complete_activity(session_id, req.activity_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}/complete", response_model=DailyLearningSession)
async def complete_session(session_id: str):
    try:
        return progress_service.complete_session(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/history/{learner_id}", response_model=List[LearnerHistoryRecord])
async def get_learner_history(
    learner_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    record_type: Optional[str] = None,
):
    return history_service.get_learner_history(learner_id, limit=limit, offset=offset, record_type=record_type)


@router.get("/stats/{learner_id}", response_model=LearnerStats)
async def get_learner_stats(learner_id: str):
    return history_service.get_learner_stats(learner_id)
