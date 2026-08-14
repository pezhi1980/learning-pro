# backend/security/authorization_service.py
"""
ROLE: AUTHORIZATION & RESOURCE OWNERSHIP GUARD

Enforces strict resource ownership boundaries across all learner resources:
learner state, lessons, sessions, submissions, assessments, recordings, writing, progress, settings.

CORE RULE: Learner A must NEVER access Learner B's private resources.
"""

import logging
from backend.security.security_models import AccessControlContext

logger = logging.getLogger(__name__)


class AuthorizationService:
    """
    Service enforcing resource ownership boundaries and access permissions.
    """

    def authorize_resource_access(
        self,
        context: AccessControlContext,
        resource_owner_id: str,
        resource_type: str = "resource",
    ) -> None:
        """
        Guards resource ownership.
        Access granted ONLY if requester is the resource owner OR an authorized admin.
        """
        if context.is_admin:
            logger.info(f"Admin '{context.requester_id}' granted access to '{resource_type}' owned by '{resource_owner_id}'.")
            return

        if context.requester_id == resource_owner_id:
            return

        logger.warning(
            f"SECURITY VIOLATION: Learner '{context.requester_id}' attempted illegal access to '{resource_type}' owned by '{resource_owner_id}'."
        )
        raise PermissionError(
            f"RESOURCE OWNERSHIP VIOLATION: Learner '{context.requester_id}' is not authorized to access '{resource_type}' owned by Learner '{resource_owner_id}'."
        )
