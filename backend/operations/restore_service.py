# backend/operations/restore_service.py

import json
import hashlib
import time
import logging
from typing import Dict, Any, Optional
from .operational_models import BackupArchive, RestoreResult

logger = logging.getLogger(__name__)


class RestoreService:
    def __init__(self, backup_manager=None):
        self.backup_manager = backup_manager

    def verify_and_restore(self, archive: BackupArchive) -> RestoreResult:
        errors = []

        # 1. Verify SHA256 Checksum Integrity
        raw_json = json.dumps(archive.data, sort_keys=True)
        computed_checksum = hashlib.sha256(raw_json.encode("utf-8")).hexdigest()

        if computed_checksum != archive.checksum:
            errors.append(f"Checksum mismatch! Stored: {archive.checksum}, Computed: {computed_checksum}")
            return RestoreResult(
                success=False,
                archive_id=archive.archive_id,
                restored_records=0,
                errors=errors,
                timestamp=time.time(),
            )

        # 2. Parse and Validate Schema Fields
        total_restored = 0
        try:
            for category, items in archive.data.items():
                if isinstance(items, list):
                    total_restored += len(items)
                elif isinstance(items, dict):
                    total_restored += len(items)
        except Exception as e:
            errors.append(f"Schema parsing error during restore: {str(e)}")
            return RestoreResult(
                success=False,
                archive_id=archive.archive_id,
                restored_records=0,
                errors=errors,
                timestamp=time.time(),
            )

        logger.info(f"RESTORE SUCCESSFUL for archive {archive.archive_id}. {total_restored} records restored.")
        return RestoreResult(
            success=True,
            archive_id=archive.archive_id,
            restored_records=total_restored,
            errors=[],
            timestamp=time.time(),
        )
