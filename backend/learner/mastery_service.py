# backend/learner/mastery_service.py
"""
ROLE: MASTERY SERVICE

Consumes EvaluationResult objects and updates individual Grammar & Vocabulary mastery dimensions deterministically.
Implements bounded incremental updates (0.0 to 1.0) without allowing a single answer to jump an item to 1.0.
Preserves independence between Grammar & Vocabulary progress and between distinct Vocabulary Senses.
"""

from __future__ import annotations
from datetime import datetime, timedelta, timezone

from typing import TYPE_CHECKING, Optional
from backend.learner.knowledge_models import (
    GrammarKnowledgeState,
    VocabularyKnowledgeState,
)
from backend.learner.learner_repository import LearnerRepository

if TYPE_CHECKING:
    from backend.evaluation.evaluation_models import EvaluationResult


class MasteryService:
    """
    Updates learner mastery states based on evaluation results.
    """


    # Configurable incremental constants
    GAIN_FACTOR = 0.15
    PENALTY_FACTOR = 0.20
    STABILITY_GAIN = 0.10
    STABILITY_PENALTY = 0.15

    def __init__(self, repository: Optional[LearnerRepository] = None):
        self.repository = repository or LearnerRepository()

    def process_evaluation_result(self, eval_result: "EvaluationResult"):
        """
        Main entrypoint: Updates Grammar and Vocabulary mastery states based on evaluation.
        """
        now = eval_result.evaluated_at or datetime.now(timezone.utc)

        # 1. Update Grammar Targets
        for g_code in eval_result.tested_grammar_codes:
            lo_id = self._find_lo_id_for_grammar(eval_result, g_code)
            state = self.repository.get_grammar_state(eval_result.learner_id, lo_id)
            if not state:
                state = GrammarKnowledgeState(
                    learner_id=eval_result.learner_id,
                    learning_object_id=lo_id,
                    grammar_code=g_code,
                    source_item_id=lo_id,
                    first_seen_at=now,
                )
            self._update_grammar_state(state, eval_result, now)
            self.repository.save_grammar_state(state)

        # 2. Update Vocabulary Targets / Senses
        for v_item in eval_result.tested_vocabulary_items:
            lo_id = self._find_lo_id_for_vocab(eval_result, v_item)
            s_ids = eval_result.tested_vocabulary_sense_ids or [None]

            for sense_id in s_ids:
                key = sense_id or lo_id
                state = self.repository.get_vocabulary_state(eval_result.learner_id, key)
                if not state:
                    state = VocabularyKnowledgeState(
                        learner_id=eval_result.learner_id,
                        learning_object_id=lo_id,
                        vocabulary_source_item_id=lo_id,
                        lexeme=v_item,
                        vocabulary_sense_id=sense_id,
                        first_seen_at=now,
                    )
                self._update_vocabulary_state(state, eval_result, now)
                self.repository.save_vocabulary_state(state)

    # ── Internal Grammar Update Logic ─────────────────────────────────────────
    def _update_grammar_state(self, state: GrammarKnowledgeState, eval_result: EvaluationResult, now: datetime):
        state.attempt_count += 1
        state.last_seen_at = now
        state.last_practiced_at = now
        state.mastery_updated_at = now

        if eval_result.correct:
            state.correct_count += 1
            state.consecutive_correct += 1
            state.consecutive_incorrect = 0
            state.last_correct_at = now

            # Increment relevant dimension based on method/score
            inc = self.GAIN_FACTOR * eval_result.score
            state.understanding = min(1.0, round(state.understanding + inc, 4))
            state.controlled_use = min(1.0, round(state.controlled_use + inc * 0.8, 4))
            if eval_result.score >= 0.9:
                state.production = min(1.0, round(state.production + inc * 0.5, 4))

            state.stability = min(1.0, round(state.stability + self.STABILITY_GAIN, 4))
            # Schedule next review
            interval_days = max(1, int(state.stability * 10) + state.consecutive_correct * 2)
            state.review_due_at = now + timedelta(days=interval_days)

        else:
            state.incorrect_count += 1
            state.consecutive_incorrect += 1
            state.consecutive_correct = 0
            state.last_incorrect_at = now

            dec = self.PENALTY_FACTOR
            state.understanding = max(0.0, round(state.understanding - dec * 0.5, 4))
            state.controlled_use = max(0.0, round(state.controlled_use - dec, 4))
            state.production = max(0.0, round(state.production - dec, 4))

            state.stability = max(0.0, round(state.stability - self.STABILITY_PENALTY, 4))
            # Weak items reviewed earlier (within 1 day)
            state.review_due_at = now + timedelta(hours=12)

    # ── Internal Vocabulary Update Logic ──────────────────────────────────────
    def _update_vocabulary_state(self, state: VocabularyKnowledgeState, eval_result: EvaluationResult, now: datetime):
        state.attempt_count += 1
        state.last_seen_at = now
        state.last_practiced_at = now
        state.mastery_updated_at = now

        if eval_result.correct:
            state.correct_count += 1
            state.consecutive_correct += 1
            state.consecutive_incorrect = 0
            state.last_correct_at = now

            inc = self.GAIN_FACTOR * eval_result.score
            state.recognition = min(1.0, round(state.recognition + inc, 4))
            state.recall = min(1.0, round(state.recall + inc * 0.8, 4))
            if eval_result.score >= 0.9:
                state.usage = min(1.0, round(state.usage + inc * 0.5, 4))

            state.stability = min(1.0, round(state.stability + self.STABILITY_GAIN, 4))
            interval_days = max(1, int(state.stability * 10) + state.consecutive_correct * 2)
            state.review_due_at = now + timedelta(days=interval_days)

        else:
            state.incorrect_count += 1
            state.consecutive_incorrect += 1
            state.consecutive_correct = 0
            state.last_incorrect_at = now

            dec = self.PENALTY_FACTOR
            state.recognition = max(0.0, round(state.recognition - dec * 0.5, 4))
            state.recall = max(0.0, round(state.recall - dec, 4))
            state.usage = max(0.0, round(state.usage - dec, 4))

            state.stability = max(0.0, round(state.stability - self.STABILITY_PENALTY, 4))
            state.review_due_at = now + timedelta(hours=12)

    def _find_lo_id_for_grammar(self, eval_result: EvaluationResult, g_code: str) -> str:
        for lo_id in eval_result.target_learning_object_ids:
            if "grammar" in lo_id or g_code in lo_id:
                return lo_id
        return f"grammar:{g_code}"

    def _find_lo_id_for_vocab(self, eval_result: EvaluationResult, v_item: str) -> str:
        for lo_id in eval_result.target_learning_object_ids:
            if "vocabulary" in lo_id or v_item.lower() in lo_id.lower():
                return lo_id
        return f"vocabulary:{v_item.lower()}"
