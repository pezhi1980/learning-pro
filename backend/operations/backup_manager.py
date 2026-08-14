# backend/operations/backup_manager.py

import os
import json
import time
import hashlib
import uuid
import logging
from typing import Dict, Any, Optional

from .operational_models import BackupArchive

logger = logging.getLogger(__name__)


class BackupManager:
    def __init__(self, backup_dir: Optional[str] = None):
        if backup_dir:
            self.backup_dir = backup_dir
        else:
            self.backup_dir = os.path.join(os.path.dirname(__file__), "..", "data", "backups")
        os.makedirs(self.backup_dir, exist_ok=True)

    def create_backup(self, state_payload: Dict[str, Any]) -> BackupArchive:
        archive_id = f"backup_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        raw_json = json.dumps(state_payload, sort_keys=True)
        checksum = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

        record_counts = {}
        for key, val in state_payload.items():
            if isinstance(val, list):
                record_counts[key] = len(val)
            elif isinstance(val, dict):
                record_counts[key] = len(val)

        archive = BackupArchive(
            archive_id=archive_id,
            version="1.0.0",
            created_at=time.time(),
            record_counts=record_counts,
            data=state_payload,
            checksum=checksum,
        )

        file_path = os.path.join(self.backup_dir, f"{archive_id}.json")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(archive.model_dump(), f, indent=2)


        logger.info(f"BACKUP ARCHIVE CREATED: {archive_id} ({len(raw_json)} bytes) at {file_path}")
        return archive

    def get_latest_backup(self) -> Optional[BackupArchive]:
        if not os.path.exists(self.backup_dir):
            return None
        files = [f for f in os.listdir(self.backup_dir) if f.endswith(".json")]
        if not files:
            return None
        files.sort(reverse=True)
        latest_path = os.path.join(self.backup_dir, files[0])
        try:
            with open(latest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return BackupArchive(**data)
        except Exception as e:
            logger.error(f"Failed to read backup {latest_path}: {e}")
            return None
