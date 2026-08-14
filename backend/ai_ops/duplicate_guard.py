# backend/ai_ops/duplicate_guard.py
"""
ROLE: DUPLICATE GENERATION GUARD

Protects against duplicate AI content generation by combining:
- Content Cache Manager lookup
- Concurrency Lock Manager
- Cost Tracking with cache_hit flags
"""

import asyncio
import logging
from typing import Any, Callable, Coroutine, Optional
from backend.ai_ops.concurrency_controller import ConcurrencyController
from backend.ai_ops.cost_tracker import AICostTracker
from backend.lifecycle import ContentCacheManager, ContentVersionRecord

logger = logging.getLogger(__name__)


class DuplicateGenerationGuard:
    """
    Guard preventing redundant AI generation calls via cache check and lock acquisition.
    """

    def __init__(
        self,
        concurrency_controller: Optional[ConcurrencyController] = None,
        cache_manager: Optional[ContentCacheManager] = None,
        cost_tracker: Optional[AICostTracker] = None,
    ):
        self.concurrency_controller = concurrency_controller or ConcurrencyController()
        self.cache_manager = cache_manager or ContentCacheManager()
        self.cost_tracker = cost_tracker or AICostTracker()

    async def execute_guarded_generation(
        self,
        request_id: str,
        lock_key: str,
        generation_coro_fn: Callable[[], Coroutine[Any, Any, Any]],
        cache_key: Optional[str] = None,
    ) -> Any:
        """
        Executes generation_coro_fn safely:
        1. Checks cache for cache_key -> returns cached content immediately.
        2. Acquires lock for lock_key -> if locked, waits for in-flight job completion.
        3. Executes generation and releases lock.
        """
        # STEP 1: Check cache
        if cache_key:
            cached = self.cache_manager.get_cached_content(cache_key)
            if cached:
                logger.info(f"Duplicate guard: Cache HIT for request '{request_id}'. Zero AI call made.")
                self.cost_tracker.record_cost(request_id=request_id, cache_hit=True)
                return cached

        # STEP 2: Acquire concurrency lock
        acquired = self.concurrency_controller.acquire_lock(lock_key)
        if not acquired:
            # Wait for in-flight job release
            logger.info(f"Duplicate guard: In-flight job detected for lock '{lock_key}'. Waiting...")
            await asyncio.sleep(0.1)
            if cache_key:
                cached_retry = self.cache_manager.get_cached_content(cache_key)
                if cached_retry:
                    self.cost_tracker.record_cost(request_id=request_id, cache_hit=True)
                    return cached_retry

        # STEP 3: Execute generation
        try:
            result = await generation_coro_fn()
            return result
        finally:
            self.concurrency_controller.release_lock(lock_key)
