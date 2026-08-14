# backend/speaking/voice_privacy_manager.py
"""
ROLE: VOICE PRIVACY MANAGER

Manages learner voice data privacy policies, data retention windows, and explicit user data deletion.
Enforces GDPR / Privacy compliance for learner audio recordings.
"""

import logging
from typing import Any, Dict
from backend.speaking.voice_attempt_repository import VoiceAttemptRepository

logger = logging.getLogger(__name__)


class VoicePrivacyManager:
    """
    Manages learner voice recording privacy rights, retention periods, and deletion requests.
    """

    def __init__(self, repository: VoiceAttemptRepository):
        self.repository = repository
        self.retention_days = 30

    def purge_learner_voice_data(self, learner_id: str, hard_delete: bool = True) -> Dict[str, Any]:
        """
        Purges all voice attempts and audio metadata associated with a learner upon request.
        """
        if hard_delete:
            deleted_count = self.repository.hard_delete_learner_attempts(learner_id)
        else:
            deleted_count = self.repository.soft_delete_learner_attempts(learner_id)

        logger.info(f"Purged {deleted_count} voice records for learner '{learner_id}' (hard_delete={hard_delete}).")

        return {
            "learner_id": learner_id,
            "deleted_records": deleted_count,
            "hard_delete": hard_delete,
            "status": "success",
        }

    def get_privacy_policy_summary(self) -> Dict[str, Any]:
        """
        Returns the data retention and privacy policy metadata summary.
        """
        return {
            "retention_period_days": self.retention_days,
            "user_data_ownership": True,
            "deletion_on_request_supported": True,
            "anonymized_analytics_only": True,
        }
