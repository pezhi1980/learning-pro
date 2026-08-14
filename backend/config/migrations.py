# backend/config/migrations.py

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class Migration:
    def __init__(self, migration_id: str, description: str):
        self.migration_id = migration_id
        self.description = description

    def apply(self) -> bool:
        logger.info(f"APPLYING DB MIGRATION [{self.migration_id}]: {self.description}")
        return True


class MigrationEngine:
    MIGRATIONS: List[Migration] = [
        Migration("001_initial_schema", "Initial database schema for curriculum, learners, and sessions."),
        Migration("002_add_analytics_indexes", "Create performance indexes for analytics and audit logs."),
        Migration("003_add_engagement_tables", "Create tables for streaks, XP, achievements, and leaderboards."),
    ]

    def __init__(self, migration_dir: Optional[str] = None):
        if migration_dir:
            self.migration_dir = migration_dir
        else:
            self.migration_dir = os.path.join(os.path.dirname(__file__), "..", "data", "migrations")
        os.makedirs(self.migration_dir, exist_ok=True)
        self.applied_file = os.path.join(self.migration_dir, "applied.json")

    def get_applied_migrations(self) -> List[str]:
        if not os.path.exists(self.applied_file):
            return []
        try:
            with open(self.applied_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("applied", [])
        except Exception:
            return []

    def apply_pending_migrations(self) -> Dict[str, Any]:
        applied = self.get_applied_migrations()
        newly_applied = []

        for m in self.MIGRATIONS:
            if m.migration_id not in applied:
                success = m.apply()
                if success:
                    applied.append(m.migration_id)
                    newly_applied.append(m.migration_id)

        with open(self.applied_file, "w", encoding="utf-8") as f:
            json.dump({"applied": applied, "updated_at": time.time()}, f, indent=2)

        return {
            "total_migrations": len(self.MIGRATIONS),
            "currently_applied": applied,
            "newly_applied": newly_applied,
        }
