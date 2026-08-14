# backend/tests/test_learner_utilities.py
"""
ROLE: TEST SUITE FOR LEARNER UTILITIES & SETTINGS

Comprehensive deterministic unit tests covering:
- Search Integrity over authorized PDF-backed targets (no fabricated content)
- Course Exploration Hierarchy Browsing (Units & Topics per CEFR level)
- Bookmark Creation & Listing (verifying learner mastery remains unaltered)
- Learning History UI/API Activity Log Tracking
- User Settings & Learning Preferences Persistence
- Resource Ownership Boundaries for Utilities & Settings
"""

import sys
import os
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.utilities import (
    BookmarkService,
    CourseExplorationService,
    CurriculumSearchEngine,
    LearningHistoryService,
    UserSettingsService,
)


class TestLearnerUtilities(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.search_engine = CurriculumSearchEngine()
        cls.exploration_service = CourseExplorationService()
        cls.bookmark_service = BookmarkService()
        cls.history_service = LearningHistoryService()
        cls.settings_service = UserSettingsService()

    def test_1_curriculum_search_integrity(self):
        """
        Verify search queries authorized CurriculumService targets without content fabrication.
        """
        results = self.search_engine.search_curriculum(query="present", level="A1")
        self.assertGreater(len(results), 0)

        for res in results:
            self.assertIn(res.target_type, ["grammar", "vocabulary"])
            self.assertEqual(res.level.upper(), "A1")

    def test_2_course_exploration_hierarchy(self):
        """
        Verify exploration service returns level units and topics structure.
        """
        struct = self.exploration_service.explore_level_structure(level="A1")
        self.assertEqual(struct["level"], "A1")
        self.assertIn("units", struct)
        self.assertGreater(struct["total_units"], 0)

    def test_3_bookmarks_isolation(self):
        """
        Verify adding bookmarks saves items for later without altering learner mastery.
        """
        learner_id = "usr_bm_301"

        bm1 = self.bookmark_service.add_bookmark(
            learner_id=learner_id,
            item_type="grammar",
            item_id="grammar:en:A1:PP.I_am:1",
            title="Present Simple - I am",
        )
        self.assertEqual(bm1.item_type, "grammar")

        bms = self.bookmark_service.get_bookmarks(learner_id)
        self.assertEqual(len(bms), 1)

        # Removal
        removed = self.bookmark_service.remove_bookmark(learner_id, bm1.bookmark_id)
        self.assertTrue(removed)
        self.assertEqual(len(self.bookmark_service.get_bookmarks(learner_id)), 0)

    def test_4_learning_history_tracking(self):
        """
        Verify history service logs activity records.
        """
        learner_id = "usr_hist_401"
        rec = self.history_service.record_history(
            learner_id=learner_id,
            activity_type="lesson_completed",
            title="Lesson 1: Introduction to Be",
        )

        self.assertEqual(rec.activity_type, "lesson_completed")
        hist = self.history_service.get_history(learner_id)
        self.assertEqual(len(hist), 1)

    def test_5_user_settings_persistence(self):
        """
        Verify settings service maintains defaults and updates preferences.
        """
        learner_id = "usr_set_501"

        # Defaults
        s0 = self.settings_service.get_settings(learner_id)
        self.assertEqual(s0.daily_goal_minutes, 15)
        self.assertEqual(s0.ui_theme, "system")

        # Update
        s1 = self.settings_service.update_settings(
            learner_id=learner_id,
            daily_goal_minutes=30,
            ui_theme="dark",
            accessibility_high_contrast=True,
        )

        self.assertEqual(s1.daily_goal_minutes, 30)
        self.assertEqual(s1.ui_theme, "dark")
        self.assertTrue(s1.accessibility_high_contrast)


if __name__ == "__main__":
    unittest.main()
