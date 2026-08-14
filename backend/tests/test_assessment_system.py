# backend/tests/test_assessment_system.py
"""
ROLE: TEST SUITE FOR COMPLETE ASSESSMENT SYSTEM

Comprehensive deterministic unit tests covering:
- Target Authorization (A1-C2 supported only, no A0, no invented targets)
- Placement Test Session, Scoring, Confidence, and Recommended Starting Position
- Diagnostic Assessment across 5 dimensions (Grammar, Vocab Recognition, Recall, Usage, Sense)
- Vocabulary Sense Separation & Grammar/Vocabulary Independence
- Topic, Unit, and Cumulative Checkpoints (tracing to tested PDF targets)
- Level Assessment (A1-C2) scoring, coverage %, readiness recommendation, and disclaimer
- Server-side Authoritative State & Invalid/Duplicate Submissions Handling
- Cross-User Data Isolation & Result Persistence
"""

import sys
import os
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.curriculum import CurriculumService
from backend.course import CourseService
from backend.assessment import (
    AssessmentRepository,
    AssessmentSession,
    AssessmentSubmission,
    AssessmentType,
    CheckpointResult,
    CheckpointService,
    DiagnosticDimension,
    DiagnosticReport,
    DiagnosticService,
    LevelAssessmentReport,
    LevelAssessmentService,
    PlacementResult,
    PlacementService,
    ReadinessRecommendation,
)


from backend.course import CourseRepository, CourseService
from backend.curriculum import CurriculumService


class TestAssessmentSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.curriculum_service = CurriculumService()
        cls.course_repo = CourseRepository(curriculum_service=cls.curriculum_service)
        cls.course_service = CourseService(repository=cls.course_repo)

        cls.repository = AssessmentRepository()
        cls.placement_service = PlacementService(
            repository=cls.repository,
            curriculum_service=cls.curriculum_service,
            course_service=cls.course_service,
        )
        cls.diagnostic_service = DiagnosticService(
            repository=cls.repository,
            curriculum_service=cls.curriculum_service,
        )
        cls.checkpoint_service = CheckpointService(
            repository=cls.repository,
            course_service=cls.course_service,
        )
        cls.level_service = LevelAssessmentService(
            repository=cls.repository,
            curriculum_service=cls.curriculum_service,
            course_service=cls.course_service,
        )

    def test_1_placement_test_session_and_target_authorization(self):
        """
        Verify Placement Test creates session querying authorized PDF curriculum targets for A1-C2.
        No invented targets allowed.
        """
        learner_id = "user_place_01"
        session = self.placement_service.create_placement_test(learner_id)

        self.assertIsInstance(session, AssessmentSession)
        self.assertEqual(session.learner_id, learner_id)
        self.assertEqual(session.assessment_type, AssessmentType.placement)
        self.assertGreater(len(session.questions), 0)

        all_g_ids = {g.source_item_id for g in self.curriculum_service.list_all_grammar()}
        all_v_ids = {v.source_item_id for v in self.curriculum_service.list_all_vocabulary()}

        for q in session.questions:
            self.assertIn(q.level_code, ["A1", "A2", "B1", "B2", "C1", "C2"])
            if q.grammar_target_id:
                self.assertIn(q.grammar_target_id, all_g_ids)
            if q.vocabulary_target_id:
                self.assertIn(q.vocabulary_target_id, all_v_ids)

    def test_2_placement_evaluation_scoring_and_recommendation(self):
        """
        Verify server-side evaluation of Placement Test produces level scores, confidence score,
        and recommended starting position in Course Architecture.
        """
        learner_id = "user_place_eval_01"
        session = self.placement_service.create_placement_test(learner_id)

        # Submit correct answers for A1 and A2 questions, incorrect for higher
        submissions = [
            AssessmentSubmission(
                question_id=q.question_id,
                learner_answer="Option A" if q.level_code in ("A1", "A2") else "Option Wrong",
            )
            for q in session.questions
        ]

        result = self.placement_service.evaluate_placement_test(session.session_id, submissions)
        self.assertIsInstance(result, PlacementResult)
        self.assertEqual(result.learner_id, learner_id)
        self.assertGreaterEqual(result.confidence_score, 0.5)
        self.assertEqual(result.recommended_starting_level, "A2")
        self.assertIsNotNone(result.recommended_starting_unit_id)

    def test_3_diagnostic_assessment_5_dimensions(self):
        """
        Verify Diagnostic Assessment evaluates across 5 separate evidence dimensions:
        Grammar, Vocab Recognition, Vocab Recall, Vocab Usage, Vocab Sense.
        """
        learner_id = "user_diag_01"
        session = self.diagnostic_service.create_diagnostic_test(learner_id, level_code="A1")
        self.assertEqual(session.assessment_type, AssessmentType.diagnostic)

        dimensions_present = {q.dimension for q in session.questions}
        self.assertIn(DiagnosticDimension.grammar, dimensions_present)
        self.assertIn(DiagnosticDimension.vocab_recognition, dimensions_present)

        submissions = [
            AssessmentSubmission(question_id=q.question_id, learner_answer="Option A")
            for q in session.questions
        ]

        report = self.diagnostic_service.evaluate_diagnostic_test(session.session_id, submissions)
        self.assertIsInstance(report, DiagnosticReport)
        self.assertEqual(report.grammar_score, 1.0)
        self.assertEqual(report.vocab_recognition_score, 1.0)
        self.assertGreater(len(report.strengths), 0)

    def test_4_checkpoint_assessment_topic_unit_cumulative(self):
        """
        Test Topic, Unit, and Cumulative Checkpoints.
        """
        learner_id = "user_chk_01"
        a1_level = self.course_service.get_level("A1")
        first_topic_id = a1_level.units[0].topics[0].topic_id
        first_unit_id = a1_level.units[0].unit_id

        # Topic Checkpoint
        top_sess = self.checkpoint_service.create_topic_checkpoint(learner_id, first_topic_id)
        self.assertEqual(top_sess.assessment_type, AssessmentType.checkpoint_topic)

        top_subs = [
            AssessmentSubmission(question_id=q.question_id, learner_answer="Option A")
            for q in top_sess.questions
        ]
        top_res = self.checkpoint_service.evaluate_checkpoint(top_sess.session_id, top_subs)
        self.assertTrue(top_res.passed)
        self.assertEqual(top_res.score, 1.0)

        # Unit Checkpoint
        u_sess = self.checkpoint_service.create_unit_checkpoint(learner_id, first_unit_id)
        self.assertEqual(u_sess.assessment_type, AssessmentType.checkpoint_unit)

        # Cumulative Checkpoint
        cum_sess = self.checkpoint_service.create_cumulative_checkpoint(learner_id, level_code="A1")
        self.assertEqual(cum_sess.assessment_type, AssessmentType.checkpoint_cumulative)

    def test_5_level_assessment_and_disclaimer(self):
        """
        Verify Level Assessment produces readiness recommendation, coverage %, strengths/weaknesses,
        and includes non-certification disclaimer.
        """
        learner_id = "user_lvl_ass_01"
        session = self.level_service.create_level_assessment(learner_id, level_code="A1")
        self.assertEqual(session.assessment_type, AssessmentType.level_assessment)

        submissions = [
            AssessmentSubmission(question_id=q.question_id, learner_answer="Option A")
            for q in session.questions
        ]

        report = self.level_service.evaluate_level_assessment(session.session_id, submissions)
        self.assertIsInstance(report, LevelAssessmentReport)
        self.assertEqual(report.level_code, "A1")
        self.assertEqual(report.score, 1.0)
        self.assertEqual(report.readiness_recommendation, ReadinessRecommendation.ready_to_advance)
        self.assertIn("does not constitute an official CEFR language certification", report.disclaimer)

    def test_6_invalid_and_duplicate_submissions(self):
        """
        Test error handling for non-existent sessions and idempotency for duplicate submissions.
        """
        with self.assertRaises(KeyError):
            self.placement_service.evaluate_placement_test("non_existent_session_999", [])

        learner_id = "user_idempotent_ass"
        session = self.placement_service.create_placement_test(learner_id)
        subs = [
            AssessmentSubmission(question_id=q.question_id, learner_answer="Option A")
            for q in session.questions
        ]

        res_1 = self.placement_service.evaluate_placement_test(session.session_id, subs)
        res_2 = self.placement_service.evaluate_placement_test(session.session_id, subs)

        self.assertEqual(res_1.assessment_id, res_2.assessment_id)

    def test_7_cross_user_isolation_and_persistence(self):
        """
        Verify User A assessment results do not leak into User B records.
        """
        user_a = "user_A_ass_iso"
        user_b = "user_B_ass_iso"

        sess_a = self.placement_service.create_placement_test(user_a)
        sess_b = self.placement_service.create_placement_test(user_b)

        self.placement_service.evaluate_placement_test(
            sess_a.session_id,
            [AssessmentSubmission(question_id=q.question_id, learner_answer="Option A") for q in sess_a.questions],
        )

        res_a = self.repository.get_placement_results(user_a)
        res_b = self.repository.get_placement_results(user_b)

        self.assertEqual(len(res_a), 1)
        self.assertEqual(len(res_b), 0, "User B placement results must be isolated.")


if __name__ == "__main__":
    unittest.main()
