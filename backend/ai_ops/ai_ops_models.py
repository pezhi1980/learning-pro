# backend/ai_ops/ai_ops_models.py
"""
ROLE: AI OPERATIONS & RESOURCE CONTROL DATA MODELS

Defines structured Pydantic models for:
- AI Cost Tracking (provider, model, tokens, cost USD, cache hit, retry count)
- Endpoint Rate Limiting policies
- Exponential Backoff Retry policies
- Asynchronous Operation Timeout configurations
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class CostRecord(BaseModel):
    request_id: str
    provider: str = "openai"
    model: str = "gpt-4o"
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    cache_hit: bool = False
    retry_count: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class RateLimitPolicy(BaseModel):
    endpoint_name: str
    max_requests: int
    window_seconds: int = 60


class RetryPolicy(BaseModel):
    max_attempts: int = 3
    base_delay_seconds: float = 0.1


class TimeoutConfig(BaseModel):
    operation_name: str
    timeout_seconds: float
