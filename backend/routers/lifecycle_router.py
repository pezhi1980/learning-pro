# backend/routers/lifecycle_router.py
"""
ROLE: CONTENT LIFECYCLE REST API ROUTER

Exposes FastAPI REST endpoints for:
- Publishing and deprecating content versions
- Production servable content lookup (only published status eligible)
- Submitting and querying background jobs
- Content cache statistics
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.lifecycle import (
    BackgroundJobRecord,
    BackgroundJobService,
    ContentCacheManager,
    ContentVersioningEngine,
    ContentVersionRecord,
    JobType,
    PublishingStatus,
    PublishingWorkflowService,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/lifecycle", tags=["Content Lifecycle & Background Processing"])

versioning_engine = ContentVersioningEngine()
publishing_service = PublishingWorkflowService(versioning_engine=versioning_engine)
cache_manager = ContentCacheManager()
job_service = BackgroundJobService()


class PublishRequest(BaseModel):
    version_hash: str


class SubmitJobRequest(BaseModel):
    job_type: JobType
    payload: Dict[str, Any] = {}


@router.post("/publishing/publish", response_model=ContentVersionRecord)
async def publish_content(req: PublishRequest):
    try:
        return publishing_service.publish_content(req.version_hash)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/publishing/deprecate", response_model=ContentVersionRecord)
async def deprecate_content(req: PublishRequest):
    try:
        return publishing_service.deprecate_content(req.version_hash)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/content/{content_id}", response_model=ContentVersionRecord)
async def get_servable_production_content(content_id: str):
    try:
        return publishing_service.get_servable_production_content(content_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/jobs/submit", response_model=BackgroundJobRecord)
async def submit_background_job(req: SubmitJobRequest):
    return job_service.submit_job(req.job_type, req.payload)


@router.get("/jobs/{job_id}", response_model=BackgroundJobRecord)
async def get_background_job_status(job_id: str):
    job = job_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Background job '{job_id}' not found.")
    return job


@router.get("/cache/stats", response_model=Dict[str, Any])
async def get_content_cache_stats():
    return cache_manager.get_cache_stats()
