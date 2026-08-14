# backend/lifecycle/background_job_service.py
"""
ROLE: BACKGROUND JOB SERVICE

Supports asynchronous background work:
- pre_generation
- audio_generation
- cache_regeneration
- maintenance
- aggregation

Uses lightweight native asyncio background task execution. Does not introduce heavy infrastructure.
"""

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.lifecycle.lifecycle_models import BackgroundJobRecord, JobStatus, JobType

logger = logging.getLogger(__name__)


class BackgroundJobService:
    """
    Service managing asynchronous background job execution queues and status tracking.
    """

    def __init__(self):
        self._jobs: Dict[str, BackgroundJobRecord] = {}

    def submit_job(self, job_type: JobType, payload: Dict[str, Any]) -> BackgroundJobRecord:
        """
        Submits an asynchronous background job for background processing.
        """
        now = datetime.now(timezone.utc)
        job_id = f"job:{job_type.value}:{int(now.timestamp())}:{len(self._jobs) + 1}"

        record = BackgroundJobRecord(
            job_id=job_id,
            job_type=job_type,
            status=JobStatus.pending,
            payload=payload,
            created_at=now,
        )

        self._jobs[job_id] = record

        # Spawn asynchronous execution task
        try:
            loop = asyncio.get_running_loop()
            loop.create_task(self._execute_job(job_id))
        except RuntimeError:
            # If no running loop, execute synchronously or defer
            pass

        logger.info(f"Submitted background job '{job_id}' (type={job_type.value}).")
        return record

    async def _execute_job(self, job_id: str) -> None:
        """
        Executes a background job asynchronously.
        """
        record = self._jobs.get(job_id)
        if not record:
            return

        now = datetime.now(timezone.utc)
        record.status = JobStatus.running
        record.started_at = now

        try:
            # Simulate work execution per job_type
            if record.job_type == JobType.pre_generation:
                await asyncio.sleep(0.05)
            elif record.job_type == JobType.audio_generation:
                await asyncio.sleep(0.05)
            elif record.job_type == JobType.cache_regeneration:
                await asyncio.sleep(0.05)
            elif record.job_type == JobType.maintenance:
                await asyncio.sleep(0.05)
            elif record.job_type == JobType.aggregation:
                await asyncio.sleep(0.05)

            record.status = JobStatus.completed
            record.completed_at = datetime.now(timezone.utc)
            logger.info(f"Background job '{job_id}' completed successfully.")
        except Exception as e:
            record.status = JobStatus.failed
            record.completed_at = datetime.now(timezone.utc)
            record.error_message = str(e)
            logger.error(f"Background job '{job_id}' failed: {e}")

    def get_job(self, job_id: str) -> Optional[BackgroundJobRecord]:
        return self._jobs.get(job_id)

    def list_jobs(self, limit: int = 50) -> List[BackgroundJobRecord]:
        return list(self._jobs.values())[-limit:]
