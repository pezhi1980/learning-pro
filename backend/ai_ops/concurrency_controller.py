# backend/ai_ops/concurrency_controller.py
"""
ROLE: CONCURRENCY CONTROLLER & GENERATION LOCK MANAGER

Prevents simultaneous duplicate reusable AI generation jobs.
Maintains in-flight task locks by target constraints hash.
"""

import asyncio
import logging
from typing import Dict, Set

logger = logging.getLogger(__name__)


class ConcurrencyController:
    """
    Manager for controlling concurrent generation tasks and preventing duplicate jobs.
    """

    def __init__(self):
        self._active_locks: Set[str] = set()

    def acquire_lock(self, lock_key: str) -> bool:
        """
        Attempts to acquire in-flight generation lock for lock_key.
        Returns True if acquired successfully, False if already locked.
        """
        if lock_key in self._active_locks:
            logger.warning(f"Concurrency lock COLLISION for key '{lock_key}'. Duplicate job prevented.")
            return False

        self._active_locks.add(lock_key)
        logger.info(f"Acquired concurrency lock for key '{lock_key}'.")
        return True

    def release_lock(self, lock_key: str) -> None:
        """
        Releases in-flight generation lock for lock_key.
        """
        self._active_locks.discard(lock_key)
        logger.info(f"Released concurrency lock for key '{lock_key}'.")

    def is_locked(self, lock_key: str) -> bool:
        return lock_key in self._active_locks
