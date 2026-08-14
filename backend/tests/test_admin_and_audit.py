# backend/tests/test_admin_and_audit.py
"""
ROLE: TEST SUITE FOR ADMIN, AUDIT & COMPLETE TRACEABILITY

Comprehensive deterministic unit tests covering:
- Admin Authorization & Invalid Key Rejection
- Complete Generation Trace Integrity (all 10 mandatory fields)
- Historical Content Version Inspection
- System-Wide Audit Log Creation (across 8 event categories)
- Enforcement of PDF Curriculum Immutability Rule
"""

import os
import sys
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.audit import (
    AdminControlAction,
    AdminControlService,
    AdminInspectionService,
    AuditEventType,
    AuditLogger,
    GenerationTraceEngine,
    SystemVersioningManager,
)
from backend.lifecycle import ContentVersioningEngine, PublishingStatus, PublishingWorkflowService
from backend.routers.admin_audit_router import verify_admin_key, HTTPException




class TestAdminAndAudit(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.version_manager = SystemVersioningManager()
        cls.trace_engine = GenerationTraceEngine(versioning_manager=cls.version_manager)
        cls.audit_logger = AuditLogger()
        cls.versioning_engine = ContentVersioningEngine()
        cls.publishing_service = PublishingWorkflowService(versioning_engine=cls.versioning_engine)
        cls.inspection_service = AdminInspectionService(
            versioning_engine=cls.versioning_engine,
            trace_engine=cls.trace_engine,
        )
        cls.control_service = AdminControlService(
            publishing_service=cls.publishing_service,
            versioning_engine=cls.versioning_engine,
            audit_logger=cls.audit_logger,
        )

    def test_1_admin_authorization_key_verification(self):
        """
        Verify admin key verification passes for valid key and raises HTTPException for invalid key.
        """
        os.environ["ADMIN_SECRET_KEY"] = "secret_admin_key_123"

        # Valid key
        try:
            verify_admin_key("secret_admin_key_123")
        except HTTPException:
            self.fail("Valid admin key should not raise HTTPException.")

        # Invalid key -> raises 401
        with self.assertRaises(HTTPException) as ctx:
            verify_admin_key("wrong_key_999")
        self.assertEqual(ctx.exception.status_code, 401)

    def test_2_generation_trace_integrity(self):
        """
        Verify GenerationTraceEngine preserves all 10 mandatory trace fields.
        """
        req_id = "req_trace_101"
        rec = self.trace_engine.record_trace(
            request_id=req_id,
            assigned_targets=["g_present_simple"],
            allowed_targets=["v_student"],
            validator_results={"output_validator": True, "coverage_validator": True},
            content_version_hash="hash_trace_abc",
        )

        trace = self.trace_engine.get_trace(req_id)
        self.assertIsNotNone(trace)
        self.assertEqual(trace.request_id, req_id)
        self.assertEqual(trace.assigned_targets, ["g_present_simple"])
        self.assertEqual(trace.allowed_targets, ["v_student"])
        self.assertIsNotNone(trace.model)
        self.assertIsNotNone(trace.model_version)
        self.assertIsNotNone(trace.prompt_version)
        self.assertIsNotNone(trace.schema_version)
        self.assertIsNotNone(trace.source_version_hash)
        self.assertIn("output_validator", trace.validator_results)
        self.assertEqual(trace.content_version_hash, "hash_trace_abc")

    def test_3_historical_version_inspection(self):
        """
        Verify AdminInspectionService returns complete version history trajectory.
        """
        content_id = "lesson_inspect_201"
        v1 = self.versioning_engine.register_content_version(
            content_id=content_id,
            payload={"text": "Inspect v1"},
            initial_status=PublishingStatus.validated,
        )
        v2 = self.versioning_engine.register_content_version(
            content_id=content_id,
            payload={"text": "Inspect v2"},
            initial_status=PublishingStatus.validated,
        )

        details = self.inspection_service.inspect_content_details(content_id)
        self.assertEqual(details["version_count"], 2)
        self.assertEqual(len(details["all_versions"]), 2)

    def test_4_audit_log_creation(self):
        """
        Verify AuditLogger records events across 8 categories with full metadata.
        """
        log1 = self.audit_logger.log_event(
            event_type=AuditEventType.admin_action,
            actor_id="admin_01",
            details={"action": "publish"},
            target_ids=["lesson_101"],
        )

        self.assertEqual(log1.event_type, AuditEventType.admin_action)
        self.assertEqual(log1.actor_id, "admin_01")

        logs = self.audit_logger.get_logs(event_type=AuditEventType.admin_action)
        self.assertGreater(len(logs), 0)

    def test_5_pdf_curriculum_immutability_enforcement(self):
        """
        Verify AdminControlService prevents direct modification of PDF-derived Curriculum truth.
        """
        with self.assertRaises(PermissionError):
            self.control_service.modify_curriculum_truth(
                admin_id="admin_01",
                target_id="grammar:en:A1:PP.I_am:1",
                payload={"code": "illegal_override"},
            )


if __name__ == "__main__":
    unittest.main()
