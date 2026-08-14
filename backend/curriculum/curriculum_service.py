# backend/curriculum/curriculum_service.py
"""
ROLE: CURRICULUM ACCESS SERVICE

This module provides the single authoritative Backend interface to curriculum data.
It coordinates GrammarRepository and VocabularyRepository to provide read-only source queries.
"""

from typing import Any, Dict, List, Optional
from .grammar_repository import GrammarRepository
from .vocabulary_repository import VocabularyRepository
from .source_models import CurriculumSourceDocument, GrammarSourceItem, IngestionReport, VocabularySourceItem


class CurriculumService:
    """
    Authoritative Curriculum Access Service over Grammar and Vocabulary repositories.
    """

    def __init__(
        self,
        grammar_repository: Optional[GrammarRepository] = None,
        vocabulary_repository: Optional[VocabularyRepository] = None,
        search_directories: Optional[List[str]] = None,
    ):
        self.grammar_repo = grammar_repository or GrammarRepository(search_directories=search_directories)
        self.vocab_repo = vocabulary_repository or VocabularyRepository(search_directories=search_directories)

    # ── Grammar API ────────────────────────────────────────────────────────────

    def grammar_exists(self, code: str) -> bool:
        return self.grammar_repo.exists(code)

    def get_grammar_by_code(self, code: str) -> Optional[GrammarSourceItem]:
        return self.grammar_repo.get_by_code(code)

    def find_all_grammar_by_code(self, code: str) -> List[GrammarSourceItem]:
        return self.grammar_repo.find_all_by_code(code)

    def get_grammar_by_id(self, item_id: str) -> Optional[GrammarSourceItem]:
        return self.grammar_repo.get_by_id(item_id)

    def list_grammar_by_level(self, level: str) -> List[GrammarSourceItem]:
        return self.grammar_repo.list_by_level(level)

    def list_all_grammar(self) -> List[GrammarSourceItem]:
        return self.grammar_repo.list_all()

    # ── Vocabulary API ─────────────────────────────────────────────────────────

    def vocabulary_source_item_exists(self, item_id: str) -> bool:
        return self.vocab_repo.exists(item_id)

    def get_vocabulary_by_id(self, item_id: str) -> Optional[VocabularySourceItem]:
        return self.vocab_repo.get_by_id(item_id)

    def find_vocabulary_by_lexeme(self, lexeme: str) -> List[VocabularySourceItem]:
        return self.vocab_repo.find_by_lexeme(lexeme)

    def find_vocabulary_by_lexeme_and_guideword(self, lexeme: str, guideword: str) -> Optional[VocabularySourceItem]:
        return self.vocab_repo.find_by_lexeme_and_guideword(lexeme, guideword)

    def list_vocabulary_by_level(self, level: str) -> List[VocabularySourceItem]:
        return self.vocab_repo.list_by_level(level)

    def list_all_vocabulary(self) -> List[VocabularySourceItem]:
        return self.vocab_repo.list_all()

    # ── Source Documents & Diagnostic Completeness Report ─────────────────────

    def list_source_documents(self) -> List[CurriculumSourceDocument]:
        return self.grammar_repo.list_source_documents() + self.vocab_repo.list_source_documents()

    def get_source_document(self, source_id: str) -> Optional[CurriculumSourceDocument]:
        doc = self.grammar_repo.get_source_document(source_id)
        if doc:
            return doc
        return self.vocab_repo.get_source_document(source_id)

    def get_completeness_report(self) -> Dict[str, Any]:
        grammar_reports = self.grammar_repo.get_ingestion_reports()
        vocab_reports = self.vocab_repo.get_ingestion_reports()

        total_grammar_items = len(self.grammar_repo.list_all())
        total_vocab_items = len(self.vocab_repo.list_all())
        total_issues = sum(r.issue_count for r in grammar_reports + vocab_reports)

        return {
            "total_source_documents": len(grammar_reports) + len(vocab_reports),
            "total_grammar_items": total_grammar_items,
            "total_vocabulary_items": total_vocab_items,
            "total_issues": total_issues,
            "grammar_reports": [r.model_dump() for r in grammar_reports],
            "vocabulary_reports": [r.model_dump() for r in vocab_reports],
        }
