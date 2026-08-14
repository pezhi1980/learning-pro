# backend/audit/system_versioning_manager.py
"""
ROLE: SYSTEM VERSIONING MANAGER

Maintains explicit system-wide versioning metadata across 4 pillars:
- model_version
- prompt_version
- schema_version
- source_version
"""

import logging
from typing import Optional
from backend.audit.audit_models import SystemVersionManifest

logger = logging.getLogger(__name__)


class SystemVersioningManager:
    """
    Manager maintaining active system-wide version manifest.
    """

    def __init__(self, initial_manifest: Optional[SystemVersionManifest] = None):
        self._manifest = initial_manifest or SystemVersionManifest()

    def get_active_manifest(self) -> SystemVersionManifest:
        return self._manifest

    def update_versions(
        self,
        model_version: Optional[str] = None,
        prompt_version: Optional[str] = None,
        schema_version: Optional[str] = None,
        source_version_hash: Optional[str] = None,
    ) -> SystemVersionManifest:
        if model_version:
            self._manifest.model_version = model_version
        if prompt_version:
            self._manifest.prompt_version = prompt_version
        if schema_version:
            self._manifest.schema_version = schema_version
        if source_version_hash:
            self._manifest.source_version_hash = source_version_hash

        logger.info(f"System versioning manifest updated: {self._manifest.model_dump()}")
        return self._manifest
