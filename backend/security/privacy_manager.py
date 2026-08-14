# backend/security/privacy_manager.py
"""
ROLE: PRIVACY MANAGER

Manages privacy preferences and GDPR governance across:
- voice recordings
- writing responses
- learning history
- error pattern diagnostics
- aggregated analytics
"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class PrivacyManager:
    """
    Manager maintaining learner GDPR privacy settings and consent preferences.
    """

    def __init__(self):
        self._settings: Dict[str, Dict[str, Any]] = {}

    def get_learner_privacy_settings(self, learner_id: str) -> Dict[str, Any]:
        return self._settings.get(learner_id, {
            "learner_id": learner_id,
            "allow_voice_retention": True,
            "allow_writing_retention": True,
            "allow_analytics": True,
            "anonymize_error_patterns": False,
        })

    def update_privacy_preferences(
        self,
        learner_id: str,
        allow_voice_retention: bool = True,
        allow_writing_retention: bool = True,
        allow_analytics: bool = True,
        anonymize_error_patterns: bool = False,
    ) -> Dict[str, Any]:

        settings = {
            "learner_id": learner_id,
            "allow_voice_retention": allow_voice_retention,
            "allow_writing_retention": allow_writing_retention,
            "allow_analytics": allow_analytics,
            "anonymize_error_patterns": anonymize_error_patterns,
        }

        self._settings[learner_id] = settings
        logger.info(f"Updated privacy preferences for learner '{learner_id}'.")
        return settings
