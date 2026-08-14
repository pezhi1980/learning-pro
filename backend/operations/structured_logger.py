# backend/operations/structured_logger.py

import json
import logging
import time
import re
from typing import Dict, Any, Optional
from .operational_models import StructuredLogEntry

logger = logging.getLogger("structured_operations")


class StructuredLogger:
    SENSITIVE_KEYS = {"api_key", "password", "secret", "bearer", "admin_key", "token", "x-admin-key"}

    def __init__(self, service_name: str = "language_backend"):
        self.service_name = service_name

    def sanitize_payload(self, data: Any) -> Any:
        if isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                if k.lower() in self.SENSITIVE_KEYS:
                    sanitized[k] = "[REDACTED_SECRET]"
                elif k in {"learner_writing", "voice_raw", "essay_text", "audio_bytes"}:
                    sanitized[k] = "[REDACTED_PRIVACY_CONTENT]"
                else:
                    sanitized[k] = self.sanitize_payload(v)
            return sanitized
        elif isinstance(data, list):
            return [self.sanitize_payload(item) for item in data]
        return data

    def log_operation(
        self,
        request_id: str,
        operation: str,
        status: str,
        message: str,
        error_code: Optional[str] = None,
        safe_identifiers: Optional[Dict[str, str]] = None,
    ) -> StructuredLogEntry:
        clean_identifiers = self.sanitize_payload(safe_identifiers or {})
        entry = StructuredLogEntry(
            request_id=request_id,
            service=self.service_name,
            operation=operation,
            status=status,
            error_code=error_code,
            message=message,
            timestamp=time.time(),
            safe_identifiers=clean_identifiers,
        )

        formatted_json = json.dumps(entry.model_dump())

        if status == "ERROR":
            logger.error(formatted_json)
        elif status == "WARNING":
            logger.warning(formatted_json)
        else:
            logger.info(formatted_json)

        return entry
