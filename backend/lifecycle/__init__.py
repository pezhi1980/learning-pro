# backend/lifecycle/__init__.py
"""
ROLE: CONTENT LIFECYCLE & BACKGROUND PROCESSING PACKAGE

Provides complete Content Lifecycle infrastructure:
- Immutable Content Versioning Engine
- 6-State Publishing Workflow Service (generated, rejected, validated, published, deprecated, replaced)
- Deterministic SHA-256 Content Cache Manager
- Pre-Generation Service enforcing normal validation pipelines
- Lightweight asyncio Background Job Service
"""

from .lifecycle_models import (
    PublishingStatus,
    JobType,
    JobStatus,
    ContentVersionRecord,
    BackgroundJobRecord,
    PreGenerationJobRequest,
)
from .content_versioning_engine import ContentVersioningEngine
from .publishing_workflow_service import PublishingWorkflowService
from .content_cache_manager import ContentCacheManager
from .pre_generation_service import PreGenerationService
from .background_job_service import BackgroundJobService

__all__ = [
    "PublishingStatus",
    "JobType",
    "JobStatus",
    "ContentVersionRecord",
    "BackgroundJobRecord",
    "PreGenerationJobRequest",
    "ContentVersioningEngine",
    "PublishingWorkflowService",
    "ContentCacheManager",
    "PreGenerationService",
    "BackgroundJobService",
]
