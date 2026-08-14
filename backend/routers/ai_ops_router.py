# backend/routers/ai_ops_router.py
"""
ROLE: AI OPERATIONS REST API ROUTER

Exposes FastAPI REST endpoints for:
- AI Cost summary & token metrics lookup
- Rate limit status checking
- Active concurrency locks inspection
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from backend.ai_ops import (
    AICostTracker,
    ConcurrencyController,
    RateLimiter,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai-ops", tags=["AI Operations & Resource Control"])

cost_tracker = AICostTracker()
rate_limiter = RateLimiter()
concurrency_controller = ConcurrencyController()


@router.get("/cost/summary")
async def get_cost_summary():
    return cost_tracker.get_cost_summary()


@router.get("/rate-limits/status")
async def check_rate_limit_status(
    endpoint_name: str = "lesson_generation",
    x_user_id: str = Header("user_default_01"),
):
    is_allowed, remaining, retry_after = rate_limiter.check_rate_limit(user_id=x_user_id, endpoint_name=endpoint_name)
    return {
        "user_id": x_user_id,
        "endpoint_name": endpoint_name,
        "is_allowed": is_allowed,
        "remaining_quota": remaining,
        "retry_after_seconds": retry_after,
    }


@router.get("/locks/active")
async def get_active_concurrency_locks():
    return {"active_locks_count": len(concurrency_controller._active_locks)}
