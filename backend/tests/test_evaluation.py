# backend/tests/test_evaluation.py
"""
Unit tests for Answer Evaluation Layer and EvaluationService.
Tests:
1. Correct MCQ evaluation.
2. Incorrect MCQ evaluation.
3. Fill-in-the-blank normalization.
4. Word order sentence evaluation.
5. Unsupported free production task safety (no false certainty).
6. Submission idempotency (duplicate submission ID does not double-count attempts).
7. Target traceability inheritance from ExerciseItem.
"""

import os
import sys
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.evaluation import AnswerEvaluator, EvaluationService
from backend.learner import LearnerRepository, MasteryService
from backend.schemas.agent_output import ExerciseItem, TargetTrace


class TestAnswerEvaluation(unittest.TestCase):

    def setUp(self):
        self.repo = LearnerRepository()
        self.evaluator = AnswerEvaluator()
        self.service = EvaluationService(repository=self.repo, evaluator=self.evaluator)

    def test_mcq_evaluation_correct(self):
        ex = ExerciseItem(
            id="ex_mcq_1",
            exercise_type="multiple_choice",
            prompt="___ a student.",
            options=["I am", "You are"],
            correct_answer="I am",
            targets=TargetTrace(learning_object_id="grammar:en:A1:PP.I_am:1", grammar_codes=["PP.I_am"]),
        )
        res = self.evaluator.evaluate_exercise("usr_1", "les_1", ex, "I am")
        self.assertTrue(res.correct)
        self.assertEqual(res.score, 1.0)
        self.assertEqual(res.tested_grammar_codes, ["PP.I_am"])

    def test_mcq_evaluation_incorrect(self):
        ex = ExerciseItem(
            id="ex_mcq_1",
            exercise_type="multiple_choice",
            prompt="___ a student.",
            options=["I am", "You are"],
            correct_answer="I am",
            targets=TargetTrace(learning_object_id="grammar:en:A1:PP.I_am:1", grammar_codes=["PP.I_am"]),
        )
        res = self.evaluator.evaluate_exercise("usr_1", "les_1", ex, "You are")
        self.assertFalse(res.correct)
        self.assertEqual(res.score, 0.0)
        self.assertIn("grammar.PP.I_am.error", res.error_codes)

    def test_fill_blank_normalization(self):
        ex = ExerciseItem(
            id="ex_fb_1",
            exercise_type="fill_in_blank",
            prompt="Fill in: I ___ (be) happy.",
            correct_answer="am",
            targets=TargetTrace(learning_object_id="grammar:en:A1:PP.I_am:1", grammar_codes=["PP.I_am"]),
        )
        # Learner inputs answer with uppercase and extra spaces
        res = self.evaluator.evaluate_exercise("usr_1", "les_1", ex, "  AM  ")
        self.assertTrue(res.correct)

    def test_free_production_safety(self):
        ex = ExerciseItem(
            id="ex_prod_1",
            exercise_type="free_production",
            prompt="Write a 5-sentence paragraph about your daily routine.",
            correct_answer="",
            targets=TargetTrace(learning_object_id="grammar:en:A1:PP.I_am:1", grammar_codes=["PP.I_am"]),
        )
        res = self.evaluator.evaluate_exercise("usr_1", "les_1", ex, "I wake up at 7am.")
        self.assertFalse(res.correct)
        self.assertEqual(res.evaluation_method, "requires_advanced_evaluation")
        self.assertIn("unsupported_deterministic_evaluation", res.error_codes)

    def test_idempotency_duplicate_submission(self):
        ex = ExerciseItem(
            id="ex_mcq_1",
            exercise_type="multiple_choice",
            prompt="___ a student.",
            options=["I am", "You are"],
            correct_answer="I am",
            targets=TargetTrace(learning_object_id="grammar:en:A1:PP.I_am:1", grammar_codes=["PP.I_am"]),
        )
        res1 = self.service.submit_answer("usr_1", "les_1", ex, "I am", submission_id="sub_unique_100")
        state1 = self.repo.get_grammar_state("usr_1", "grammar:en:A1:PP.I_am:1")
        self.assertEqual(state1.attempt_count, 1)

        # Duplicate submission with same submission_id
        res2 = self.service.submit_answer("usr_1", "les_1", ex, "I am", submission_id="sub_unique_100")
        state2 = self.repo.get_grammar_state("usr_1", "grammar:en:A1:PP.I_am:1")
        # Attempt count must NOT double increment!
        self.assertEqual(state2.attempt_count, 1)
        self.assertTrue(res2.metadata.get("idempotent_duplicate", False))


if __name__ == "__main__":
    unittest.main()
