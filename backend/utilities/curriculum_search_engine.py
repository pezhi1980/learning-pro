# backend/utilities/curriculum_search_engine.py
"""
ROLE: AUTHORIZED CURRICULUM SEARCH ENGINE

Performs search over authorized PDF-derived Grammar and Vocabulary items in CurriculumService.
MANDATORY RULE: Search MUST NEVER fabricate Curriculum items. Only queries official CurriculumService targets.
"""

import logging
from typing import List, Optional
from backend.curriculum import CurriculumService
from backend.utilities.utility_models import SearchResultItem

logger = logging.getLogger(__name__)


class CurriculumSearchEngine:
    """
    Search engine over authorized PDF-backed CurriculumService targets.
    """

    def __init__(self, curriculum_service: Optional[CurriculumService] = None):
        self.curriculum_service = curriculum_service or CurriculumService()

    def search_curriculum(
        self,
        query: str,
        level: Optional[str] = None,
        target_type: Optional[str] = None,
    ) -> List[SearchResultItem]:
        """
        Searches authorized Grammar and Vocabulary source items.
        """
        clean_query = query.strip().lower()
        if not clean_query:
            return []

        results: List[SearchResultItem] = []

        # 1. Search Grammar Items
        if target_type in [None, "grammar"]:
            for item in self.curriculum_service.list_all_grammar():
                item_level = item.document_level or ""
                if level and item_level.upper() != level.upper():
                    continue

                searchable_text = f"{item.grammar_code} {item.label} {item.source_item_id} {item.raw_text or ''}".lower()
                if clean_query in searchable_text:
                    results.append(
                        SearchResultItem(
                            target_id=item.grammar_code,
                            target_type="grammar",
                            title=item.label or item.grammar_code,
                            level=item_level,
                            topic=item.grammar_code,
                            details={"label": item.label, "code": item.grammar_code},
                            match_score=1.0,
                        )
                    )

        # 2. Search Vocabulary Items
        if target_type in [None, "vocabulary"]:
            for item in self.curriculum_service.vocab_repo.list_all():
                item_level = item.document_level or ""
                if level and item_level.upper() != level.upper():
                    continue

                searchable_text = f"{item.lexeme} {item.guideword or ''} {item.raw_text or ''}".lower()
                if clean_query in searchable_text:
                    v_target_id = f"vocab:{item.lexeme}:{item.guideword or ''}"
                    results.append(
                        SearchResultItem(
                            target_id=v_target_id,
                            target_type="vocabulary",
                            title=f"{item.lexeme} ({item.guideword})" if item.guideword else item.lexeme,
                            level=item_level,
                            topic="vocabulary",
                            details={"lexeme": item.lexeme, "guideword": item.guideword, "part_of_speech": item.part_of_speech},
                            match_score=1.0,
                        )
                    )



        logger.info(f"Curriculum search for '{query}' returned {len(results)} authorized items.")
        return results
