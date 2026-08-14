# backend/tests/test_release_engineering.py

import os
import unittest
import tempfile
from backend.config.app_config import AppConfig, get_app_config
from backend.config.feature_flags import FeatureFlagService
from backend.config.migrations import MigrationEngine
from backend.config.content_migration import ContentMigrationTool


class TestReleaseEngineering(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.migration_engine = MigrationEngine(migration_dir=self.temp_dir)
        self.content_migration_tool = ContentMigrationTool()

    def test_1_app_config_environments(self):
        """Verify AppConfig environment detection and versioning properties."""
        config = get_app_config()
        self.assertIsNotNone(config.app_version)
        self.assertIsNotNone(config.api_version)
        self.assertIsNotNone(config.schema_version)
        self.assertIsNotNone(config.content_version)

    def test_2_feature_flags(self):
        """Verify feature flags resolution and environment overrides."""
        svc = FeatureFlagService(override_flags={"enable_writing_evaluation": True})
        self.assertTrue(svc.is_enabled("enable_writing_evaluation"))

        svc.set_flag("test_flag", False)
        self.assertFalse(svc.is_enabled("test_flag"))

        flags = svc.get_all_flags()
        self.assertIn("enable_spaced_repetition", flags)

    def test_3_database_migrations(self):
        """Verify sequential database schema migration application."""
        res = self.migration_engine.apply_pending_migrations()
        self.assertEqual(res["total_migrations"], 3)
        self.assertEqual(len(res["newly_applied"]), 3)

        # Subsequent run should find no pending migrations
        res2 = self.migration_engine.apply_pending_migrations()
        self.assertEqual(len(res2["newly_applied"]), 0)

    def test_4_safe_content_migration(self):
        """Verify content version migration preserves historical traceability."""
        targets = [{"id": "g_101", "content_version": "1.0.0"}]
        record = self.content_migration_tool.migrate_content_version(
            from_version="1.0.0",
            to_version="1.1.0",
            pdf_source_id="pdf_grammar_a1",
            targets=targets,
        )

        self.assertEqual(record.status, "COMPLETED")
        self.assertEqual(targets[0]["content_version"], "1.1.0")
        self.assertEqual(targets[0]["previous_version"], "1.0.0")


if __name__ == "__main__":
    unittest.main()
