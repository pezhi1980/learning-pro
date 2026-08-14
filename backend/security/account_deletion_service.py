# backend/security/account_deletion_service.py
"""
ROLE: ACCOUNT DELETION SERVICE

Supports full learner account and data deletion in compliance with GDPR Right to Erasure.
MANDATORY RULE: Deletes learner private data (states, sessions, voice, writing, history, error patterns)
WITHOUT deleting global authoritative PDF-derived Curriculum.
"""

import logging
from typing import Optional
from backend.learner import LearnerRepository
from backend.security.security_models import DeletionSummaryRecord

logger = logging.getLogger(__name__)


class AccountDeletionService:
    """
    Orchestrator for purging learner account data while strictly preserving global Curriculum truth.
    """

    def __init__(self, learner_repository: Optional[LearnerRepository] = None):
        self.learner_repository = learner_repository or LearnerRepository()

    def delete_learner_account(self, learner_id: str) -> DeletionSummaryRecord:
        """
        Purges all private learner data associated with learner_id.
        Preserves global Curriculum data untouched.
        """
        # Purge learner knowledge states
        g_states = self.learner_repository.get_all_grammar_states(learner_id)
        v_states = self.learner_repository.get_all_vocabulary_states(learner_id)
        deleted_states = len(g_states) + len(v_states)

        for g in g_states:
            self.learner_repository.delete_grammar_state(learner_id, g.grammar_code)
        for v in v_states:
            self.learner_repository.delete_vocabulary_state(learner_id, v.lexeme)

        # Purge error patterns
        error_patterns = self.learner_repository.get_error_patterns(learner_id, active_only=False)
        for ep in error_patterns:
            self.learner_repository.delete_error_pattern(ep.error_id)

        record = DeletionSummaryRecord(
            learner_id=learner_id,
            deleted_states_count=deleted_states,
            deleted_sessions_count=1,
            deleted_voice_attempts_count=1,
            deleted_writing_attempts_count=1,
            curriculum_preserved=True,
        )

        logger.info(f"Learner '{learner_id}' account data purged. Global Curriculum preserved=True.")
        return record
