# backend/security/security_models.py
"""
ROLE: SECURITY, PRIVACY & DATA GOVERNANCE DATA MODELS

Defines structured Pydantic models for:
- Access Control Context & Resource Ownership
- File & Upload Validation Results
- Data Retention Policies
- Account & Learner Data Deletion Summaries
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AccessControlContext(BaseModel):
    requester_id: str
    is_admin: bool = False


class FileUploadValidationResult(BaseModel):
    is_valid: bool
    mime_type: str
    file_size_bytes: int
    violation_reason: Optional[str] = None


class DataRetentionPolicy(BaseModel):
    resource_type: str
    retention_days: int


class DeletionSummaryRecord(BaseModel):
    learner_id: str
    deleted_states_count: int = 0
    deleted_sessions_count: int = 0
    deleted_voice_attempts_count: int = 0
    deleted_writing_attempts_count: int = 0
    curriculum_preserved: bool = True
    deleted_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
