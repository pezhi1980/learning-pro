# backend/learner/learner_repository.py
"""
ROLE: LEARNER REPOSITORY

Provides persistence operations for Learner Knowledge State and Error Patterns.
Enforces strict user isolation: Learner A data is completely segregated from Learner B data.
Includes submission idempotency tracking.
"""

from threading import Lock
from typing import Dict, List, Optional, Set
from backend.learner.knowledge_models import (
    GrammarKnowledgeState,
    LearnerErrorPattern,
    VocabularyKnowledgeState,
)


class LearnerRepository:
    """
    Thread-safe repository abstraction for managing learner knowledge states and error patterns.
    """

    def __init__(self):
        self._lock = Lock()
        # learner_id -> {learning_object_id -> GrammarKnowledgeState}
        self._grammar_store: Dict[str, Dict[str, GrammarKnowledgeState]] = {}
        # learner_id -> {target_or_sense_id -> VocabularyKnowledgeState}
        self._vocab_store: Dict[str, Dict[str, VocabularyKnowledgeState]] = {}
        # learner_id -> {error_id -> LearnerErrorPattern}
        self._error_store: Dict[str, Dict[str, LearnerErrorPattern]] = {}
        # Idempotency: processed submission IDs
        self._processed_submissions: Set[str] = set()

    # ── Idempotency Check ─────────────────────────────────────────────────────
    def is_submission_processed(self, submission_id: str) -> bool:
        with self._lock:
            return submission_id in self._processed_submissions

    def record_submission(self, submission_id: str):
        with self._lock:
            self._processed_submissions.add(submission_id)

    # ── Grammar State Operations ──────────────────────────────────────────────
    def get_grammar_state(self, learner_id: str, learning_object_id: str) -> Optional[GrammarKnowledgeState]:
        with self._lock:
            learner_grammar = self._grammar_store.get(learner_id, {})
            return learner_grammar.get(learning_object_id)

    def get_all_grammar_states(self, learner_id: str) -> List[GrammarKnowledgeState]:
        with self._lock:
            return list(self._grammar_store.get(learner_id, {}).values())

    def save_grammar_state(self, state: GrammarKnowledgeState) -> GrammarKnowledgeState:
        with self._lock:
            if state.learner_id not in self._grammar_store:
                self._grammar_store[state.learner_id] = {}
            self._grammar_store[state.learner_id][state.learning_object_id] = state
            return state

    # ── Vocabulary State Operations ───────────────────────────────────────────
    def get_vocabulary_state(self, learner_id: str, key_id: str) -> Optional[VocabularyKnowledgeState]:
        with self._lock:
            learner_vocab = self._vocab_store.get(learner_id, {})
            return learner_vocab.get(key_id)

    def get_all_vocabulary_states(self, learner_id: str) -> List[VocabularyKnowledgeState]:
        with self._lock:
            return list(self._vocab_store.get(learner_id, {}).values())

    def save_vocabulary_state(self, state: VocabularyKnowledgeState) -> VocabularyKnowledgeState:
        key = state.vocabulary_sense_id or state.learning_object_id
        with self._lock:
            if state.learner_id not in self._vocab_store:
                self._vocab_store[state.learner_id] = {}
            self._vocab_store[state.learner_id][key] = state
            return state

    # ── Error Pattern Operations ──────────────────────────────────────────────
    def get_error_patterns(self, learner_id: str, active_only: bool = True) -> List[LearnerErrorPattern]:
        with self._lock:
            patterns = list(self._error_store.get(learner_id, {}).values())
            if active_only:
                patterns = [p for p in patterns if p.active]
            return patterns

    def save_error_pattern(self, pattern: LearnerErrorPattern) -> LearnerErrorPattern:
        with self._lock:
            if pattern.learner_id not in self._error_store:
                self._error_store[pattern.learner_id] = {}
            self._error_store[pattern.learner_id][pattern.error_id] = pattern
            return pattern
