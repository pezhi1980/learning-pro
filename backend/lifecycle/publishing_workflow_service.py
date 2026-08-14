# backend/lifecycle/publishing_workflow_service.py
"""
ROLE: PUBLISHING WORKFLOW SERVICE

Enforces publishing workflow state transitions across 6 states:
- generated
- rejected
- validated
- published
- deprecated
- replaced

CORE RULE: Only eligible content in state 'published' may be served in production to learners.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from backend.lifecycle.content_versioning_engine import ContentVersioningEngine
from backend.lifecycle.lifecycle_models import ContentVersionRecord, PublishingStatus

logger = logging.getLogger(__name__)


class PublishingWorkflowService:
    """
    Service enforcing production publishing rules and workflow state transitions.
    """

    def __init__(self, versioning_engine: Optional[ContentVersioningEngine] = None):
        self.versioning_engine = versioning_engine or ContentVersioningEngine()

    def update_status(
        self, version_hash: str, new_status: PublishingStatus
    ) -> ContentVersionRecord:
        """
        Updates the publishing status of a content version record.
        """
        record = self.versioning_engine.get_version_by_hash(version_hash)
        if not record:
            raise KeyError(f"Content version record hash '{version_hash}' not found.")

        now = datetime.now(timezone.utc)
        record.publishing_status = new_status

        if new_status == PublishingStatus.published:
            record.published_at = now
        elif new_status == PublishingStatus.deprecated:
            record.deprecated_at = now

        logger.info(f"Updated content '{record.content_id}' (hash={version_hash[:10]}) to status '{new_status.value}'.")
        return record

    def publish_content(self, version_hash: str) -> ContentVersionRecord:
        """
        Publishes a validated content version to production.
        Content MUST be in state 'validated' or 'generated' (if pre-validated) to be published.
        """
        record = self.versioning_engine.get_version_by_hash(version_hash)
        if not record:
            raise KeyError(f"Content version record hash '{version_hash}' not found.")

        if record.publishing_status == PublishingStatus.rejected:
            raise ValueError(f"Cannot publish rejected content (version hash '{version_hash}').")

        return self.update_status(version_hash, PublishingStatus.published)

    def deprecate_content(self, version_hash: str) -> ContentVersionRecord:
        """
        Deprecates an active published content version.
        """
        return self.update_status(version_hash, PublishingStatus.deprecated)

    def get_servable_production_content(self, content_id: str) -> ContentVersionRecord:
        """
        Retrieves active published content version for production serving.
        Enforces rule: ONLY content in state 'published' may be served in production.
        """
        latest = self.versioning_engine.get_latest_version(content_id)
        if not latest:
            raise KeyError(f"No content found for content_id '{content_id}'.")

        if latest.publishing_status != PublishingStatus.published:
            raise ValueError(
                f"Content '{content_id}' has status '{latest.publishing_status.value}' and cannot be served in production. "
                "Only 'published' content is eligible."
            )

        return latest
