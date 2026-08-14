# backend/speaking/voice_attempt_repository.py
"""
ROLE: VOICE ATTEMPT REPOSITORY

Persistence and storage management for learner voice attempt records.
Enforces learner ownership tracking, target traceability, and deletion support for data privacy.
"""

from typing import Dict, List, Optional
from backend.speaking.speaking_models import VoiceAttemptRecord


class VoiceAttemptRepository:
    """
    Repository maintaining learner voice attempt records with soft and hard deletion capabilities.
    """

    def __init__(self):
        self._attempts: Dict[str, VoiceAttemptRecord] = {}
        self._attempts_by_learner: Dict[str, List[VoiceAttemptRecord]] = {}

    def save_attempt(self, attempt: VoiceAttemptRecord) -> None:
        """
        Saves or updates a VoiceAttemptRecord.
        """
        self._attempts[attempt.attempt_id] = attempt
        if attempt.learner_id not in self._attempts_by_learner:
            self._attempts_by_learner[attempt.learner_id] = []
        if attempt not in self._attempts_by_learner[attempt.learner_id]:
            self._attempts_by_learner[attempt.learner_id].append(attempt)

    def get_attempt(self, attempt_id: str) -> Optional[VoiceAttemptRecord]:
        record = self._attempts.get(attempt_id)
        if record and record.is_deleted:
            return None
        return record

    def get_attempts_by_learner(self, learner_id: str, include_deleted: bool = False) -> List[VoiceAttemptRecord]:
        records = self._attempts_by_learner.get(learner_id, [])
        if include_deleted:
            return records
        return [r for r in records if not r.is_deleted]

    def soft_delete_learner_attempts(self, learner_id: str) -> int:
        """
        Soft deletes all voice attempts belonging to a learner.
        """
        records = self._attempts_by_learner.get(learner_id, [])
        count = 0
        for r in records:
            if not r.is_deleted:
                r.is_deleted = True
                count += 1
        return count

    def hard_delete_learner_attempts(self, learner_id: str) -> int:
        """
        Permanently purges all voice attempts belonging to a learner for privacy compliance.
        """
        records = self._attempts_by_learner.get(learner_id, [])
        count = len(records)
        for r in records:
            if r.attempt_id in self._attempts:
                del self._attempts[r.attempt_id]
        self._attempts_by_learner[learner_id] = []
        return count
