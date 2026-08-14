# backend/routers/writing_router.py
"""
ROLE: WRITING, FREE PRODUCTION & HINTS REST API ROUTER

Exposes FastAPI REST endpoints for:
- Writing task evaluation (5 task types, 3 evaluation modes)
- Progressive hint requests (hint_1..3, answer_reveal)
- Learner writing evaluation history
"""

import logging
from typing import List
from fastapi import APIRouter, HTTPException

from backend.writing import (
    HintRequest,
    HintResponse,
    WritingEvaluationResult,
    WritingService,
    WritingSubmission,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/writing", tags=["Writing & Free Production"])

writing_service = WritingService()


@router.post("/evaluate", response_model=WritingEvaluationResult)
async def evaluate_writing(submission: WritingSubmission):
    try:
        return writing_service.evaluate_writing(submission)
    except Exception as e:
        logger.error(f"Writing evaluation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/hint/request", response_model=HintResponse)
async def request_progressive_hint(req: HintRequest):
    try:
        return writing_service.request_progressive_hint(req)
    except Exception as e:
        logger.error(f"Hint request failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/history/{learner_id}", response_model=List[WritingEvaluationResult])
async def get_learner_writing_history(learner_id: str):
    return writing_service.get_learner_writing_history(learner_id)
