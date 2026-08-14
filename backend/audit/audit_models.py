# backend/audit/audit_models.py
"""
ROLE: AUDIT, TRACEABILITY & ADMIN DATA MODELS

Defines structured data models for:
- Audit Event types across 8 categories (generation, validation, publication, deprecation, target_selection, evaluation, mastery_update, admin_action)
- End-to-end Generation Trace records tracking all 10 mandatory fields
- Explicit System Versioning manifest (model_version, prompt_version, schema_version, source_version)
- Admin Control actions
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AuditEventType(str, Enum):
    generation = "generation"
    validation = "validation"
    publication = "publication"
    deprecation = "deprecation"
    target_selection = "target_selection"
    evaluation = "evaluation"
    mastery_update = "mastery_update"
    admin_action = "admin_action"


class AdminControlAction(str, Enum):
    publish = "publish"
    unpublish = "unpublish"
    deprecate = "deprecate"
    regenerate = "regenerate"
    inspect_history = "inspect_history"
    disable_content = "disable_content"


class SystemVersionManifest(BaseModel):
    model_name: str = "gpt-4o"
    model_version: str = "gpt-4o-2024-08-06"
    prompt_version: str = "pedagogy_v2.1"
    schema_version: str = "agent_schema_v1.0"
    source_version_hash: str = "sha256_curriculum_source_pdf_v1"


class GenerationTraceRecord(BaseModel):
    request_id: str
    assigned_targets: List[str] = Field(default_factory=list)
    allowed_targets: List[str] = Field(default_factory=list)
    model: str
    model_version: str
    prompt_version: str
    schema_version: str
    source_version_hash: str
    validator_results: Dict[str, Any] = Field(default_factory=dict)
    content_version_hash: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditLogRecord(BaseModel):
    log_id: str
    event_type: AuditEventType
    actor_id: str = "system"
    details: Dict[str, Any] = Field(default_factory=dict)
    target_ids: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
