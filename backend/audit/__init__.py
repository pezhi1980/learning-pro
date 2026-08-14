# backend/audit/__init__.py
"""
ROLE: AUDIT, TRACEABILITY & ADMIN CONTROL PACKAGE

Provides complete administrative inspection, control, audit logging, and generation traceability infrastructure:
- 8 Audit Event Types (generation, validation, publication, deprecation, target_selection, evaluation, mastery_update, admin_action)
- 10-Field End-to-End Generation Trace Engine
- 4-Pillar System Versioning Manager (model_version, prompt_version, schema_version, source_version)
- Admin Inspection Service
- Admin Control Service enforcing PDF Curriculum Immutability
"""

from .audit_models import (
    AdminControlAction,
    AuditEventType,
    AuditLogRecord,
    GenerationTraceRecord,
    SystemVersionManifest,
)
from .admin_control_service import AdminControlService
from .admin_inspection_service import AdminInspectionService
from .audit_logger import AuditLogger
from .generation_trace_engine import GenerationTraceEngine
from .system_versioning_manager import SystemVersioningManager

__all__ = [
    "AuditEventType",
    "AdminControlAction",
    "SystemVersionManifest",
    "GenerationTraceRecord",
    "AuditLogRecord",
    "SystemVersioningManager",
    "GenerationTraceEngine",
    "AuditLogger",
    "AdminInspectionService",
    "AdminControlService",
]
