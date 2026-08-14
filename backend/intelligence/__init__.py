# backend/intelligence/__init__.py
"""
ROLE: ADVANCED LEARNING INTELLIGENCE PACKAGE

Provides adaptive learning intelligence infrastructure:
- Evidence-Based Spaced Repetition Engine
- 4-Dimensional Advanced Mastery Trajectory Service
- Curriculum Knowledge Graph Architecture
- Personalized Opportunity Ranking Engine
- Cognitive Load & Novelty Control Service
"""

from .spaced_repetition_engine import SpacedRepetitionEngine
from .advanced_mastery_service import AdvancedMasteryService
from .knowledge_graph_service import KnowledgeGraphService, RelationshipType, KnowledgeEdge
from .personalization_service import PersonalizationService
from .novelty_control_service import NoveltyControlService

__all__ = [
    "SpacedRepetitionEngine",
    "AdvancedMasteryService",
    "KnowledgeGraphService",
    "RelationshipType",
    "KnowledgeEdge",
    "PersonalizationService",
    "NoveltyControlService",
]
