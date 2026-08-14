# backend/ai_ops/timeout_manager.py
"""
ROLE: OPERATION TIMEOUT MANAGER

Configures explicit execution timeouts for external AI and provider operations:
- lesson_generation: 25.0s
- ai_evaluation: 10.0s
- speech: 15.0s
- tts: 15.0s
"""

import asyncio
import logging
from typing import Any, Callable, Coroutine, Dict, Optional

logger = logging.getLogger(__name__)

DEFAULT_TIMEOUTS: Dict[str, float] = {
    "lesson_generation": 25.0,
    "ai_evaluation": 10.0,
    "speech": 15.0,
    "tts": 15.0,
    "default": 30.0,
}


class TimeoutManager:
    """
    Manager enforcing explicit execution timeouts on asynchronous tasks.
    """

    def __init__(self, custom_timeouts: Optional[Dict[str, float]] = None):
        self.timeouts = custom_timeouts or DEFAULT_TIMEOUTS

    async def execute_with_timeout(
        self,
        coro_fn: Callable[[], Coroutine[Any, Any, Any]],
        operation_name: str = "default",
        custom_timeout: Optional[float] = None,
    ) -> Any:
        """
        Wraps asynchronous coroutine with explicit timeout cap.
        """
        timeout_sec = custom_timeout or self.timeouts.get(operation_name, self.timeouts["default"])

        try:
            return await asyncio.wait_for(coro_fn(), timeout=timeout_sec)
        except asyncio.TimeoutError:
            logger.error(f"Operation '{operation_name}' TIMED OUT after {timeout_sec}s.")
            raise TimeoutError(f"Operation '{operation_name}' exceeded explicit timeout cap of {timeout_sec}s.")
