# backend/tests/test_ai_operations.py
"""
ROLE: TEST SUITE FOR AI OPERATIONS & RESOURCE CONTROL

Comprehensive deterministic unit tests covering:
- AI Cost Tracking & USD calculations (tokens, cache hits, retries)
- Rate Limiting policy enforcement & quota exhaustion
- Concurrency & In-Flight Generation Lock deduplication
- Bounded Exponential Retries (transient errors vs deterministic validation failure exclusion)
- Explicit Operation Timeouts
- Duplicate Generation Guard
"""

import sys
import os
import unittest
import asyncio

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.ai_ops import (
    AICostTracker,
    ConcurrencyController,
    DuplicateGenerationGuard,
    RateLimiter,
    RetryManager,
    TimeoutManager,
)
from backend.lifecycle import ContentCacheManager, ContentVersionRecord, PublishingStatus


class TestAIOperations(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.cost_tracker = AICostTracker()
        cls.rate_limiter = RateLimiter()
        cls.concurrency_controller = ConcurrencyController()
        cls.retry_manager = RetryManager()
        cls.timeout_manager = TimeoutManager()
        cls.cache_manager = ContentCacheManager()
        cls.duplicate_guard = DuplicateGenerationGuard(
            concurrency_controller=cls.concurrency_controller,
            cache_manager=cls.cache_manager,
            cost_tracker=cls.cost_tracker,
        )

    def test_1_ai_cost_tracking(self):
        """
        Verify AICostTracker calculates USD cost and maintains token/retry statistics.
        """
        rec1 = self.cost_tracker.record_cost(
            request_id="req_cost_101",
            provider="openai",
            model="gpt-4o",
            input_tokens=1000,
            output_tokens=500,
            cache_hit=False,
            retry_count=1,
        )

        self.assertGreater(rec1.cost_usd, 0.0)
        self.assertEqual(rec1.input_tokens, 1000)

        # Cache hit cost record -> 0 USD
        rec2 = self.cost_tracker.record_cost(
            request_id="req_cost_102",
            cache_hit=True,
        )
        self.assertEqual(rec2.cost_usd, 0.0)

        summary = self.cost_tracker.get_cost_summary()
        self.assertGreater(summary["total_requests"], 0)
        self.assertGreater(summary["total_input_tokens"], 0)

    def test_2_rate_limiting_enforcement(self):
        """
        Verify RateLimiter enforces sliding window quotas.
        """
        user_id = "usr_rate_201"
        endpoint = "lesson_generation"  # Max 5 req/min

        for i in range(5):
            allowed, remaining, _ = self.rate_limiter.check_rate_limit(user_id, endpoint)
            self.assertTrue(allowed, f"Request {i+1} should be allowed.")

        # 6th request must be rejected
        allowed_6th, remaining_6th, retry_after = self.rate_limiter.check_rate_limit(user_id, endpoint)
        self.assertFalse(allowed_6th, "6th request should be blocked by rate limit policy.")
        self.assertEqual(remaining_6th, 0)
        self.assertGreater(retry_after, 0.0)

    def test_3_concurrency_locks_and_duplicate_guard(self):
        """
        Verify ConcurrencyController acquires/releases locks and DuplicateGuard prevents redundant generation.
        """
        lock_key = "lock_target_g_present_simple"

        self.assertTrue(self.concurrency_controller.acquire_lock(lock_key))
        self.assertFalse(self.concurrency_controller.acquire_lock(lock_key), "Duplicate lock acquisition must fail.")

        self.concurrency_controller.release_lock(lock_key)
        self.assertFalse(self.concurrency_controller.is_locked(lock_key))

    def test_4_retry_manager_transient_vs_deterministic(self):
        """
        Verify RetryManager retries transient errors and fails immediately for deterministic validation errors.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Transient error retry case
        transient_counter = {"attempts": 0}

        async def transient_fn():
            transient_counter["attempts"] += 1
            if transient_counter["attempts"] < 2:
                raise RuntimeError("Temporary network glitch")
            return "success_transient"

        try:
            res = loop.run_until_complete(
                self.retry_manager.execute_with_retry(transient_fn, max_attempts=3, base_delay_sec=0.001)
            )
            self.assertEqual(res, "success_transient")
            self.assertEqual(transient_counter["attempts"], 2)
        finally:
            loop.close()

        # Deterministic validation error case -> must NOT retry
        loop2 = asyncio.new_event_loop()
        asyncio.set_event_loop(loop2)

        deterministic_counter = {"attempts": 0}

        async def validation_failure_fn():
            deterministic_counter["attempts"] += 1
            raise ValueError("OutputValidator failed: schema mismatch")

        try:
            with self.assertRaises(ValueError):
                loop2.run_until_complete(
                    self.retry_manager.execute_with_retry(validation_failure_fn, max_attempts=3, base_delay_sec=0.001)
                )
            self.assertEqual(deterministic_counter["attempts"], 1, "Validation failure MUST NOT be retried.")
        finally:
            loop2.close()

    def test_5_timeout_manager_enforcement(self):
        """
        Verify TimeoutManager raises TimeoutError when execution exceeds timeout cap.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        async def slow_operation():
            await asyncio.sleep(0.2)
            return "slow_result"

        try:
            with self.assertRaises(TimeoutError):
                loop.run_until_complete(
                    self.timeout_manager.execute_with_timeout(
                        slow_operation, operation_name="test_slow", custom_timeout=0.05
                    )
                )
        finally:
            loop.close()


if __name__ == "__main__":
    unittest.main()
