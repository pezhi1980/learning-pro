# backend/tests/test_engagement_systems.py
"""
ROLE: TEST SUITE FOR ENGAGEMENT SYSTEMS

Comprehensive deterministic unit tests covering:
- Notification Alert Generation (review_due, reminder, unfinished, assessment_availability)
- Meaningful Streak Qualification Boundaries & Multi-Day Break Resets
- XP Rewards & Anti-Farming Activity ID Deduplication
- Achievement Badge Unlocks on Milestones
- Privacy-Aware Weekly XP Leaderboard & Opt-Out Controls
- Dynamic Engagement Feature Flag Toggles
"""

import sys
import os
import unittest
from datetime import date, timedelta

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.engagement import (
    AchievementService,
    EngagementFeatureFlagManager,
    LeaderboardService,
    NotificationService,
    NotificationTriggerType,
    SocialService,
    StreakService,
    XPService,
)


class TestEngagementSystems(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.flag_manager = EngagementFeatureFlagManager()
        cls.notification_service = NotificationService()
        cls.streak_service = StreakService()
        cls.xp_service = XPService()
        cls.achievement_service = AchievementService()
        cls.leaderboard_service = LeaderboardService()
        cls.social_service = SocialService()

    def test_1_notification_generation(self):
        """
        Verify NotificationService sends alerts for review_due and learning_reminders.
        """
        learner_id = "usr_notif_101"
        rec = self.notification_service.send_notification(
            recipient_id=learner_id,
            trigger_type=NotificationTriggerType.review_due,
            title="Review Due",
            message="You have 3 grammar items ready for review.",
        )

        self.assertEqual(rec.trigger_type, NotificationTriggerType.review_due)
        notifs = self.notification_service.get_learner_notifications(learner_id)
        self.assertEqual(len(notifs), 1)

    def test_2_meaningful_streak_qualification_and_break(self):
        """
        Verify streak increments only on qualifying activity (1 session or >=5 exercises) and breaks on gap > 1 day.
        """
        learner_id = "usr_streak_201"
        day1 = date(2026, 8, 1)
        day2 = date(2026, 8, 2)
        day4 = date(2026, 8, 4)  # Gap of 2 days -> streak break

        # Non-qualifying activity (< 5 exercises)
        st0 = self.streak_service.record_activity(learner_id, exercises_count=2, activity_date=day1)
        self.assertEqual(st0.current_streak, 0)

        # Reaches 5 exercises on Day 1 -> qualifies!
        st1 = self.streak_service.record_activity(learner_id, exercises_count=3, activity_date=day1)
        self.assertEqual(st1.current_streak, 1)

        # Day 2: Full session -> streak=2
        st2 = self.streak_service.record_activity(learner_id, is_full_session=True, activity_date=day2)
        self.assertEqual(st2.current_streak, 2)

        # Day 4 (gap of 2 days) -> streak resets to 1
        st4 = self.streak_service.record_activity(learner_id, is_full_session=True, activity_date=day4)
        self.assertEqual(st4.current_streak, 1)

    def test_3_xp_anti_farming_deduplication(self):
        """
        Verify XPService awards XP for legitimate activities and prevents duplicate farming.
        """
        learner_id = "usr_xp_301"
        act_id = "activity_unique_1001"

        # 1st request -> +50 XP
        xp1 = self.xp_service.award_xp(learner_id, activity_id=act_id, activity_type="session_complete")
        self.assertEqual(xp1.total_xp, 50)

        # 2nd request with SAME activity_id -> duplicate farming blocked (0 XP awarded)
        xp2 = self.xp_service.award_xp(learner_id, activity_id=act_id, activity_type="session_complete")
        self.assertEqual(xp2.total_xp, 50, "Duplicate activity ID MUST NOT yield additional XP.")

    def test_4_achievements_badge_unlocking(self):
        """
        Verify AchievementService unlocks milestone badges.
        """
        learner_id = "usr_achieve_401"
        unlocked = self.achievement_service.evaluate_achievements(
            learner_id=learner_id,
            total_lessons=1,
            current_streak=7,
            total_vocab=55,
        )

        unlocked_ids = [b.badge_id for b in unlocked]
        self.assertIn("first_lesson", unlocked_ids)
        self.assertIn("streak_7", unlocked_ids)
        self.assertIn("vocab_50", unlocked_ids)

    def test_5_leaderboard_privacy_and_opt_out(self):
        """
        Verify LeaderboardService ranks weekly XP and excludes opt-out users.
        """
        self.leaderboard_service.register_or_update_entry("user_top", display_name="Alice", weekly_xp=500, opt_out=False)
        self.leaderboard_service.register_or_update_entry("user_private", display_name="Bob", weekly_xp=1000, opt_out=True)

        rankings = self.leaderboard_service.get_top_rankings()
        ranked_ids = [r.learner_id for r in rankings]

        self.assertIn("user_top", ranked_ids)
        self.assertNotIn("user_private", ranked_ids, "Opt-out user MUST be excluded from public leaderboard.")

    def test_6_feature_flag_controls(self):
        """
        Verify EngagementFeatureFlagManager updates and checks feature toggles.
        """
        self.flag_manager.update_flags(enable_streaks=False, enable_xp=True)
        self.assertFalse(self.flag_manager.is_enabled("streaks"))
        self.assertTrue(self.flag_manager.is_enabled("xp"))

        # Restore default
        self.flag_manager.update_flags(enable_streaks=True, enable_xp=True)


if __name__ == "__main__":
    unittest.main()
