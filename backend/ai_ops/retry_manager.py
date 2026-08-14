# backend/ai_ops/retry_manager.py
"""
ROLE: RETRY MANAGER

Executes bounded exponential backoff retries for transient failures ONLY.
CORE RULE: Do not retry deterministic validation failures (e.g., OutputValidator, CurriculumValidator).
Validation failures fail immediately.
"""

import asyncio
import logging
from typing import Any, Callable, Coroutine, Tuple, Type

logger = logging.getLogger(__name__)

# Transient exceptions eligible for retry
TRANSIENT_EXCEPTIONS: Tuple[Type[BaseException], ...] = (
    TimeoutError,
    ConnectionError,
    RuntimeError,
)

# Deterministic non-retryable validation exceptions
DETERMINISTIC_VALIDATION_EXCEPTIONS: Tuple[Type[BaseException], ...] = (
    ValueError,
    KeyError,
    TypeError,
)


class RetryManager:
    """
    Manager executing bounded retries for transient operations.
    """

    async def execute_with_retry(
        self,
        coro_fn: Callable[[], Coroutine[Any, Any, Any]],
        max_attempts: int = 3,
        base_delay_sec: float = 0.02,
        retryable_exceptions: Tuple[Type[BaseException], ...] = TRANSIENT_EXCEPTIONS,
    ) -> Any:
        """
        Executes coro_fn with bounded exponential backoff retries.
        """
        attempt = 0
        last_exception = None

        while attempt < max_attempts:
            attempt += 1
            try:
                return await coro_fn()
            except DETERMINISTIC_VALIDATION_EXCEPTIONS as e:
                # Deterministic validation failures MUST NOT be retried
                logger.error(f"Deterministic validation failure encountered ({type(e).__name__}): {e}. No retries attempted.")
                raise e
            except retryable_exceptions as e:
                last_exception = e
                if attempt >= max_attempts:
                    logger.error(f"Max retry attempts ({max_attempts}) reached for transient error: {e}")
                    raise e

                delay = base_delay_sec * (2 ** (attempt - 1))
                logger.warning(f"Transient error on attempt {attempt}/{max_attempts}: {e}. Retrying in {delay:.3f}s...")
                await asyncio.sleep(delay)

        if last_exception:
            raise last_exception
