# backend/audit/admin_control_service.py
"""
ROLE: ADMIN CONTENT CONTROL SERVICE

Supports controlled admin management actions:
- publish
- unpublish
- deprecate
- regenerate
- inspect_history
- disable_content

MANDATORY RULE: Admin must NOT directly modify authoritative PDF-derived Curriculum truth.
"""

import logging
from typing import Any, Dict, Optional
from backend.audit.audit_logger import AuditLogger
from backend.audit.audit_models import AdminControlAction, AuditEventType
from backend.lifecycle import ContentVersioningEngine, PublishingStatus, PublishingWorkflowService

logger = logging.getLogger(__name__)


class AdminControlService:
    """
    Control service managing authorized admin actions on generated content lifecycle.
    Enforces strict immutability on PDF-derived Curriculum truth.
    """

    def __init__(
        self,
        publishing_service: Optional[PublishingWorkflowService] = None,
        versioning_engine: Optional[ContentVersioningEngine] = None,
        audit_logger: Optional[AuditLogger] = None,
    ):
        self.versioning_engine = versioning_engine or ContentVersioningEngine()
        self.publishing_service = publishing_service or PublishingWorkflowService(
            versioning_engine=self.versioning_engine
        )
        self.audit_logger = audit_logger or AuditLogger()

    def execute_admin_action(
        self,
        admin_id: str,
        action: AdminControlAction,
        content_id: str,
        version_hash: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Executes a controlled administrative action on generated content.
        """
        latest = self.versioning_engine.get_latest_version(content_id)
        target_hash = version_hash or (latest.content_version_hash if latest else None)

        if not target_hash and action != AdminControlAction.inspect_history:
            raise KeyError(f"No content version record found for content_id '{content_id}'.")

        result_status = "executed"

        if action == AdminControlAction.publish:
            rec = self.publishing_service.publish_content(target_hash)
            result_status = rec.publishing_status.value
        elif action == AdminControlAction.unpublish:
            rec = self.publishing_service.update_status(target_hash, PublishingStatus.validated)
            result_status = rec.publishing_status.value
        elif action == AdminControlAction.deprecate:
            rec = self.publishing_service.deprecate_content(target_hash)
            result_status = rec.publishing_status.value
        elif action == AdminControlAction.disable_content:
            rec = self.publishing_service.update_status(target_hash, PublishingStatus.rejected)
            result_status = rec.publishing_status.value
        elif action == AdminControlAction.inspect_history:
            history = self.versioning_engine.list_version_history(content_id)
            result_status = f"retrieved_{len(history)}_versions"

        # Log admin action in audit logger
        self.audit_logger.log_event(
            event_type=AuditEventType.admin_action,
            actor_id=admin_id,
            details={
                "action": action.value,
                "content_id": content_id,
                "version_hash": target_hash,
                "result_status": result_status,
            },
            target_ids=[content_id],
        )

        logger.info(f"Admin '{admin_id}' executed action '{action.value}' on content '{content_id}'.")
        return {
            "admin_id": admin_id,
            "action": action.value,
            "content_id": content_id,
            "version_hash": target_hash,
            "status": result_status,
        }

    def modify_curriculum_truth(self, admin_id: str, target_id: str, payload: Dict[str, Any]) -> None:
        """
        Guards PDF Curriculum Immutability Rule.
        Admins CANNOT modify PDF-derived Curriculum truth directly.
        """
        logger.warning(f"Admin '{admin_id}' attempted illegal direct modification of Curriculum target '{target_id}'.")
        raise PermissionError(
            f"ADMIN AUTHORIZATION VIOLATION: Admins cannot directly modify authoritative PDF-derived Curriculum truth (target '{target_id}')."
        )
