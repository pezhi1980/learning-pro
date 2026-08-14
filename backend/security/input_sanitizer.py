# backend/security/input_sanitizer.py
"""
ROLE: INPUT SANITIZER & UPLOAD VALIDATOR

Validates and sanitizes IDs, payloads, answer types, metadata, and audio uploads.
Enforces:
- Anti-path traversal & SQL/script injection protection
- Strict MIME type whitelist for audio uploads (audio/wav, mp3, m4a, ogg, webm)
- 10 MB file size caps
"""

import re
import logging
from typing import Any, Dict, List, Optional, Set
from backend.security.security_models import FileUploadValidationResult

logger = logging.getLogger(__name__)

ALLOWED_AUDIO_MIME_TYPES: Set[str] = {
    "audio/wav",
    "audio/x-wav",
    "audio/mp3",
    "audio/mpeg",
    "audio/m4a",
    "audio/ogg",
    "audio/webm",
}

MAX_AUDIO_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB


class InputSanitizer:
    """
    Sanitization service for preventing injection attacks and bad payloads.
    """

    @staticmethod
    def sanitize_identifier(identifier: str) -> str:
        """
        Sanitizes resource identifiers. Rejects path traversal and dangerous characters.
        """
        if not identifier or not isinstance(identifier, str):
            raise ValueError("Identifier must be a non-empty string.")

        clean_id = identifier.strip()

        # Path traversal check
        if ".." in clean_id or "/" in clean_id or "\\" in clean_id:
            logger.warning(f"PATH TRAVERSAL ATTEMPT REJECTED: '{identifier}'.")
            raise ValueError(f"SECURITY VIOLATION: Invalid identifier '{identifier}'. Path traversal is strictly forbidden.")

        # SQL / Script injection patterns check
        dangerous_patterns = [r"<script>", r"select\s+", r"drop\s+", r"union\s+", r"--", r";"]
        for pat in dangerous_patterns:
            if re.search(pat, clean_id, re.IGNORECASE):
                logger.warning(f"INJECTION PATTERN REJECTED: '{identifier}'.")
                raise ValueError(f"SECURITY VIOLATION: Dangerous injection payload detected in identifier '{identifier}'.")

        return clean_id

    @staticmethod
    def validate_audio_upload(
        file_bytes: bytes,
        mime_type: str,
        max_size_bytes: int = MAX_AUDIO_SIZE_BYTES,
    ) -> FileUploadValidationResult:
        """
        Validates audio file upload byte size and MIME type.
        """
        clean_mime = mime_type.strip().lower()
        size_bytes = len(file_bytes)

        if size_bytes == 0:
            return FileUploadValidationResult(
                is_valid=False,
                mime_type=clean_mime,
                file_size_bytes=size_bytes,
                violation_reason="File upload is empty (0 bytes).",
            )

        if size_bytes > max_size_bytes:
            return FileUploadValidationResult(
                is_valid=False,
                mime_type=clean_mime,
                file_size_bytes=size_bytes,
                violation_reason=f"File size {size_bytes} bytes exceeds max cap of {max_size_bytes} bytes (10MB).",
            )

        if clean_mime not in ALLOWED_AUDIO_MIME_TYPES:
            return FileUploadValidationResult(
                is_valid=False,
                mime_type=clean_mime,
                file_size_bytes=size_bytes,
                violation_reason=f"MIME type '{clean_mime}' is not in allowed audio MIME whitelist ({', '.join(sorted(ALLOWED_AUDIO_MIME_TYPES))}).",
            )

        return FileUploadValidationResult(
            is_valid=True,
            mime_type=clean_mime,
            file_size_bytes=size_bytes,
        )
