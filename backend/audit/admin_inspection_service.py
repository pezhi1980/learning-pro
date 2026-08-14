# backend/audit/admin_inspection_service.py
"""
ROLE: ADMIN CONTENT INSPECTION SERVICE

Provides administrative inspection access to:
- Curriculum source items
- Grammar codes
- Vocabulary items & senses
- Lessons, examples, and exercises
- Validator results & rejection reasons
- Content versions & generation traces
"""

import logging
from typing import Any, Dict, Optional
from backend.audit.generation_trace_engine import GenerationTraceEngine
from backend.curriculum import CurriculumService
from backend.lifecycle import ContentVersioningEngine

logger = logging.getLogger(__name__)


class AdminInspectionService:
    """
    Inspection service providing complete administrative visibility into curriculum and generated content.
    """

    def __init__(
        self,
        curriculum_service: Optional[CurriculumService] = None,
        versioning_engine: Optional[ContentVersioningEngine] = None,
        trace_engine: Optional[GenerationTraceEngine] = None,
    ):
        self.curriculum_service = curriculum_service or CurriculumService()
        self.versioning_engine = versioning_engine or ContentVersioningEngine()
        self.trace_engine = trace_engine or GenerationTraceEngine()

    def inspect_content_details(self, content_id: str) -> Dict[str, Any]:
        """
        Inspects content version history, payload, and status.
        """
        history = self.versioning_engine.list_version_history(content_id)
        if not history:
            raise KeyError(f"Content ID '{content_id}' not found.")

        latest = history[-1]
        return {
            "content_id": content_id,
            "version_count": len(history),
            "latest_version": latest.model_dump(),
            "all_versions": [h.model_dump() for h in history],
        }

    def inspect_curriculum_target(self, target_id: str) -> Dict[str, Any]:
        """
        Inspects authoritative Curriculum source item, grammar code, or vocabulary sense.
        """
        target = self.curriculum_service.resolve_target(target_id)
        if not target:
            raise KeyError(f"Curriculum target ID '{target_id}' not found.")
        return target.model_dump()

    def inspect_generation_trace(self, request_id: str) -> Dict[str, Any]:
        """
        Inspects complete generation trace for a request ID.
        """
        trace = self.trace_engine.get_trace(request_id)
        if not trace:
            raise KeyError(f"Generation trace for request_id '{request_id}' not found.")
        return trace.model_dump()
