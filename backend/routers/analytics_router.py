# backend/routers/analytics_router.py
"""
ROLE: ANALYTICS & CONTENT QUALITY REST API ROUTER

Exposes FastAPI REST endpoints for:
- Logging telemetry events
- Querying learner aggregate metrics (accuracy, completion, drop-off)
- Querying suspicious content flags
- Submitting learner content issue reports
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from backend.analytics import (
    AnalyticsEventService,
    AnalyticsEventType,
    ContentQualityAnalyticsService,
    LearningAnalyticsEngine,
    ReportType,
    UserReportService,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/analytics", tags=["Analytics & Content Quality"])

event_service = AnalyticsEventService()
analytics_engine = LearningAnalyticsEngine(event_service=event_service)
quality_service = ContentQualityAnalyticsService()
report_service = UserReportService()


class LogEventRequest(BaseModel):
    event_type: AnalyticsEventType
    learner_id: str
    target_id: Optional[str] = None
    lesson_id: Optional[str] = None
    exercise_id: Optional[str] = None
    payload: Dict[str, Any] = {}


class SubmitReportRequest(BaseModel):
    learner_id: str
    report_type: ReportType
    description: str
    lesson_id: Optional[str] = None
    exercise_id: Optional[str] = None
    content_version: Optional[str] = None
    source_trace: List[str] = []


@router.post("/events/log")
async def log_analytics_event(req: LogEventRequest):
    return event_service.log_event(
        event_type=req.event_type,
        learner_id=req.learner_id,
        target_id=req.target_id,
        lesson_id=req.lesson_id,
        exercise_id=req.exercise_id,
        payload=req.payload,
    )


@router.get("/learning/summary/{learner_id}")
async def get_learner_analytics_summary(learner_id: str):
    return analytics_engine.compute_learner_metrics(learner_id)


@router.get("/quality/suspicious")
async def get_suspicious_content_flags():
    return quality_service.list_suspicious_content()


@router.post("/reports/submit")
async def submit_user_content_report(req: SubmitReportRequest):
    return report_service.submit_report(
        learner_id=req.learner_id,
        report_type=req.report_type,
        description=req.description,
        lesson_id=req.lesson_id,
        exercise_id=req.exercise_id,
        content_version=req.content_version,
        source_trace=req.source_trace,
    )
