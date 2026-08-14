# backend/learner/learner_service.py
"""
ROLE: LEARNER SERVICE

Provides the primary read interface for retrieving a learner's knowledge snapshot,
active error patterns, and review-due targets.
Composes repository data for downstream services.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.learner.knowledge_models import (
    GrammarKnowledgeState,
    LearnerErrorPattern,
    LearningStatus,
    VocabularyKnowledgeState,
)
from backend.learner.learner_repository import LearnerRepository


class LearnerService:
    """
    Service layer providing read access to learner knowledge snapshots and history.
    """

    def __init__(self, repository: Optional[LearnerRepository] = None):
        self.repository = repository or LearnerRepository()

    def get_grammar_state(self, learner_id: str, learning_object_id: str) -> Optional[GrammarKnowledgeState]:
        return self.repository.get_grammar_state(learner_id, learning_object_id)

    def get_vocabulary_state(self, learner_id: str, key_id: str) -> Optional[VocabularyKnowledgeState]:
        return self.repository.get_vocabulary_state(learner_id, key_id)

    def get_active_errors(self, learner_id: str) -> List[LearnerErrorPattern]:
        return self.repository.get_error_patterns(learner_id, active_only=True)

    def get_review_due_items(self, learner_id: str) -> Dict[str, List[Any]]:
        now = datetime.now(timezone.utc)

        grammar_due = [
            g for g in self.repository.get_all_grammar_states(learner_id)
            if (g.review_due_at and g.review_due_at <= now) or g.status == LearningStatus.review_due
        ]

        vocab_due = [
            v for v in self.repository.get_all_vocabulary_states(learner_id)
            if (v.review_due_at and v.review_due_at <= now) or v.status == LearningStatus.review_due
        ]

        return {
            "grammar": grammar_due,
            "vocabulary": vocab_due,
        }

    def get_learner_snapshot(self, learner_id: str) -> Dict[str, Any]:
        grammar_states = self.repository.get_all_grammar_states(learner_id)
        vocab_states = self.repository.get_all_vocabulary_states(learner_id)
        active_errors = self.get_active_errors(learner_id)
        review_due = self.get_review_due_items(learner_id)

        return {
            "learner_id": learner_id,
            "total_grammar_items": len(grammar_states),
            "mastered_grammar_count": sum(1 for g in grammar_states if g.status == LearningStatus.mastered),
            "total_vocabulary_items": len(vocab_states),
            "mastered_vocabulary_count": sum(1 for v in vocab_states if v.status == LearningStatus.mastered),
            "active_error_count": len(active_errors),
            "review_due_count": len(review_due["grammar"]) + len(review_due["vocabulary"]),
            "grammar_states": grammar_states,
            "vocabulary_states": vocab_states,
            "active_errors": active_errors,
        }
