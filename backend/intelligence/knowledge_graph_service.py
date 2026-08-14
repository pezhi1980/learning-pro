# backend/intelligence/knowledge_graph_service.py
"""
ROLE: KNOWLEDGE GRAPH SERVICE

Manages semantic relationship graph connecting Curriculum targets:
- prerequisite (target A must precede target B)
- builds_on (target B expands target A)
- related (shared domain context)
- contrasts_with (contrasting target concepts)
- repair_for (foundation repair target for errors)

CORE RULE: Do not automatically accept AI-generated relationships as authoritative without verification.
"""

import logging
from enum import Enum
from typing import Dict, List, Optional, Set
from pydantic import BaseModel, Field
from backend.curriculum import CurriculumService

logger = logging.getLogger(__name__)


class RelationshipType(str, Enum):
    prerequisite = "prerequisite"
    builds_on = "builds_on"
    related = "related"
    contrasts_with = "contrasts_with"
    repair_for = "repair_for"


class KnowledgeEdge(BaseModel):
    source_id: str
    target_id: str
    relationship: RelationshipType
    verified: bool = True


class KnowledgeGraphService:
    """
    Service managing curriculum graph relationships and dependency validation.
    """

    def __init__(self, curriculum_service: Optional[CurriculumService] = None):
        self.curriculum_service = curriculum_service or CurriculumService()
        self._edges: List[KnowledgeEdge] = []
        self._seed_default_graph()

    def _seed_default_graph(self):
        """
        Populates foundational verified relationship edges for A1-A2 targets.
        """
        # Example verified relationships
        self.add_edge("g_be_present", "g_personal_pronouns", RelationshipType.prerequisite, verified=True)
        self.add_edge("g_present_simple", "g_be_present", RelationshipType.builds_on, verified=True)
        self.add_edge("g_present_simple", "g_present_continuous", RelationshipType.contrasts_with, verified=True)

    def add_edge(
        self, source_id: str, target_id: str, relationship: RelationshipType, verified: bool = True
    ) -> Optional[KnowledgeEdge]:
        """
        Adds a graph edge between source and target targets if validated.
        """
        if not verified:
            logger.warning(f"Unverified relationship edge between {source_id} -> {target_id} rejected.")
            return None

        edge = KnowledgeEdge(
            source_id=source_id,
            target_id=target_id,
            relationship=relationship,
            verified=verified,
        )
        self._edges.append(edge)
        return edge

    def get_prerequisites(self, target_id: str) -> List[str]:
        """
        Returns prerequisite target IDs required before attempting target_id.
        """
        return [
            e.source_id for e in self._edges
            if e.target_id == target_id and e.relationship == RelationshipType.prerequisite and e.verified
        ]

    def get_repair_targets(self, target_id: str) -> List[str]:
        """
        Returns foundational repair target IDs for error remediation.
        """
        return [
            e.source_id for e in self._edges
            if e.target_id == target_id and e.relationship == RelationshipType.repair_for and e.verified
        ]

    def get_related_targets(self, target_id: str) -> List[str]:
        """
        Returns related or contrasting target IDs.
        """
        return [
            e.target_id if e.source_id == target_id else e.source_id
            for e in self._edges
            if (e.source_id == target_id or e.target_id == target_id)
            and e.relationship in (RelationshipType.related, RelationshipType.contrasts_with)
            and e.verified
        ]

    def list_edges(self) -> List[KnowledgeEdge]:
        return [e for e in self._edges if e.verified]
