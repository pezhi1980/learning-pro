# backend/tests/test_advanced_learning_intelligence.py
"""
ROLE: TEST SUITE FOR ADVANCED LEARNING INTELLIGENCE

Comprehensive deterministic unit tests covering:
- Spaced Repetition Engine interval expansion & lapse handling
- 4-Dimensional Advanced Mastery updates from accumulated evidence
- Knowledge Graph relationship integrity & prerequisite verification
- Personalized Opportunity Ranking (0 invented targets)
- Novelty Control cognitive load caps
"""

import sys
import os
import unittest
from datetime import datetime, timedelta, timezone

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.intelligence import (
    AdvancedMasteryService,
    KnowledgeEdge,
    KnowledgeGraphService,
    NoveltyControlService,
    PersonalizationService,
    RelationshipType,
    SpacedRepetitionEngine,
)
from backend.learner.knowledge_models import GrammarKnowledgeState, VocabularyKnowledgeState


class TestAdvancedLearningIntelligence(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.srs_engine = SpacedRepetitionEngine()
        cls.mastery_service = AdvancedMasteryService(srs_engine=cls.srs_engine)
        cls.graph_service = KnowledgeGraphService()
        cls.personalization_service = PersonalizationService()
        cls.novelty_service = NoveltyControlService()

    def test_1_spaced_repetition_scheduling(self):
        """
        Verify SpacedRepetitionEngine expands interval on success and resets stability on lapse.
        """
        now = datetime.now(timezone.utc)
        last_prac = now - timedelta(days=2)

        # Success case
        new_s, lapses, ret_prob, due_at = self.srs_engine.compute_next_schedule(
            current_stability=2.0,
            is_correct=True,
            overall_mastery=0.80,
            consecutive_correct=2,
            consecutive_incorrect=0,
            lapses=0,
            last_practiced_at=last_prac,
        )

        self.assertGreater(new_s, 2.0, "Stability must expand on correct recall.")
        self.assertEqual(lapses, 0)
        self.assertGreater(ret_prob, 0.0)

        # Failure/Lapse case
        new_s_fail, lapses_fail, _, _ = self.srs_engine.compute_next_schedule(
            current_stability=10.0,
            is_correct=False,
            overall_mastery=0.80,
            consecutive_correct=0,
            consecutive_incorrect=1,
            lapses=0,
            last_practiced_at=last_prac,
        )

        self.assertLess(new_s_fail, 10.0, "Stability must drop on lapse.")
        self.assertEqual(lapses_fail, 1)

    def test_2_advanced_4d_grammar_and_vocabulary_mastery(self):
        """
        Test 4-dimensional mastery updates for Grammar and Vocabulary from accumulated evidence.
        """
        g_state = GrammarKnowledgeState(
            learner_id="usr_intel_01",
            learning_object_id="lobj_g1",
            grammar_code="present_simple",
            source_item_id="src_g1",
        )

        # Process production evidence
        updated_g = self.mastery_service.process_grammar_evidence(
            state=g_state,
            activity_type="production_writing",
            is_correct=True,
            score=1.0,
        )

        self.assertGreater(updated_g.production, 0.0)
        self.assertGreater(updated_g.controlled_use, 0.0)
        self.assertGreater(updated_g.stability, 0.0)

        v_state = VocabularyKnowledgeState(
            learner_id="usr_intel_01",
            learning_object_id="lobj_v1",
            lexeme="apple",
            vocabulary_source_item_id="src_v1",
        )


        updated_v = self.mastery_service.process_vocabulary_evidence(
            state=v_state,
            activity_type="vocabulary_recognition",
            is_correct=True,
            score=1.0,
        )

        self.assertGreater(updated_v.recognition, 0.0)
        self.assertGreater(updated_v.stability, 0.0)

    def test_3_knowledge_graph_relationships(self):
        """
        Verify Knowledge Graph relationship edges and prerequisite retrieval.
        """
        self.graph_service.add_edge(
            source_id="g_a1_be",
            target_id="g_a1_present_simple",
            relationship=RelationshipType.prerequisite,
            verified=True,
        )

        prereqs = self.graph_service.get_prerequisites("g_a1_present_simple")
        self.assertIn("g_a1_be", prereqs)

        # Unverified relationship rejection
        unverified_edge = self.graph_service.add_edge(
            source_id="g_fake_source",
            target_id="g_a1_present_simple",
            relationship=RelationshipType.prerequisite,
            verified=False,
        )
        self.assertIsNone(unverified_edge, "Unverified relationships must be rejected.")

    def test_4_personalized_opportunity_ranking(self):
        """
        Test ranking candidate opportunities using multi-factor personalization weights with 0 invented targets.
        """
        learner_id = "usr_rank_01"
        candidates = ["src_g1", "src_v1", "src_unseen_99"]

        ranked = self.personalization_service.rank_learning_opportunities(
            learner_id=learner_id,
            candidate_target_ids=candidates,
            preferences={"focus_type": "grammar"},
        )

        self.assertEqual(len(ranked), 3)
        self.assertIn("priority_score", ranked[0])
        # Ranked order check: items with higher priority_score appear first
        self.assertGreaterEqual(ranked[0]["priority_score"], ranked[1]["priority_score"])

    def test_5_novelty_control_cognitive_load_caps(self):
        """
        Verify NoveltyControlService caps simultaneous unknown Grammar (1), Vocab (2), and complexity (1.5).
        """
        known_set = {"g_known_01", "v_known_01"}

        # Valid session within caps
        valid, violations, stats = self.novelty_service.validate_session_novelty(
            proposed_grammar_target_ids=["g_new_01"],
            proposed_vocab_target_ids=["v_new_01", "v_new_02"],
            task_complexity_index=1.2,
            known_target_ids=known_set,
        )
        self.assertTrue(valid)
        self.assertEqual(len(violations), 0)

        # Overload session exceeding caps
        valid_over, violations_over, stats_over = self.novelty_service.validate_session_novelty(
            proposed_grammar_target_ids=["g_new_01", "g_new_02"],  # 2 > 1
            proposed_vocab_target_ids=["v_new_01", "v_new_02", "v_new_03"],  # 3 > 2
            task_complexity_index=2.0,  # 2.0 > 1.5
            known_target_ids=known_set,
        )
        self.assertFalse(valid_over)
        self.assertEqual(len(violations_over), 3)


if __name__ == "__main__":
    unittest.main()
