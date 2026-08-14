# backend/intelligence/advanced_mastery_service.py
"""
ROLE: ADVANCED MASTERY SERVICE

Accumulates evaluation evidence over time to update 4-dimension knowledge models:
Grammar: understanding, controlled_use, production, stability
Vocabulary: recognition, recall, usage, stability

Uses historical evidence trajectory rather than single-answer state mutation.
"""

import logging
from datetime import datetime, timezone
from typing import Optional
from backend.intelligence.spaced_repetition_engine import SpacedRepetitionEngine
from backend.learner.knowledge_models import GrammarKnowledgeState, VocabularyKnowledgeState

logger = logging.getLogger(__name__)


class AdvancedMasteryService:
    """
    Updates 4-dimensional mastery states using accumulated historical evidence trajectories.
    """

    def __init__(self, srs_engine: Optional[SpacedRepetitionEngine] = None):
        self.srs_engine = srs_engine or SpacedRepetitionEngine()

    def process_grammar_evidence(
        self,
        state: GrammarKnowledgeState,
        activity_type: str,
        is_correct: bool,
        score: float = 1.0,
    ) -> GrammarKnowledgeState:
        """
        Updates 4-dimension Grammar state (understanding, controlled_use, production, stability).
        """
        now = datetime.now(timezone.utc)
        state.attempt_count += 1
        state.last_seen_at = now
        state.last_practiced_at = now

        if is_correct:
            state.correct_count += 1
            state.consecutive_correct += 1
            state.consecutive_incorrect = 0
            state.last_correct_at = now
            delta = 0.08 * score
        else:
            state.incorrect_count += 1
            state.consecutive_incorrect += 1
            state.consecutive_correct = 0
            state.last_incorrect_at = now
            delta = -0.10

        # Activity-type dimension targeted updates
        act_lower = activity_type.lower()
        if "explanation" in act_lower or "recognition" in act_lower:
            state.understanding = self._clamp(state.understanding + delta)
        elif "practice" in act_lower or "choice" in act_lower or "fill" in act_lower:
            state.controlled_use = self._clamp(state.controlled_use + delta)
            state.understanding = self._clamp(state.understanding + delta * 0.5)
        elif "production" in act_lower or "writing" in act_lower or "speaking" in act_lower:
            state.production = self._clamp(state.production + delta)
            state.controlled_use = self._clamp(state.controlled_use + delta * 0.5)
        else:
            state.controlled_use = self._clamp(state.controlled_use + delta)

        # Update Spaced Repetition Stability & Review Due Timestamp
        last_prac = state.last_practiced_at or now
        new_stability, lapses, _, review_due_at = self.srs_engine.compute_next_schedule(
            current_stability=state.stability,
            is_correct=is_correct,
            overall_mastery=state.overall_mastery,
            consecutive_correct=state.consecutive_correct,
            consecutive_incorrect=state.consecutive_incorrect,
            lapses=0,
            last_practiced_at=last_prac,
        )

        state.stability = new_stability
        state.review_due_at = review_due_at
        state.mastery_updated_at = now

        return state

    def process_vocabulary_evidence(
        self,
        state: VocabularyKnowledgeState,
        activity_type: str,
        is_correct: bool,
        score: float = 1.0,
    ) -> VocabularyKnowledgeState:
        """
        Updates 4-dimension Vocabulary state (recognition, recall, usage, stability).
        """
        now = datetime.now(timezone.utc)
        state.attempt_count += 1
        state.last_seen_at = now
        state.last_practiced_at = now

        if is_correct:
            state.correct_count += 1
            state.consecutive_correct += 1
            state.consecutive_incorrect = 0
            state.last_correct_at = now
            delta = 0.08 * score
        else:
            state.incorrect_count += 1
            state.consecutive_incorrect += 1
            state.consecutive_correct = 0
            state.last_incorrect_at = now
            delta = -0.10

        act_lower = activity_type.lower()
        if "recognition" in act_lower or "multiple" in act_lower:
            state.recognition = self._clamp(state.recognition + delta)
        elif "recall" in act_lower or "flashcard" in act_lower:
            state.recall = self._clamp(state.recall + delta)
            state.recognition = self._clamp(state.recognition + delta * 0.5)
        elif "usage" in act_lower or "writing" in act_lower or "speaking" in act_lower or "sentence" in act_lower:
            state.usage = self._clamp(state.usage + delta)
            state.recall = self._clamp(state.recall + delta * 0.5)
        else:
            state.recognition = self._clamp(state.recognition + delta)

        last_prac = state.last_practiced_at or now
        new_stability, lapses, _, review_due_at = self.srs_engine.compute_next_schedule(
            current_stability=state.stability,
            is_correct=is_correct,
            overall_mastery=state.overall_mastery,
            consecutive_correct=state.consecutive_correct,
            consecutive_incorrect=state.consecutive_incorrect,
            lapses=0,
            last_practiced_at=last_prac,
        )

        state.stability = new_stability
        state.review_due_at = review_due_at
        state.mastery_updated_at = now

        return state

    def _clamp(self, val: float) -> float:
        return round(max(0.0, min(1.0, val)), 4)
