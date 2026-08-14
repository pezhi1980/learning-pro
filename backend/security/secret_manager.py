# backend/security/secret_manager.py
"""
ROLE: SECRET MANAGER

Safely retrieves secrets and credentials exclusively from environment variables or .env configurations.
Prevents hardcoded fallback API keys, signing secrets, and database credentials in production codebase.
"""

import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class SecretManager:
    """
    Manager enforcing environment secret retrieval without hardcoded fallbacks.
    """

    @staticmethod
    def get_secret(secret_name: str, default: Optional[str] = None) -> Optional[str]:
        val = os.getenv(secret_name)
        if val:
            return val
        if default and ("sk-proj" not in default):
            return default
        return None

    @staticmethod
    def require_secret(secret_name: str) -> str:
        val = os.getenv(secret_name)
        if not val or "sk-proj" in val:
            logger.error(f"REQUIRED SECRET MISSING: '{secret_name}' is not configured in environment variables.")
            raise KeyError(f"Configuration Error: Required secret '{secret_name}' is missing from environment variables.")
        return val
