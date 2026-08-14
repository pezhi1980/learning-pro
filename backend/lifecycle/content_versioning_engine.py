# backend/lifecycle/content_versioning_engine.py
"""
ROLE: CONTENT VERSIONING ENGINE

Manages immutable content versioning for lessons, explanations, examples, exercises, audio references, and generation metadata.
CORE RULE: Never silently overwrite historical validated content. Updating content creates a new version record (version_index += 1).
"""

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.lifecycle.lifecycle_models import ContentVersionRecord, PublishingStatus

logger = logging.getLogger(__name__)


class ContentVersioningEngine:
    """
    Engine maintaining immutable content version records and version history trajectories.
    """

    def __init__(self):
        self._versions_by_id: Dict[str, List[ContentVersionRecord]] = {}
        self._versions_by_hash: Dict[str, ContentVersionRecord] = {}

    def register_content_version(
        self,
        content_id: str,
        payload: Dict[str, Any],
        target_ids: Optional[List[str]] = None,
        initial_status: PublishingStatus = PublishingStatus.generated,
    ) -> ContentVersionRecord:
        """
        Registers a new immutable content version record.
        If a previous version exists, increments version_index and marks previous version as replaced.
        """
        now = datetime.now(timezone.utc)
        payload_str = json.dumps(payload, sort_keys=True)
        version_hash = hashlib.sha256(f"{content_id}:{payload_str}:{now.isoformat()}".encode("utf-8")).hexdigest()

        history = self._versions_by_id.get(content_id, [])
        version_index = len(history) + 1

        if history:
            prev_record = history[-1]
            prev_record.replaced_by_version_hash = version_hash
            if prev_record.publishing_status == PublishingStatus.published:
                prev_record.publishing_status = PublishingStatus.replaced
                prev_record.deprecated_at = now

        record = ContentVersionRecord(
            content_id=content_id,
            version_index=version_index,
            content_version_hash=version_hash,
            target_ids=target_ids or [],
            publishing_status=initial_status,
            created_at=now,
            content_payload=payload,
        )

        if content_id not in self._versions_by_id:
            self._versions_by_id[content_id] = []
        self._versions_by_id[content_id].append(record)
        self._versions_by_hash[version_hash] = record

        logger.info(f"Registered content '{content_id}' v{version_index} (hash={version_hash[:10]}).")
        return record

    def get_latest_version(self, content_id: str) -> Optional[ContentVersionRecord]:
        history = self._versions_by_id.get(content_id, [])
        return history[-1] if history else None

    def get_version_by_hash(self, content_version_hash: str) -> Optional[ContentVersionRecord]:
        return self._versions_by_hash.get(content_version_hash)

    def list_version_history(self, content_id: str) -> List[ContentVersionRecord]:
        return self._versions_by_id.get(content_id, [])
