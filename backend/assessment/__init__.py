# backend/assessment/__init__.py
"""
ROLE: ASSESSMENT SYSTEM PACKAGE

Provides complete Assessment architecture including:
- Placement Test Engine & starting position recommendation
- Diagnostic Assessment Engine across 5 dimensions (Grammar, Vocab Recognition, Recall, Usage, Sense)
- Topic, Unit, and Cumulative Checkpoints
- Level Assessment Engine (A1-C2) with readiness recommendations (No official CEFR certification claims)
- Server-side authoritative assessment evaluation & security
"""

from .assessment_models import (
    AssessmentType,
    DiagnosticDimension,
    ReadinessRecommendation,
    AssessmentQuestion,
    AssessmentSubmission,
    AssessmentSession,
    PlacementResult,
    DiagnosticReport,
    CheckpointResult,
    LevelAssessmentReport,
)
from .assessment_repository import AssessmentRepository
from .placement_service import PlacementService
from .diagnostic_service import DiagnosticService
from .checkpoint_service import CheckpointService
from .level_assessment_service import LevelAssessmentService

__all__ = [
    "AssessmentType",
    "DiagnosticDimension",
    "ReadinessRecommendation",
    "AssessmentQuestion",
    "AssessmentSubmission",
    "AssessmentSession",
    "PlacementResult",
    "DiagnosticReport",
    "CheckpointResult",
    "LevelAssessmentReport",
    "AssessmentRepository",
    "PlacementService",
    "DiagnosticService",
    "CheckpointService",
    "LevelAssessmentService",
]
