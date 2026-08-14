# backend/routers/assessment_router.py
"""
ROLE: ASSESSMENT REST API ROUTER

Exposes FastAPI endpoints for:
- Placement Test creation & evaluation
- Diagnostic Assessment creation & evaluation (5 dimensions)
- Topic, Unit, and Cumulative Checkpoints
- Level Assessment creation & evaluation
Enforces server-side authoritative state.
"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.assessment import (
    AssessmentSession,
    AssessmentSubmission,
    CheckpointResult,
    CheckpointService,
    DiagnosticReport,
    DiagnosticService,
    LevelAssessmentReport,
    LevelAssessmentService,
    PlacementResult,
    PlacementService,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/assessment", tags=["Assessment Systems"])

# Service Singletons
placement_service = PlacementService()
diagnostic_service = DiagnosticService()
checkpoint_service = CheckpointService()
level_service = LevelAssessmentService()


class CreateTestRequest(BaseModel):
    learner_id: str
    level_code: Optional[str] = "A1"
    target_id: Optional[str] = None


class SubmissionBatchRequest(BaseModel):
    submissions: List[AssessmentSubmission]


# ── Placement Test Endpoints ───────────────────────────────────────────────

@router.post("/placement/create", response_model=AssessmentSession)
async def create_placement_test(req: CreateTestRequest):
    return placement_service.create_placement_test(req.learner_id)


@router.post("/placement/{session_id}/submit", response_model=PlacementResult)
async def submit_placement_test(session_id: str, req: SubmissionBatchRequest):
    try:
        return placement_service.evaluate_placement_test(session_id, req.submissions)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Diagnostic Assessment Endpoints ─────────────────────────────────────────

@router.post("/diagnostic/create", response_model=AssessmentSession)
async def create_diagnostic_test(req: CreateTestRequest):
    level = req.level_code or "A1"
    return diagnostic_service.create_diagnostic_test(req.learner_id, level_code=level)


@router.post("/diagnostic/{session_id}/submit", response_model=DiagnosticReport)
async def submit_diagnostic_test(session_id: str, req: SubmissionBatchRequest):
    try:
        return diagnostic_service.evaluate_diagnostic_test(session_id, req.submissions)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Checkpoint Assessment Endpoints ────────────────────────────────────────

@router.post("/checkpoint/topic/create", response_model=AssessmentSession)
async def create_topic_checkpoint(req: CreateTestRequest):
    if not req.target_id:
        raise HTTPException(status_code=400, detail="target_id (topic_id) is required for Topic Checkpoint.")
    return checkpoint_service.create_topic_checkpoint(req.learner_id, req.target_id)


@router.post("/checkpoint/unit/create", response_model=AssessmentSession)
async def create_unit_checkpoint(req: CreateTestRequest):
    if not req.target_id:
        raise HTTPException(status_code=400, detail="target_id (unit_id) is required for Unit Checkpoint.")
    return checkpoint_service.create_unit_checkpoint(req.learner_id, req.target_id)


@router.post("/checkpoint/cumulative/create", response_model=AssessmentSession)
async def create_cumulative_checkpoint(req: CreateTestRequest):
    level = req.level_code or "A1"
    return checkpoint_service.create_cumulative_checkpoint(req.learner_id, level_code=level)


@router.post("/checkpoint/{session_id}/submit", response_model=CheckpointResult)
async def submit_checkpoint_test(session_id: str, req: SubmissionBatchRequest):
    try:
        return checkpoint_service.evaluate_checkpoint(session_id, req.submissions)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


# ── Level Assessment Endpoints ──────────────────────────────────────────────

@router.post("/level/create", response_model=AssessmentSession)
async def create_level_assessment(req: CreateTestRequest):
    level = req.level_code or "A1"
    return level_service.create_level_assessment(req.learner_id, level_code=level)


@router.post("/level/{session_id}/submit", response_model=LevelAssessmentReport)
async def submit_level_assessment(session_id: str, req: SubmissionBatchRequest):
    try:
        return level_service.evaluate_level_assessment(session_id, req.submissions)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
