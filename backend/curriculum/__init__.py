# backend/curriculum/__init__.py
"""
Curriculum Layer Package
────────────────────────
Authoritative Source of Truth for all English language learning curriculum data.
"""

from .curriculum_service import CurriculumService
from .grammar_repository import GrammarRepository, GrammarRepositoryError
from .source_models import (
    CurriculumSourceDocument,
    GrammarSourceItem,
    IngestionReport,
    VocabularySourceItem,
)
from .vocabulary_repository import VocabularyRepository, VocabularyRepositoryError

__all__ = [
    "CurriculumService",
    "GrammarRepository",
    "VocabularyRepository",
    "GrammarRepositoryError",
    "VocabularyRepositoryError",
    "CurriculumSourceDocument",
    "GrammarSourceItem",
    "VocabularySourceItem",
    "IngestionReport",
]
