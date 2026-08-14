# backend/utilities/__init__.py
"""
ROLE: LEARNER UTILITIES & SETTINGS PACKAGE

Provides learner utilities, search, exploration, bookmarks, and preferences infrastructure:
- Authorized Curriculum Search Engine (Grammar, Vocabulary, Units, Topics without content fabrication)
- Course Exploration Hierarchy Service (A1-C2 browsing)
- Bookmark & Save for Later Service (without altering learner mastery)
- Learning History UI/API Activity Log Service
- Persistent User Settings & Preferences Service (daily goal, reminders, audio, themes, accessibility)
"""

from .bookmark_service import BookmarkService
from .course_exploration_service import CourseExplorationService
from .curriculum_search_engine import CurriculumSearchEngine
from .learning_history_service import LearningHistoryService
from .user_settings_service import UserSettingsService
from .utility_models import (
    BookmarkItem,
    LearnerSettings,
    LearningHistoryRecord,
    SearchResultItem,
)

__all__ = [
    "SearchResultItem",
    "BookmarkItem",
    "LearningHistoryRecord",
    "LearnerSettings",
    "CurriculumSearchEngine",
    "CourseExplorationService",
    "BookmarkService",
    "LearningHistoryService",
    "UserSettingsService",
]
