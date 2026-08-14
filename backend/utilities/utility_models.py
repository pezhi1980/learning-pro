# backend/utilities/utility_models.py
"""
ROLE: LEARNER UTILITIES & SETTINGS DATA MODELS

Defines structured Pydantic data models for:
- Authorized Curriculum Search Results
- Bookmarks & Save for Later items (lessons, topics, grammar, vocabulary, review targets)
- Learning History activity records
- User Settings & Preferences (daily goal, reminders, audio autoplay, playback speed, UI theme, accessibility)
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SearchResultItem(BaseModel):
    target_id: str
    target_type: str  # "grammar" or "vocabulary"
    title: str
    level: str
    topic: str
    details: Dict[str, Any] = Field(default_factory=dict)
    match_score: float = 1.0


class BookmarkItem(BaseModel):
    bookmark_id: str
    learner_id: str
    item_type: str  # "lesson", "topic", "grammar", "vocabulary", "review_target"
    item_id: str
    title: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearningHistoryRecord(BaseModel):
    history_id: str
    learner_id: str
    activity_type: str
    title: str
    details: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LearnerSettings(BaseModel):
    learner_id: str
    daily_goal_minutes: int = 15
    reminders_enabled: bool = True
    reminder_time: str = "20:00"
    audio_autoplay: bool = True
    playback_speed: float = 1.0
    ui_theme: str = "system"  # "system", "dark", "light"
    accessibility_high_contrast: bool = False
    font_scale: float = 1.0
