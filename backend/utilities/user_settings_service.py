# backend/utilities/user_settings_service.py
"""
ROLE: USER SETTINGS & LEARNING PREFERENCES SERVICE

Manages persistent learner preferences including:
- daily_goal_minutes
- reminders_enabled & reminder_time
- audio_autoplay & playback_speed
- ui_theme ("system", "dark", "light")
- accessibility_high_contrast & font_scale
"""

import logging
from typing import Dict, Any
from backend.utilities.utility_models import LearnerSettings

logger = logging.getLogger(__name__)


class UserSettingsService:
    """
    Service maintaining learner user settings and UI preferences.
    """

    def __init__(self):
        self._settings: Dict[str, LearnerSettings] = {}

    def get_settings(self, learner_id: str) -> LearnerSettings:
        return self._settings.get(learner_id, LearnerSettings(learner_id=learner_id))

    def update_settings(self, learner_id: str, **kwargs: Any) -> LearnerSettings:
        current = self.get_settings(learner_id)
        current_dict = current.model_dump()
        current_dict.update({k: v for k, v in kwargs.items() if v is not None})
        updated = LearnerSettings(**current_dict)
        self._settings[learner_id] = updated
        logger.info(f"Learner settings updated for '{learner_id}'.")
        return updated
