# backend/learning/target_selection_service.py
"""
ROLE: TARGET SELECTION SERVICE

Selects authorized curriculum targets for a learner based on current knowledge state, review needs,
active error patterns, and PDF-backed curriculum sequence.
Enforces Novelty Budget (1 primary new learning target per activity segment).
Selection ONLY chooses authorized PDF curriculum items.
"""

from typing import List, Optional, Tuple
from backend.curriculum import CurriculumService
from backend.learner import LearnerService
from backend.learning.learning_config import LearningConfig


class TargetSelectionService:
    """
    Selects authorized target IDs from CurriculumService matching learner state and priority strategy.
    """

    def __init__(
        self,
        curriculum_service: Optional[CurriculumService] = None,
        learner_service: Optional[LearnerService] = None,
        config: Optional[LearningConfig] = None,
    ):
        self.curriculum_service = curriculum_service or CurriculumService()
        self.learner_service = learner_service or LearnerService()
        self.config = config or LearningConfig()

    def select_repair_target(self, learner_id: str) -> Optional[Tuple[str, str]]:
        """
        Selects an authorized target for repair based on active error patterns.
        Returns tuple of (target_type, target_id) or None.
        """
        active_errors = self.learner_service.get_active_errors(learner_id)
        if not active_errors:
            return None

        # Sort errors by severity score descending
        sorted_errors = sorted(active_errors, key=lambda e: e.severity_score, reverse=True)
        top_err = sorted_errors[0]

        lo_id = top_err.target_learning_object_id
        if top_err.category == "grammar" or top_err.grammar_code:
            if self.curriculum_service.get_grammar_by_id(lo_id) or self.curriculum_service.grammar_exists(top_err.grammar_code or ""):
                return "grammar", lo_id
        elif top_err.category in ("vocabulary", "sense_confusion") or top_err.vocabulary_sense_id:
            s_id = top_err.vocabulary_sense_id or lo_id
            if self.curriculum_service.get_vocabulary_by_id(s_id.replace(":sense", "")):
                return "vocabulary", s_id

        return None

    def select_review_targets(self, learner_id: str) -> Tuple[List[str], List[str]]:
        """
        Selects already-authorized targets due for review.
        Returns tuple of ([grammar_ids], [vocab_ids]).
        """
        review_due = self.learner_service.get_review_due_items(learner_id)

        grammar_ids = [
            g.learning_object_id for g in review_due["grammar"][:self.config.max_review_targets_per_session]
        ]
        vocab_ids = [
            v.vocabulary_sense_id or v.learning_object_id for v in review_due["vocabulary"][:self.config.max_review_targets_per_session]
        ]

        return grammar_ids, vocab_ids

    def select_next_new_grammar_target(self, learner_id: str, level: str = "A1") -> Optional[str]:
        """
        Selects the next unstudied, authorized Grammar target from PDF source sequence.
        """
        snapshot = self.learner_service.get_learner_snapshot(learner_id)
        studied_lo_ids = {g.learning_object_id for g in snapshot["grammar_states"]}

        # Query CurriculumService for authorized PDF grammar sequence
        all_grammar = self.curriculum_service.list_all_grammar()
        level_grammar = [g for g in all_grammar if g.document_level == level]

        for g_item in level_grammar:
            if g_item.source_item_id not in studied_lo_ids:
                return g_item.source_item_id

        # Fallback to any unstudied level item if level is exhausted
        for g_item in all_grammar:
            if g_item.source_item_id not in studied_lo_ids:
                return g_item.source_item_id

        return None

    def select_next_new_vocabulary_target(self, learner_id: str, level: str = "A1") -> Optional[str]:
        """
        Selects the next unstudied, authorized Vocabulary target/sense from PDF source sequence.
        """
        snapshot = self.learner_service.get_learner_snapshot(learner_id)
        studied_keys = {
            v.vocabulary_sense_id or v.learning_object_id for v in snapshot["vocabulary_states"]
        }

        all_vocab = self.curriculum_service.list_all_vocabulary()
        level_vocab = [v for v in all_vocab if v.document_level == level]

        for v_item in level_vocab:
            key = f"{v_item.source_item_id}:sense" if v_item.guideword else v_item.source_item_id
            if key not in studied_keys:
                return key

        for v_item in all_vocab:
            key = f"{v_item.source_item_id}:sense" if v_item.guideword else v_item.source_item_id
            if key not in studied_keys:
                return key

        return None

    def select_known_supporting_content(self, learner_id: str) -> Tuple[List[str], List[str]]:
        """
        Selects learner-known Grammar Codes and Vocabulary Items to serve as supporting allowed content.
        Preserves GRAMMAR COMPLEXITY != VOCABULARY COMPLEXITY.
        """
        snapshot = self.learner_service.get_learner_snapshot(learner_id)

        known_grammar_codes = [
            g.grammar_code for g in snapshot["grammar_states"] if g.overall_mastery >= 0.5
        ][:self.config.max_supporting_allowed_items]

        known_vocab_items = [
            v.lexeme for v in snapshot["vocabulary_states"] if v.overall_mastery >= 0.5
        ][:self.config.max_supporting_allowed_items]

        return known_grammar_codes, known_vocab_items
