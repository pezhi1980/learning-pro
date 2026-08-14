# backend/audit/audit_logger.py
"""
ROLE: AUDIT LOGGER

System-wide audit logging repository recording events across 8 event types:
generation, validation, publication, deprecation, target_selection, evaluation, mastery_update, admin_action.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.audit.audit_models import AuditEventType, AuditLogRecord

logger = logging.getLogger(__name__)


class AuditLogger:
    """
    Repository for system-wide immutable audit logging.
    """

    def __init__(self):
        self._logs: List[AuditLogRecord] = []

    def log_event(
        self,
        event_type: AuditEventType,
        actor_id: str = "system",
        details: Optional[Dict[str, Any]] = None,
        target_ids: Optional[List[str]] = None,
    ) -> AuditLogRecord:
        now = datetime.now(timezone.utc)
        log_id = f"audit:{event_type.value}:{int(now.timestamp())}:{len(self._logs) + 1}"

        record = AuditLogRecord(
            log_id=log_id,
            event_type=event_type,
            actor_id=actor_id,
            details=details or {},
            target_ids=target_ids or [],
            created_at=now,
        )

        self._logs.append(record)
        logger.info(f"Audit log recorded [{event_type.value}] by '{actor_id}' (id={log_id}).")
        return record

    def get_logs(
        self, event_type: Optional[AuditEventType] = None, limit: int = 50
    ) -> List[AuditLogRecord]:
        if event_type:
            filtered = [l for l in self._logs if l.event_type == event_type]
            return filtered[-limit:]
        return self._logs[-limit:]
