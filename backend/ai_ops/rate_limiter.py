# backend/ai_ops/rate_limiter.py
"""
ROLE: ENDPOINT RATE LIMITER

Protects expensive AI & system endpoints using sliding-window rate limiting policies:
- lesson_generation (5 req / min)
- ai_evaluation (20 req / min)
- speech (15 req / min)
- tts (30 req / min)
- authentication (60 req / min)
- admin_operations (50 req / min)
"""

import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from backend.ai_ops.ai_ops_models import RateLimitPolicy

logger = logging.getLogger(__name__)

DEFAULT_RATE_POLICIES: Dict[str, RateLimitPolicy] = {
    "lesson_generation": RateLimitPolicy(endpoint_name="lesson_generation", max_requests=5, window_seconds=60),
    "ai_evaluation": RateLimitPolicy(endpoint_name="ai_evaluation", max_requests=20, window_seconds=60),
    "speech": RateLimitPolicy(endpoint_name="speech", max_requests=15, window_seconds=60),
    "tts": RateLimitPolicy(endpoint_name="tts", max_requests=30, window_seconds=60),
    "authentication": RateLimitPolicy(endpoint_name="authentication", max_requests=60, window_seconds=60),
    "admin_operations": RateLimitPolicy(endpoint_name="admin_operations", max_requests=50, window_seconds=60),
}


class RateLimiter:
    """
    Sliding window rate limiter for protecting endpoints from quota exhaustion.
    """

    def __init__(self, custom_policies: Optional[Dict[str, RateLimitPolicy]] = None):
        self.policies = custom_policies or DEFAULT_RATE_POLICIES
        # Key: (user_id, endpoint_name) -> List[timestamp]
        self._request_history: Dict[Tuple[str, str], List[float]] = {}

    def check_rate_limit(self, user_id: str, endpoint_name: str) -> Tuple[bool, int, float]:
        """
        Checks whether request is allowed under endpoint policy.
        Returns (is_allowed, remaining_quota, retry_after_seconds).
        """
        policy = self.policies.get(
            endpoint_name, RateLimitPolicy(endpoint_name=endpoint_name, max_requests=10, window_seconds=60)
        )

        now_ts = datetime.now(timezone.utc).timestamp()
        key = (user_id, endpoint_name)

        history = self._request_history.get(key, [])
        # Prune timestamps outside sliding window
        window_start = now_ts - policy.window_seconds
        valid_history = [ts for ts in history if ts >= window_start]

        if len(valid_history) >= policy.max_requests:
            oldest_ts = valid_history[0]
            retry_after = round(max(0.1, policy.window_seconds - (now_ts - oldest_ts)), 2)
            logger.warning(f"Rate limit EXCEEDED for user '{user_id}' on endpoint '{endpoint_name}'. Retry in {retry_after}s.")
            return False, 0, retry_after

        # Record new request timestamp
        valid_history.append(now_ts)
        self._request_history[key] = valid_history
        remaining = policy.max_requests - len(valid_history)

        return True, remaining, 0.0
