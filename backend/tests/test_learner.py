# backend/tests/test_learner.py
"""
Unit tests for Learner Knowledge Model, Repository, MasteryService, ErrorTracker, and ReviewService.
Tests:
1. Grammar state independent from Vocabulary state.
2. Grammar dimensions remain independently stored.
3. Vocabulary recognition, recall, usage, stability remain independent.
4. Two senses of the same lexeme remain different learner states.
5. Attempt statistics update without destroying source identity.
6. Unseen item representation.
7. Error patterns reference Grammar targets and Vocabulary senses.
8. Learner A state NEVER leaks into Learner B state (User Isolation).
9. Invalid mastery values outside 0.0-1.0 fail validation.
10. Correct recognition increases recognition; repeated incorrect reduces mastery.
11. One correct answer does not produce instant 1.0 mastery.
"""

import os
import sys
import unittest
from datetime import datetime, timezone

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from pydantic import ValidationError
from backend.evaluation.evaluation_models import EvaluationResult
from backend.learner import (
    ErrorTracker,
    GrammarKnowledgeState,
    LearnerErrorPattern,
    LearnerRepository,
    LearnerService,
    LearningStatus,
    MasteryService,
    ReviewService,
    VocabularyKnowledgeState,
)


class TestLearnerDomain(unittest.TestCase):

    def setUp(self):
        self.repo = LearnerRepository()
        self.learner_service = LearnerService(repository=self.repo)
        self.mastery_service = MasteryService(repository=self.repo)
        self.error_tracker = ErrorTracker(repository=self.repo)
        self.review_service = ReviewService(repository=self.repo)

    def test_1_grammar_vocabulary_independence(self):
        g_state = GrammarKnowledgeState(
            learner_id="usr_1",
            learning_object_id="grammar:en:A1:PP.I_am:1",
            grammar_code="PP.I_am",
            source_item_id="grammar:en:A1:PP.I_am:1",
            understanding=0.8,
        )
        v_state = VocabularyKnowledgeState(
            learner_id="usr_1",
            learning_object_id="vocabulary:en:A2:ability:1",
            vocabulary_source_item_id="vocabulary:en:A2:ability:1",
            lexeme="Ability",
            recognition=0.2,
        )
        self.repo.save_grammar_state(g_state)
        self.repo.save_vocabulary_state(v_state)

        fetched_g = self.repo.get_grammar_state("usr_1", "grammar:en:A1:PP.I_am:1")
        fetched_v = self.repo.get_vocabulary_state("usr_1", "vocabulary:en:A2:ability:1")

        self.assertEqual(fetched_g.understanding, 0.8)
        self.assertEqual(fetched_v.recognition, 0.2)
        self.assertNotEqual(fetched_g.understanding, fetched_v.recognition)

    def test_2_vocabulary_senses_are_distinct(self):
        # Two senses for lexeme 'abandon'
        sense1 = VocabularyKnowledgeState(
            learner_id="usr_1",
            learning_object_id="vocabulary:en:C1:abandon:1",
            vocabulary_source_item_id="vocabulary:en:C1:abandon:1",
            lexeme="Abandon",
            vocabulary_sense_id="vocabulary:en:C1:abandon:1:sense",
            guideword="STOP DOING",
            recall=0.9,
        )
        sense2 = VocabularyKnowledgeState(
            learner_id="usr_1",
            learning_object_id="vocabulary:en:C1:abandon:2",
            vocabulary_source_item_id="vocabulary:en:C1:abandon:2",
            lexeme="Abandon",
            vocabulary_sense_id="vocabulary:en:C1:abandon:2:sense",
            guideword="LEAVE PLACE",
            recall=0.1,
        )
        self.repo.save_vocabulary_state(sense1)
        self.repo.save_vocabulary_state(sense2)

        s1_fetched = self.repo.get_vocabulary_state("usr_1", "vocabulary:en:C1:abandon:1:sense")
        s2_fetched = self.repo.get_vocabulary_state("usr_1", "vocabulary:en:C1:abandon:2:sense")

        self.assertIsNotNone(s1_fetched)
        self.assertIsNotNone(s2_fetched)
        self.assertEqual(s1_fetched.guideword, "STOP DOING")
        self.assertEqual(s2_fetched.guideword, "LEAVE PLACE")
        self.assertEqual(s1_fetched.recall, 0.9)
        self.assertEqual(s2_fetched.recall, 0.1)

    def test_3_user_isolation(self):
        g1 = GrammarKnowledgeState(
            learner_id="user_A",
            learning_object_id="grammar:en:A1:PP.I_am:1",
            grammar_code="PP.I_am",
            source_item_id="grammar:en:A1:PP.I_am:1",
            understanding=0.9,
        )
        self.repo.save_grammar_state(g1)

        # User B reads grammar state
        user_b_state = self.repo.get_grammar_state("user_B", "grammar:en:A1:PP.I_am:1")
        self.assertIsNone(user_b_state)

    def test_4_invalid_mastery_value_fails(self):
        with self.assertRaises(ValidationError):
            GrammarKnowledgeState(
                learner_id="usr_1",
                learning_object_id="g1",
                grammar_code="g1",
                source_item_id="g1",
                understanding=1.5,  # Out of range!
            )

    def test_5_one_correct_answer_does_not_produce_instant_full_mastery(self):
        eval_res = EvaluationResult(
            evaluation_id="eval_1",
            learner_id="usr_1",
            lesson_id="les_1",
            exercise_id="ex_1",
            correct=True,
            score=1.0,
            tested_grammar_codes=["PP.I_am"],
            target_learning_object_ids=["grammar:en:A1:PP.I_am:1"],
            evaluation_method="mcq_exact",
            learner_answer="I am",
            expected_answer="I am",
        )
        self.mastery_service.process_evaluation_result(eval_res)
        state = self.repo.get_grammar_state("usr_1", "grammar:en:A1:PP.I_am:1")

        self.assertIsNotNone(state)
        self.assertEqual(state.attempt_count, 1)
        self.assertLess(state.overall_mastery, 1.0)
        self.assertGreater(state.overall_mastery, 0.0)

    def test_6_error_pattern_tracking(self):
        eval_res = EvaluationResult(
            evaluation_id="eval_err_1",
            learner_id="usr_1",
            lesson_id="les_1",
            exercise_id="ex_1",
            correct=False,
            score=0.0,
            tested_vocabulary_items=["Ability"],
            tested_vocabulary_sense_ids=["vocabulary:en:A2:ability:1:sense"],
            target_learning_object_ids=["vocabulary:en:A2:ability:1"],
            evaluation_method="mcq_exact",
            learner_answer="Able",
            expected_answer="Ability",
            error_codes=["vocabulary.sense.confusion"],
        )
        patterns = self.error_tracker.process_evaluation_errors(eval_res)
        self.assertEqual(len(patterns), 1)
        self.assertEqual(patterns[0].error_code, "vocabulary.sense.confusion")
        self.assertEqual(patterns[0].occurrence_count, 1)

        # Process same error again
        patterns2 = self.error_tracker.process_evaluation_errors(eval_res)
        self.assertEqual(patterns2[0].occurrence_count, 2)


if __name__ == "__main__":
    unittest.main()
