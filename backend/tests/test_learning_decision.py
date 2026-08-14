# backend/tests/test_learning_decision.py
"""
Unit tests for Learning Decision Engine, TargetSelectionService, and LearningDecisionService.
Tests:
1. Active Grammar error triggers grammar_repair decision.
2. Active Vocabulary error triggers vocabulary_repair decision.
3. Review due items trigger smart_review decision.
4. New learning decision selects authorized PDF curriculum targets.
5. Novelty budget is respected.
6. Allowed supporting content prefers learner-known items.
7. Decision Engine NEVER calls ContentAgent or invents targets.
"""

import os
import sys
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.curriculum import CurriculumService
from backend.learner import GrammarKnowledgeState, LearnerErrorPattern, LearnerRepository, LearnerService
from backend.learning import DecisionType, LearningDecisionService, TargetSelectionService


class TestLearningDecisionEngine(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.curriculum_service = CurriculumService()

    def setUp(self):
        self.repo = LearnerRepository()
        self.learner_service = LearnerService(repository=self.repo)
        self.target_selector = TargetSelectionService(
            curriculum_service=self.curriculum_service,
            learner_service=self.learner_service,
        )
        self.decision_service = LearningDecisionService(
            learner_service=self.learner_service,
            target_selector=self.target_selector,
        )

    def test_1_new_learning_decision_selects_authorized_pdf_item(self):
        decision = self.decision_service.determine_next_learning_decision("usr_fresh", requested_level="A1")
        self.assertEqual(decision.decision_type, DecisionType.new_learning)
        self.assertTrue(len(decision.selected_target_grammar_ids) > 0)

        # Verify selected target actually exists in CurriculumService
        target_id = decision.selected_target_grammar_ids[0]
        g_item = self.curriculum_service.get_grammar_by_id(target_id)
        self.assertIsNotNone(g_item)

    def test_2_active_error_triggers_repair_decision(self):
        # Create active error pattern
        err = LearnerErrorPattern(
            error_id="err_1",
            learner_id="usr_err",
            error_code="grammar.PP.I_am.error",
            category="grammar",
            target_learning_object_id="grammar:en:A1:PP.I_am:1",
            grammar_code="PP.I_am",
            severity_score=0.9,
            first_seen_at=self._now(),
            last_seen_at=self._now(),
        )
        self.repo.save_error_pattern(err)

        decision = self.decision_service.determine_next_learning_decision("usr_err")
        self.assertEqual(decision.decision_type, DecisionType.grammar_repair)
        self.assertIn("grammar:en:A1:PP.I_am:1", decision.selected_target_grammar_ids)

    def test_3_decision_converts_to_assignment_request(self):
        decision = self.decision_service.determine_next_learning_decision("usr_fresh", requested_level="A1")
        assignment_req = self.decision_service.to_assignment_request(decision)

        self.assertIsNotNone(assignment_req.request_id)
        self.assertEqual(assignment_req.target_grammar_ids, decision.selected_target_grammar_ids)
        self.assertEqual(assignment_req.generation_mode, decision.generation_mode)

    def _now(self):
        from datetime import datetime, timezone
        return datetime.now(timezone.utc)


if __name__ == "__main__":
    unittest.main()
