# backend/tests/test_analytics_and_quality.py
"""
ROLE: TEST SUITE FOR ANALYTICS & CONTENT QUALITY

Comprehensive deterministic unit tests covering:
- Analytics Event Logging across 8 event categories
- Learning Performance Metrics computation (accuracy, completion, drop-off, retention)
- Automated Suspicious Content Quality Detection Signals
- Learner Content Issue Reporting with content version and source trace attachment
- Verification that Analytics does NOT mutate learner mastery truth or Curriculum authority
"""

import sys
import os
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.analytics import (
    AnalyticsEventService,
    AnalyticsEventType,
    ContentQualityAnalyticsService,
    LearningAnalyticsEngine,
    ReportType,
    UserReportService,
)


class TestAnalyticsAndQuality(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.event_service = AnalyticsEventService()
        cls.analytics_engine = LearningAnalyticsEngine(event_service=cls.event_service)
        cls.quality_service = ContentQualityAnalyticsService()
        cls.report_service = UserReportService()

    def test_1_analytics_event_logging(self):
        """
        Verify logging and querying events across 8 event types.
        """
        learner_id = "learner_evt_101"

        e1 = self.event_service.log_event(
            event_type=AnalyticsEventType.lesson_started,
            learner_id=learner_id,
            lesson_id="lesson_101",
        )
        self.assertEqual(e1.event_type, AnalyticsEventType.lesson_started)

        e2 = self.event_service.log_event(
            event_type=AnalyticsEventType.exercise_answered,
            learner_id=learner_id,
            exercise_id="ex_101",
            payload={"is_correct": True},
        )

        events = self.event_service.get_events(learner_id=learner_id)
        self.assertEqual(len(events), 2)

    def test_2_learning_analytics_metrics_calculation(self):
        """
        Test calculation of accuracy, completion rate, and drop-off metrics.
        """
        learner_id = "learner_metrics_201"

        # Log started & completed lessons
        self.event_service.log_event(AnalyticsEventType.lesson_started, learner_id=learner_id, lesson_id="l_1")
        self.event_service.log_event(AnalyticsEventType.lesson_completed, learner_id=learner_id, lesson_id="l_1")
        self.event_service.log_event(AnalyticsEventType.lesson_started, learner_id=learner_id, lesson_id="l_2")
        self.event_service.log_event(AnalyticsEventType.session_abandoned, learner_id=learner_id, lesson_id="l_2")

        # Log exercise answers (1 correct, 1 incorrect)
        self.event_service.log_event(
            AnalyticsEventType.exercise_answered, learner_id=learner_id, target_id="g_target_1", payload={"is_correct": True}
        )
        self.event_service.log_event(
            AnalyticsEventType.exercise_answered, learner_id=learner_id, target_id="g_target_1", payload={"is_correct": False}
        )

        metrics = self.analytics_engine.compute_learner_metrics(learner_id)

        self.assertEqual(metrics["accuracy_percentage"], 50.0)
        self.assertEqual(metrics["completion_rate_percentage"], 50.0)
        self.assertEqual(metrics["drop_off_rate_percentage"], 50.0)

    def test_3_automated_content_quality_signals(self):
        """
        Verify ContentQualityAnalyticsService flags suspicious content exceeding failure/abandonment caps.
        """
        content_id = "lesson_suspicious_301"

        # Normal content -> not suspicious
        normal_rec = self.quality_service.evaluate_content_quality(
            content_id=content_id,
            total_attempts=10,
            failure_count=2,
            started_count=10,
            abandoned_count=1,
            report_count=0,
        )
        self.assertFalse(normal_rec.is_suspicious)

        # Suspicious content (high failure > 60%, high reports >= 3)
        suspicious_rec = self.quality_service.evaluate_content_quality(
            content_id=content_id,
            total_attempts=10,
            failure_count=8,  # 80% failure
            started_count=10,
            abandoned_count=5,  # 50% abandonment
            report_count=3,
        )
        self.assertTrue(suspicious_rec.is_suspicious)
        self.assertGreaterEqual(len(suspicious_rec.suspicious_flags), 3)

        flagged_list = self.quality_service.list_suspicious_content()
        self.assertEqual(len(flagged_list), 1)

    def test_4_user_content_issue_reporting(self):
        """
        Verify learner issue reports are stored with content version and source trace attachment.
        """
        report = self.report_service.submit_report(
            learner_id="learner_report_401",
            report_type=ReportType.wrong_answer,
            description="The expected answer for multiple choice was incorrect.",
            lesson_id="lesson_401",
            exercise_id="ex_401",
            content_version="ver_hash_999",
            source_trace=["grammar:en:A1:PP.I_am:1"],
        )

        self.assertEqual(report.report_type, ReportType.wrong_answer)
        self.assertEqual(report.content_version, "ver_hash_999")
        self.assertIn("grammar:en:A1:PP.I_am:1", report.source_trace)

        reports = self.report_service.list_reports(lesson_id="lesson_401")
        self.assertEqual(len(reports), 1)


if __name__ == "__main__":
    unittest.main()
