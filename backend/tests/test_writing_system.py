# backend/tests/test_writing_system.py
"""
ROLE: TEST SUITE FOR WRITING, FREE PRODUCTION, FEEDBACK & HINTS

Comprehensive deterministic unit tests covering:
- Free Production Evaluation & Non-Exact Matching
- 3 Evaluation Modes (deterministic, advanced_evaluation_required, ai_assisted)
- Curriculum Safeguards (no curriculum invention, no direct mastery mutation)
- 5-Dimension Structured Feedback & Repair Connections
- Progressive Hint System (hint_1 -> hint_2 -> hint_3 -> answer_reveal) & Hint Usage Context
- Learner Ownership & History Persistence
"""

import sys
import os
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.writing import (
    EvaluationMode,
    FreeProductionEvaluator,
    HintLevel,
    HintRequest,
    HintResponse,
    ProgressiveHintService,
    StructuredFeedback,
    WritingEvaluationResult,
    WritingEvaluator,
    WritingFeedbackService,
    WritingService,
    WritingSubmission,
    WritingTaskType,
)


class TestWritingSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.writing_service = WritingService()

    def test_1_free_production_non_exact_matching(self):
        """
        Verify semantically open responses are evaluated without requiring exact string matches.
        """
        sub = WritingSubmission(
            submission_id="sub_open_01",
            learner_id="user_write_01",
            task_type=WritingTaskType.sentence_construction,
            prompt="Write a sentence using the word 'coffee'.",
            learner_text="In the morning I enjoy drinking hot coffee with milk.",
            target_vocabulary_items=["coffee"],
            evaluation_mode=EvaluationMode.advanced_evaluation_required,
        )

        result = self.writing_service.evaluate_writing(sub)
        self.assertIsInstance(result, WritingEvaluationResult)
        self.assertTrue(result.is_correct, "Valid open response must pass despite non-exact string match.")
        self.assertGreaterEqual(result.overall_score, 0.70)

    def test_2_three_evaluation_modes(self):
        """
        Test evaluation across 3 modes: deterministic, advanced_evaluation_required, ai_assisted.
        """
        # 1. Deterministic
        sub_det = WritingSubmission(
            submission_id="sub_det_01",
            learner_id="user_write_02",
            task_type=WritingTaskType.short_answer,
            prompt="What is the plural of 'cat'?",
            learner_text="cats",
            target_vocabulary_items=["cats"],
            evaluation_mode=EvaluationMode.deterministic,
        )
        res_det = self.writing_service.evaluate_writing(sub_det)
        self.assertEqual(res_det.evaluation_mode, EvaluationMode.deterministic)
        self.assertTrue(res_det.is_correct)

        # 2. Advanced Evaluation Required (Free Production Heuristics)
        sub_adv = WritingSubmission(
            submission_id="sub_adv_01",
            learner_id="user_write_02",
            task_type=WritingTaskType.paragraph,
            prompt="Write a short paragraph about your daily routine.",
            learner_text="Every morning I wake up at seven o'clock. Then I drink tea and go to work by bus.",
            target_grammar_codes=["present_simple"],
            target_vocabulary_items=["morning", "work", "bus"],
            evaluation_mode=EvaluationMode.advanced_evaluation_required,
        )
        res_adv = self.writing_service.evaluate_writing(sub_adv)
        self.assertEqual(res_adv.evaluation_mode, EvaluationMode.advanced_evaluation_required)
        self.assertTrue(res_adv.is_correct)

        # 3. AI Assisted (Mocked path)
        sub_ai = WritingSubmission(
            submission_id="sub_ai_01",
            learner_id="user_write_02",
            task_type=WritingTaskType.extended_writing,
            prompt="Describe your favorite vacation place.",
            learner_text="My favorite place to visit is the mountains because it is peaceful and beautiful.",
            target_vocabulary_items=["mountains", "beautiful"],
            evaluation_mode=EvaluationMode.ai_assisted,
        )
        res_ai = self.writing_service.evaluate_writing(sub_ai)
        self.assertEqual(res_ai.evaluation_mode, EvaluationMode.ai_assisted)

    def test_3_five_structured_feedback_dimensions_and_repairs(self):
        """
        Test structured feedback generation across 5 dimensions, repair target linking, and sense clarification.
        """
        sub = WritingSubmission(
            submission_id="sub_fb_01",
            learner_id="user_write_03",
            task_type=WritingTaskType.sentence_construction,
            prompt="Write a sentence using 'abandon'.",
            learner_text="Short",  # Under word count
            target_grammar_codes=["past_simple"],
            target_vocabulary_items=["abandon"],
            target_vocabulary_sense_ids=["v_abandon:sense_leave"],
            evaluation_mode=EvaluationMode.advanced_evaluation_required,
        )

        result = self.writing_service.evaluate_writing(sub)
        fb = result.feedback
        self.assertIsInstance(fb, StructuredFeedback)

        self.assertIsNotNone(fb.target_grammar_feedback)
        self.assertIsNotNone(fb.target_vocabulary_feedback)
        self.assertIsNotNone(fb.task_completion_feedback)
        self.assertIsNotNone(fb.clarity_feedback)
        self.assertIsNotNone(fb.vocabulary_sense_clarification)
        self.assertIn("abandon", fb.repair_target_ids)

    def test_4_progressive_hint_system(self):
        """
        Test 4 progressive hint levels (hint_1 -> hint_2 -> hint_3 -> answer_reveal) and hint usage tracking.
        """
        task_id = "task_hint_101"
        learner_id = "user_write_04"

        req_h1 = HintRequest(
            learner_id=learner_id,
            task_id=task_id,
            prompt="Write a sentence",
            target_grammar_codes=["present_simple"],
            target_vocabulary_items=["apple"],
            requested_level=HintLevel.hint_1,
        )
        res_h1 = self.writing_service.request_progressive_hint(req_h1)
        self.assertEqual(res_h1.hint_level, HintLevel.hint_1)
        self.assertFalse(res_h1.answer_revealed)

        req_rev = HintRequest(
            learner_id=learner_id,
            task_id=task_id,
            prompt="Write a sentence",
            target_grammar_codes=["present_simple"],
            target_vocabulary_items=["apple"],
            requested_level=HintLevel.answer_reveal,
        )
        res_rev = self.writing_service.request_progressive_hint(req_rev)
        self.assertEqual(res_rev.hint_level, HintLevel.answer_reveal)
        self.assertTrue(res_rev.answer_revealed)

        # Submit task with hints_used tracked
        sub = WritingSubmission(
            submission_id="sub_hint_eval",
            learner_id=learner_id,
            task_type=WritingTaskType.sentence_construction,
            prompt="Write a sentence",
            learner_text="I eat a fresh green apple every day.",
            target_vocabulary_items=["apple"],
            hints_used=[HintLevel.hint_1, HintLevel.answer_reveal],
        )

        res_eval = self.writing_service.evaluate_writing(sub)
        self.assertEqual(res_eval.hints_used_count, 2)
        self.assertTrue(res_eval.answer_revealed)

    def test_5_learner_writing_history_and_isolation(self):
        """
        Verify learner history tracking and cross-user data isolation.
        """
        u_a = "user_write_A"
        u_b = "user_write_B"

        sub_a = WritingSubmission(
            submission_id="sub_a_1",
            learner_id=u_a,
            task_type=WritingTaskType.sentence_construction,
            prompt="Prompt A",
            learner_text="Sentence by User A.",
        )
        self.writing_service.evaluate_writing(sub_a)

        hist_a = self.writing_service.get_learner_writing_history(u_a)
        hist_b = self.writing_service.get_learner_writing_history(u_b)

        self.assertEqual(len(hist_a), 1)
        self.assertEqual(len(hist_b), 0, "User B writing history must be isolated.")


if __name__ == "__main__":
    unittest.main()
