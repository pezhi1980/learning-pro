# backend/routers/learning_router.py
"""
ROLE: LEARNING API ROUTER

Exposes FastAPI endpoints for the Core Learning Backend:
- GET /api/learner/snapshot: Retrieve learner knowledge snapshot & active errors.
- POST /api/learner/decision: Determine what the learner should study next.
- POST /api/learner/lesson/generate: Generate a validated lesson based on a LearningDecision.
- POST /api/learner/answer/submit: Submit an exercise answer, evaluate response, and update mastery.

Routes ALL lesson generation through LessonGenerationService.
Routes ALL answer processing through EvaluationService.
Direct calling of ContentAgent is STRICTLY FORBIDDEN.
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from backend.evaluation import EvaluationResult, EvaluationService
from backend.learner import LearnerService
from backend.learning import LearningDecision, LearningDecisionService
from backend.schemas import Lesson, LessonStatus
from backend.schemas.agent_output import ExerciseItem
from backend.services import CurriculumAssignmentService, LessonGenerationService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/learner", tags=["Learning Loop"])

# Singletons / Shared Service Instances
learner_service = LearnerService()
decision_service = LearningDecisionService(learner_service=learner_service)
assignment_service = CurriculumAssignmentService()
generation_service = LessonGenerationService(assignment_service=assignment_service)
evaluation_service = EvaluationService(repository=learner_service.repository)


# ── Request / Response Models ─────────────────────────────────────────────────

class AnswerSubmissionRequest(BaseModel):
    learner_id: str
    lesson_id: str
    exercise: ExerciseItem
    learner_answer: str
    submission_id: Optional[str] = None


class DecisionRequest(BaseModel):
    learner_id: str
    target_language: str = "en"
    native_language: str = "fa"
    requested_level: str = "A1"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/snapshot", response_model=Dict[str, Any])
async def get_learner_snapshot(x_learner_id: str = Header(..., alias="X-Learner-ID")):
    """
    Retrieve learner knowledge snapshot, active error patterns, and review due counts.
    """
    if not x_learner_id or not x_learner_id.strip():
        raise HTTPException(status_code=400, detail="X-Learner-ID header is required")
    return learner_service.get_learner_snapshot(x_learner_id)


@router.post("/decision", response_model=LearningDecision)
async def get_next_learning_decision(req: DecisionRequest):
    """
    Determines what the learner should study next (New Learning, Repair, or Smart Review).
    """
    return decision_service.determine_next_learning_decision(
        learner_id=req.learner_id,
        target_language=req.target_language,
        native_language=req.native_language,
        requested_level=req.requested_level,
    )


@router.post("/lesson/generate", response_model=Lesson)
async def generate_lesson_for_decision(decision: LearningDecision):
    """
    Routes a LearningDecision through CurriculumAssignmentService -> LessonGenerationService -> ContentAgent -> Validators.
    """
    try:
        assignment_req = decision_service.to_assignment_request(decision)
        lesson = await generation_service.generate_lesson(assignment_req)
        return lesson
    except Exception as e:
        logger.error(f"Failed to generate lesson for decision {decision.decision_id}: {e}")
        raise HTTPException(status_code=422, detail=f"Lesson generation failed: {str(e)}")


@router.post("/answer/submit", response_model=EvaluationResult)
async def submit_exercise_answer(req: AnswerSubmissionRequest):
    """
    Submits a learner exercise answer. Evaluates correctness, updates mastery, and tracks error patterns.
    Enforces idempotency when submission_id is provided.
    """
    try:
        eval_result = evaluation_service.submit_answer(
            learner_id=req.learner_id,
            lesson_id=req.lesson_id,
            exercise=req.exercise,
            learner_answer=req.learner_answer,
            submission_id=req.submission_id,
        )
        return eval_result
    except Exception as e:
        logger.error(f"Failed to process answer submission: {e}")
        raise HTTPException(status_code=400, detail=f"Answer evaluation failed: {str(e)}")
