# backend/lifecycle/lifecycle_models.py
"""
ROLE: CONTENT LIFECYCLE & BACKGROUND PROCESSING DATA MODELS

Defines structured data models for:
- 6 Publishing Workflow states (generated, rejected, validated, published, deprecated, replaced)
- Immutable Content Version records for lessons, explanations, examples, exercises, and audio references
- Background Job types and statuses (pre_generation, audio_generation, cache_regeneration, maintenance, aggregation)
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PublishingStatus(str, Enum):
    generated = "generated"
    rejected = "rejected"
    validated = "validated"
    published = "published"
    deprecated = "deprecated"
    replaced = "replaced"


class JobType(str, Enum):
    pre_generation = "pre_generation"
    audio_generation = "audio_generation"
    cache_regeneration = "cache_regeneration"
    maintenance = "maintenance"
    aggregation = "aggregation"


class JobStatus(str, Enum):
    pending = "pending"
    running = "running"
    completed = "completed"
    failed = "failed"


class ContentVersionRecord(BaseModel):
    content_id: str
    version_index: int = 1
    content_version_hash: str
    target_ids: List[str] = Field(default_factory=list)
    publishing_status: PublishingStatus = PublishingStatus.generated
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: Optional[datetime] = None
    deprecated_at: Optional[datetime] = None
    replaced_by_version_hash: Optional[str] = None
    content_payload: Dict[str, Any] = Field(default_factory=dict)


class BackgroundJobRecord(BaseModel):
    job_id: str
    job_type: JobType
    status: JobStatus = JobStatus.pending
    payload: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class PreGenerationJobRequest(BaseModel):
    level_code: str = "A1"
    topic_code: Optional[str] = None
    target_micro_lesson_ids: List[str] = Field(default_factory=list)
