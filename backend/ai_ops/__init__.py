# backend/ai_ops/__init__.py
"""
ROLE: AI OPERATIONS & RESOURCE CONTROL PACKAGE

Provides operational resilience and resource control infrastructure:
- AI Cost Tracking & USD Token Calculation
- 6-Policy Sliding Window Endpoint Rate Limiting
- In-Flight Concurrency & Generation Lock Controller
- Bounded Exponential Backoff Retry Manager (Transient errors only)
- Explicit Asynchronous Timeout Manager
- Duplicate Generation Protection Guard
"""

from .ai_ops_models import CostRecord, RateLimitPolicy, RetryPolicy, TimeoutConfig
from .concurrency_controller import ConcurrencyController
from .cost_tracker import AICostTracker
from .duplicate_guard import DuplicateGenerationGuard
from .rate_limiter import DEFAULT_RATE_POLICIES, RateLimiter
from .retry_manager import RetryManager
from .timeout_manager import TimeoutManager

__all__ = [
    "CostRecord",
    "RateLimitPolicy",
    "RetryPolicy",
    "TimeoutConfig",
    "AICostTracker",
    "RateLimiter",
    "DEFAULT_RATE_POLICIES",
    "ConcurrencyController",
    "RetryManager",
    "TimeoutManager",
    "DuplicateGenerationGuard",
]
