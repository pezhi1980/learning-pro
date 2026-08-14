# backend/audit/generation_trace_engine.py
"""
ROLE: GENERATION TRACE ENGINE

Records and retrieves full end-to-end generation traces connecting requests to:
assigned_targets, allowed_targets, model, model_version, prompt_version, schema_version, source_version_hash, validator_results, and content_version_hash.
"""

import logging
from typing import Any, Dict, List, Optional
from backend.audit.audit_models import GenerationTraceRecord
from backend.audit.system_versioning_manager import SystemVersioningManager

logger = logging.getLogger(__name__)


class GenerationTraceEngine:
    """
    Engine maintaining end-to-end generation trace records.
    """

    def __init__(self, versioning_manager: Optional[SystemVersioningManager] = None):
        self.versioning_manager = versioning_manager or SystemVersioningManager()
        self._traces: Dict[str, GenerationTraceRecord] = {}

    def record_trace(
        self,
        request_id: str,
        assigned_targets: List[str],
        allowed_targets: List[str],
        validator_results: Dict[str, Any],
        content_version_hash: Optional[str] = None,
    ) -> GenerationTraceRecord:
        manifest = self.versioning_manager.get_active_manifest()

        record = GenerationTraceRecord(
            request_id=request_id,
            assigned_targets=assigned_targets,
            allowed_targets=allowed_targets,
            model=manifest.model_name,
            model_version=manifest.model_version,
            prompt_version=manifest.prompt_version,
            schema_version=manifest.schema_version,
            source_version_hash=manifest.source_version_hash,
            validator_results=validator_results,
            content_version_hash=content_version_hash,
        )

        self._traces[request_id] = record
        logger.info(f"Recorded generation trace for request '{request_id}'.")
        return record

    def get_trace(self, request_id: str) -> Optional[GenerationTraceRecord]:
        return self._traces.get(request_id)
