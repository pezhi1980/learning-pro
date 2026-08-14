# backend/learner/review_service.py
"""
ROLE: REVIEW SERVICE

Determines which already-authorized curriculum items are due for review for a given learner.
Calculates review priority based on stability, mastery, time since last practice, and active error patterns.
Review Service NEVER authorizes new curriculum.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.learner.knowledge_models import LearningStatus
from backend.learner.learner_repository import LearnerRepository


class ReviewService:
    """
    Schedules and retrieves review-due items for learners.
    """

    def __init__(self, repository: Optional[LearnerRepository] = None):
        self.repository = repository or LearnerRepository()

    def get_review_due_targets(self, learner_id: str, max_items: int = 5) -> Dict[str, List[Any]]:
        now = datetime.now(timezone.utc)

        # 1. Retrieve Grammar review candidates
        grammar_states = self.repository.get_all_grammar_states(learner_id)
        grammar_due = [
            g for g in grammar_states
            if (g.review_due_at and g.review_due_at <= now) or g.status in (LearningStatus.review_due, LearningStatus.learning)
        ]
        # Sort by urgency: lowest stability first, then lowest overall_mastery
        grammar_due.sort(key=lambda g: (g.stability, g.overall_mastery))

        # 2. Retrieve Vocabulary review candidates
        vocab_states = self.repository.get_all_vocabulary_states(learner_id)
        vocab_due = [
            v for v in vocab_states
            if (v.review_due_at and v.review_due_at <= now) or v.status in (LearningStatus.review_due, LearningStatus.learning)
        ]
        vocab_due.sort(key=lambda v: (v.stability, v.overall_mastery))

        return {
            "grammar": grammar_due[:max_items],
            "vocabulary": vocab_due[:max_items],
        }
