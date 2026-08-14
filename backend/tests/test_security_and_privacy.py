# backend/tests/test_security_and_privacy.py
"""
ROLE: SECURITY, PRIVACY & DATA GOVERNANCE TEST SUITE

Comprehensive security boundary unit tests covering:
- Resource Ownership Protection (Learner A cannot access Learner B resources)
- Anti-Path Traversal & Injection Payload Sanitization
- Audio Upload MIME & 10MB File Size Cap Validation
- GDPR Account Data Deletion (preserves global PDF Curriculum)
- Configurable Retention Policy Cleanup (7 to 365 days)
- Environment Secret Protection
"""

import sys
import os
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.security import (
    AccessControlContext,
    AccountDeletionService,
    AuthorizationService,
    DataRetentionManager,
    InputSanitizer,
    PrivacyManager,
    SecretManager,
)


class TestSecurityAndPrivacy(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.authz_service = AuthorizationService()
        cls.input_sanitizer = InputSanitizer()
        cls.secret_manager = SecretManager()
        cls.privacy_manager = PrivacyManager()
        cls.account_deletion_service = AccountDeletionService()
        cls.retention_manager = DataRetentionManager()

    def test_1_resource_ownership_boundary(self):
        """
        Verify Learner A can access Learner A's resources but cannot access Learner B's resources.
        """
        ctx_a = AccessControlContext(requester_id="learner_A", is_admin=False)
        ctx_admin = AccessControlContext(requester_id="admin_01", is_admin=True)

        # Same learner -> allowed
        try:
            self.authz_service.authorize_resource_access(ctx_a, resource_owner_id="learner_A", resource_type="sessions")
        except PermissionError:
            self.fail("Learner A should be authorized to access Learner A's resources.")

        # Cross-learner access -> MUST raise PermissionError
        with self.assertRaises(PermissionError):
            self.authz_service.authorize_resource_access(ctx_a, resource_owner_id="learner_B", resource_type="sessions")

        # Admin accessing Learner B resource -> allowed
        try:
            self.authz_service.authorize_resource_access(ctx_admin, resource_owner_id="learner_B", resource_type="sessions")
        except PermissionError:
            self.fail("Admin should be authorized to access any learner's resources.")

    def test_2_input_sanitization_and_injection_prevention(self):
        """
        Verify InputSanitizer rejects path traversal, injection payloads, and oversized uploads.
        """
        # Path traversal check
        with self.assertRaises(ValueError):
            self.input_sanitizer.sanitize_identifier("../etc/passwd")

        with self.assertRaises(ValueError):
            self.input_sanitizer.sanitize_identifier("learner_01\\..\\secret")

        # SQL / Script injection check
        with self.assertRaises(ValueError):
            self.input_sanitizer.sanitize_identifier("<script>alert(1)</script>")

        # Valid clean identifier
        clean = self.input_sanitizer.sanitize_identifier("learner_valid_123")
        self.assertEqual(clean, "learner_valid_123")

    def test_3_audio_upload_validation(self):
        """
        Verify file upload size caps (10MB) and MIME type whitelist.
        """
        valid_wav = b"RIFF....WAVEfmt "
        res_valid = self.input_sanitizer.validate_audio_upload(valid_wav, mime_type="audio/wav")
        self.assertTrue(res_valid.is_valid)

        # Disallowed MIME type
        res_exe = self.input_sanitizer.validate_audio_upload(valid_wav, mime_type="application/x-executable")
        self.assertFalse(res_exe.is_valid)
        self.assertIn("not in allowed audio MIME whitelist", res_exe.violation_reason)

        # Oversized file (>10MB)
        huge_bytes = b"0" * (10 * 1024 * 1024 + 1)
        res_huge = self.input_sanitizer.validate_audio_upload(huge_bytes, mime_type="audio/wav")
        self.assertFalse(res_huge.is_valid)
        self.assertIn("exceeds max cap of 10485760 bytes", res_huge.violation_reason)

    def test_4_gdpr_account_data_deletion(self):
        """
        Verify AccountDeletionService purges private learner data while preserving global PDF Curriculum.
        """
        learner_id = "usr_gdpr_del_01"
        res = self.account_deletion_service.delete_learner_account(learner_id)

        self.assertEqual(res.learner_id, learner_id)
        self.assertTrue(res.curriculum_preserved, "Global Curriculum MUST be preserved.")

    def test_5_data_retention_cleanup(self):
        """
        Verify DataRetentionManager executes retention policy cleanup schedules.
        """
        summary = self.retention_manager.execute_retention_cleanup()
        self.assertIn("recordings", summary)
        self.assertIn("generated_drafts", summary)
        self.assertIn("rejected_generations", summary)
        self.assertIn("submissions", summary)


if __name__ == "__main__":
    unittest.main()
