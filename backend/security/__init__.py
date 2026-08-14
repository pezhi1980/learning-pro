# backend/security/__init__.py
"""
ROLE: SECURITY, PRIVACY & DATA GOVERNANCE PACKAGE

Provides security, authorization, input sanitization, and data governance infrastructure:
- Resource Ownership & Authorization Service (Learner A cannot access Learner B resources)
- Anti-Path Traversal & Audio Upload Input Sanitizer (10MB caps)
- Environment Secret Protection Manager
- GDPR Privacy Preference Manager
- Account & Learner Data Deletion Service (preserves global PDF Curriculum)
- Configurable Data Retention Policy Manager (7 to 365 days)
"""

from .security_models import (
    AccessControlContext,
    FileUploadValidationResult,
    DataRetentionPolicy,
    DeletionSummaryRecord,
)
from .authorization_service import AuthorizationService
from .input_sanitizer import InputSanitizer
from .secret_manager import SecretManager
from .privacy_manager import PrivacyManager
from .account_deletion_service import AccountDeletionService
from .data_retention_manager import DataRetentionManager

__all__ = [
    "AccessControlContext",
    "FileUploadValidationResult",
    "DataRetentionPolicy",
    "DeletionSummaryRecord",
    "AuthorizationService",
    "InputSanitizer",
    "SecretManager",
    "PrivacyManager",
    "AccountDeletionService",
    "DataRetentionManager",
]
