# backend/intelligence/personalization_service.py
"""
ROLE: PERSONALIZATION & RECOMMENDATION ENGINE

Ranks pre-authorized learning opportunities for a learner using:
- mastery states
- active error patterns
- review urgency (Spaced Repetition due state)
- practice history
- course completion status
- learner preferences

CORE RULE: Never invent Curriculum. Only ranks pre-authorized items.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.curriculum import CurriculumService
from backend.learner import ErrorTracker, LearnerRepository

logger = logging.getLogger(__name__)


class PersonalizationService:
    """
    Ranks authorized learning opportunities using multi-factor personalization weights.
    """

    def __init__(
        self,
        repository: Optional[LearnerRepository] = None,
        error_tracker: Optional[ErrorTracker] = None,
        curriculum_service: Optional[CurriculumService] = None,
    ):
        self.repository = repository or LearnerRepository()
        self.error_tracker = error_tracker or ErrorTracker(repository=self.repository)
        self.curriculum_service = curriculum_service or CurriculumService()

    def rank_learning_opportunities(
        self,
        learner_id: str,
        candidate_target_ids: List[str],
        preferences: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Ranks candidate target IDs using accumulated evidence and preference metadata.
        """
        now = datetime.now(timezone.utc)
        pref_focus = (preferences or {}).get("focus_type", "").lower()

        active_errors = {e.target_learning_object_id: e for e in self.repository.get_error_patterns(learner_id, active_only=True)}
        grammar_states = {g.source_item_id: g for g in self.repository.get_all_grammar_states(learner_id)}
        vocab_states = {v.vocabulary_source_item_id: v for v in self.repository.get_all_vocabulary_states(learner_id)}


        ranked_items: List[Dict[str, Any]] = []

        for target_id in candidate_target_ids:
            g_state = grammar_states.get(target_id)
            v_state = vocab_states.get(target_id)

            mastery = 0.0
            is_review_due = False
            if g_state:
                mastery = g_state.overall_mastery
                if g_state.review_due_at and g_state.review_due_at <= now:
                    is_review_due = True
            elif v_state:
                mastery = v_state.overall_mastery
                if v_state.review_due_at and v_state.review_due_at <= now:
                    is_review_due = True

            # Factor 1: Error Boost (0.0 to 1.0)
            error_obj = active_errors.get(target_id)
            error_boost = min(1.0, error_obj.error_count * 0.3) if error_obj else 0.0

            # Factor 2: Review Due Boost (1.0 if review due, else 0.0)
            review_boost = 1.0 if is_review_due else 0.0

            # Factor 3: Mastery Gap (1.0 - mastery)
            mastery_gap = max(0.0, 1.0 - mastery)

            # Factor 4: Preference Bonus
            pref_bonus = 0.2 if pref_focus and (
                ("grammar" in pref_focus and g_state) or ("vocab" in pref_focus and v_state)
            ) else 0.0

            # Composite Priority Calculation
            priority_score = round(
                0.35 * error_boost + 0.30 * review_boost + 0.25 * mastery_gap + 0.10 * pref_bonus,
                4,
            )

            ranked_items.append({
                "target_id": target_id,
                "priority_score": priority_score,
                "overall_mastery": mastery,
                "is_review_due": is_review_due,
                "has_active_error": target_id in active_errors,
            })

        # Sort descending by priority_score
        ranked_items.sort(key=lambda x: x["priority_score"], reverse=True)
        return ranked_items
