# backend/tests/test_operations.py

import os
import unittest
import tempfile
import json
from backend.operations.health_checker import HealthChecker
from backend.operations.structured_logger import StructuredLogger
from backend.operations.metrics_monitor import MetricsMonitor
from backend.operations.alerting_engine import AlertingEngine
from backend.operations.backup_manager import BackupManager
from backend.operations.restore_service import RestoreService
from backend.curriculum.curriculum_service import CurriculumService


class TestOperations(unittest.TestCase):
    def setUp(self):
        self.curriculum_service = CurriculumService()
        self.health_checker = HealthChecker(curriculum_service=self.curriculum_service)

        self.logger = StructuredLogger(service_name="test_service")
        self.metrics_monitor = MetricsMonitor()
        self.alerting_engine = AlertingEngine(cooldown_seconds=1.0)
        self.temp_dir = tempfile.mkdtemp()
        self.backup_manager = BackupManager(backup_dir=self.temp_dir)
        self.restore_service = RestoreService(self.backup_manager)

    def test_1_health_checker(self):
        """Verify health checker checks dependencies and returns status."""
        report = self.health_checker.check_health()
        self.assertIn(report.status, ["HEALTHY", "DEGRADED", "UNHEALTHY"])
        self.assertIn("application", report.checks)
        self.assertIn("database", report.checks)
        self.assertIn("curriculum", report.checks)
        self.assertIn("storage", report.checks)

    def test_2_structured_logging_privacy(self):
        """Verify logger redacts secrets and learner writing content."""
        payload = {
            "api_key": "sk-secret-12345",
            "learner_writing": "My private essay about my family.",
            "learner_id": "usr_101",
        }
        sanitized = self.logger.sanitize_payload(payload)
        self.assertEqual(sanitized["api_key"], "[REDACTED_SECRET]")
        self.assertEqual(sanitized["learner_writing"], "[REDACTED_PRIVACY_CONTENT]")
        self.assertEqual(sanitized["learner_id"], "usr_101")

        entry = self.logger.log_operation(
            request_id="req_test_01",
            operation="test_op",
            status="SUCCESS",
            message="Test log message",
            safe_identifiers={"learner_id": "usr_101", "api_key": "secret"},
        )
        self.assertEqual(entry.safe_identifiers["api_key"], "[REDACTED_SECRET]")

    def test_3_metrics_monitoring(self):
        """Verify request metrics, latency p95, and failure tracking."""
        self.metrics_monitor.record_request(status_code=200, latency_ms=10.0)
        self.metrics_monitor.record_request(status_code=200, latency_ms=20.0)
        self.metrics_monitor.record_request(status_code=500, latency_ms=100.0)
        self.metrics_monitor.record_failure("speech_tts")

        summary = self.metrics_monitor.get_metrics_summary()
        self.assertEqual(summary["counters"]["api_requests_total"], 3)
        self.assertEqual(summary["counters"]["api_errors_total"], 1)
        self.assertEqual(summary["counters"]["speech_tts_failures_total"], 1)
        self.assertGreater(summary["p95_latency_ms"], 0.0)

    def test_4_alerting_throttling(self):
        """Verify alert triggering and anti-spam cooldown throttling."""
        metrics = {
            "error_rate_percent": 15.0,
            "counters": {"database_failures_total": 1},
        }

        alerts_1 = self.alerting_engine.evaluate_metrics(metrics)
        self.assertGreaterEqual(len(alerts_1), 1)

        # Immediate re-evaluate should trigger cooldown throttling
        alerts_2 = self.alerting_engine.evaluate_metrics(metrics)
        self.assertEqual(len(alerts_2), 0)

    def test_5_backup_and_restore_cycle(self):
        """Verify atomic backup creation, SHA256 checksum, and restoration."""
        state_data = {
            "learners": [{"id": "l_101", "mastery": 0.85}],
            "progress": [{"unit_id": "u_1", "completion": 1.0}],
            "content_versions": [{"version": "1.0.0"}],
        }

        archive = self.backup_manager.create_backup(state_data)
        self.assertIsNotNone(archive.checksum)
        self.assertEqual(archive.record_counts["learners"], 1)

        # Execute Restore Service
        result = self.restore_service.verify_and_restore(archive)
        self.assertTrue(result.success)
        self.assertEqual(result.restored_records, 3)
        self.assertEqual(len(result.errors), 0)

        # Corrupt archive checksum and verify failure
        corrupted_archive = archive.model_copy(update={"checksum": "corrupted_sha256_hash"})
        bad_result = self.restore_service.verify_and_restore(corrupted_archive)

        self.assertFalse(bad_result.success)
        self.assertIn("Checksum mismatch", bad_result.errors[0])


if __name__ == "__main__":
    unittest.main()
