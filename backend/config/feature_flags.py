# backend/config/feature_flags.py

import os
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field


class FeatureFlagState(BaseModel):
    flags: Dict[str, bool] = Field(
        default_factory=lambda: {
            "enable_writing_evaluation": True,
            "enable_spaced_repetition": True,
            "enable_leaderboards": True,
            "enable_ai_pregeneration": True,
            "enable_dark_theme": True,
            "enable_experimental_stt": False,
        }
    )


class FeatureFlagService:
    def __init__(self, override_flags: Optional[Dict[str, bool]] = None):
        self._state = FeatureFlagState()
        if override_flags:
            self._state.flags.update(override_flags)

    def is_enabled(self, flag_name: str, default: bool = False) -> bool:
        env_val = os.getenv(f"FLAG_{flag_name.upper()}")
        if env_val is not None:
            return env_val.lower() in ["true", "1", "yes"]
        return self._state.flags.get(flag_name, default)

    def set_flag(self, flag_name: str, enabled: bool):
        self._state.flags[flag_name] = enabled

    def get_all_flags(self) -> Dict[str, bool]:
        result = dict(self._state.flags)
        for k in self._state.flags.keys():
            env_val = os.getenv(f"FLAG_{k.upper()}")
            if env_val is not None:
                result[k] = env_val.lower() in ["true", "1", "yes"]
        return result
