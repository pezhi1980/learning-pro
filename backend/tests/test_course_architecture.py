# backend/tests/test_course_architecture.py
"""
ROLE: TEST SUITE FOR COURSE ARCHITECTURE

Comprehensive deterministic tests for:
- 4-Tier Hierarchy Integrity (Level -> Unit -> Topic -> Micro Lesson)
- Valid Curriculum Source Item References (Grammar & Vocabulary)
- Stable Ordering & Boundary Enforcement (A1-C2 supported only, no A0, no invented targets)
- Course Progression, Unlocking, and Resume Position Updates
- Prerequisite Rules Engine ('requires' and 'builds_on')
- Level Progress Calculation Formula & Summary
- Preservation of completed != mastered
- Integration with LearningDecisionService
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
from backend.learner import LearnerService, LearningStatus
from backend.learning import LearningDecisionService
from backend.course import (
    CourseService,
    CourseRepository,
    PrerequisiteService,
    SUPPORTED_LEVELS,
    CourseLevel,
    CourseUnit,
    CourseTopic,
    MicroLessonNode,
    PrerequisiteRule,
    LevelProgressSummary,
)


class TestCourseArchitecture(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.curriculum_service = CurriculumService()
        cls.learner_service = LearnerService()
        cls.repository = CourseRepository(curriculum_service=cls.curriculum_service)
        cls.prereq_service = PrerequisiteService(repository=cls.repository)
        cls.course_service = CourseService(
            repository=cls.repository,
            prerequisite_service=cls.prereq_service,
            learner_service=cls.learner_service,
        )
        cls.decision_service = LearningDecisionService(
            learner_service=cls.learner_service,
            course_service=cls.course_service,
        )

    def test_1_hierarchy_integrity(self):
        """
        Verify complete 4-tier hierarchy for all supported levels (A1-C2).
        Level -> Unit -> Topic -> Micro Lesson
        """
        self.assertEqual(set(SUPPORTED_LEVELS), {"A1", "A2", "B1", "B2", "C1", "C2"})

        for level_code in SUPPORTED_LEVELS:
            level_obj = self.course_service.get_level(level_code)
            self.assertIsNotNone(level_obj, f"Level {level_code} should exist.")
            self.assertIsInstance(level_obj, CourseLevel)
            self.assertEqual(level_obj.level_code, level_code)
            self.assertGreater(len(level_obj.units), 0, f"Level {level_code} must contain Units.")

            for unit in level_obj.units:
                self.assertIsInstance(unit, CourseUnit)
                self.assertEqual(unit.level_code, level_code)
                self.assertGreater(len(unit.topics), 0, f"Unit {unit.unit_id} must contain Topics.")

                for topic in unit.topics:
                    self.assertIsInstance(topic, CourseTopic)
                    self.assertEqual(topic.unit_id, unit.unit_id)
                    self.assertGreater(len(topic.micro_lessons), 0, f"Topic {topic.topic_id} must contain Micro Lessons.")

                    for ml in topic.micro_lessons:
                        self.assertIsInstance(ml, MicroLessonNode)
                        self.assertEqual(ml.topic_id, topic.topic_id)
                        self.assertEqual(ml.unit_id, unit.unit_id)
                        self.assertEqual(ml.level_code, level_code)

    def test_2_valid_curriculum_references_and_traceability(self):
        """
        Verify all Micro Lessons reference existing authoritative PDF curriculum target IDs.
        No invented targets allowed.
        """
        all_grammar_ids = {g.source_item_id for g in self.curriculum_service.list_all_grammar()}
        all_vocab_ids = {v.source_item_id for v in self.curriculum_service.list_all_vocabulary()}

        for level_code in SUPPORTED_LEVELS:
            micro_lessons = self.repository.get_all_micro_lessons_in_level(level_code)
            self.assertGreater(len(micro_lessons), 0, f"Level {level_code} must have micro lessons.")

            for ml in micro_lessons:
                self.assertGreater(len(ml.grammar_target_ids), 0, f"Micro lesson {ml.micro_lesson_id} must have grammar targets.")
                for g_id in ml.grammar_target_ids:
                    self.assertIn(g_id, all_grammar_ids, f"Grammar target {g_id} must exist in authoritative PDF curriculum.")

                for v_id in ml.vocabulary_target_ids:
                    raw_v_id = v_id.replace(":sense", "")
                    self.assertIn(raw_v_id, all_vocab_ids, f"Vocab target {v_id} must exist in authoritative PDF curriculum.")

    def test_3_stable_ordering_and_lookup(self):
        """
        Verify stable ordering and exact lookup of Course Nodes across multiple queries.
        """
        a1_level_1 = self.course_service.get_level("A1")
        a1_level_2 = self.course_service.get_level("A1")

        self.assertEqual(
            [u.unit_id for u in a1_level_1.units],
            [u.unit_id for u in a1_level_2.units],
        )

        first_ml_id = a1_level_1.units[0].topics[0].micro_lessons[0].micro_lesson_id
        fetched_ml = self.course_service.get_micro_lesson(first_ml_id)
        self.assertIsNotNone(fetched_ml)
        self.assertEqual(fetched_ml.micro_lesson_id, first_ml_id)

    def test_4_unsupported_and_invalid_levels_rejected(self):
        """
        Verify invalid levels (A0, C3, XYZ) return None and are not supported.
        """
        self.assertIsNone(self.course_service.get_level("A0"))
        self.assertIsNone(self.course_service.get_level("C3"))
        self.assertIsNone(self.course_service.get_level("INVALID"))

    def test_5_prerequisite_enforcement(self):
        """
        Test PrerequisiteService rules ('requires' and 'builds_on').
        """
        a1_nodes = self.repository.get_all_micro_lessons_in_level("A1")
        node_1 = a1_nodes[0].micro_lesson_id
        node_2 = a1_nodes[1].micro_lesson_id
        node_3 = a1_nodes[2].micro_lesson_id

        # Register explicit rule: node_3 requires node_1
        self.prereq_service.add_prerequisite_rule(
            source_micro_lesson_id=node_1,
            target_micro_lesson_id=node_3,
            relationship="requires",
            description="Node 1 is required for Node 3",
        )

        # Without completion of node_1, node_3 should be locked
        is_unlocked, unfulfilled = self.prereq_service.validate_prerequisites(node_3, completed_micro_lesson_ids=[])
        self.assertFalse(is_unlocked)
        self.assertIn(node_1, unfulfilled)

        # With node_1 completed, node_3 prerequisites are fulfilled
        is_unlocked_2, unfulfilled_2 = self.prereq_service.validate_prerequisites(
            node_3, completed_micro_lesson_ids=[node_1, node_2]
        )
        self.assertTrue(is_unlocked_2)
        self.assertEqual(len(unfulfilled_2), 0)

    def test_6_course_progression_unlocking_and_resume_position(self):
        """
        Test progress recording, dynamic unlocking, and resume position updates.
        """
        learner_id = "test_learner_course_01"
        progress_0 = self.course_service.get_learner_progress(learner_id)
        self.assertEqual(progress_0.current_level, "A1")
        self.assertIsNotNone(progress_0.current_micro_lesson_id)

        initial_ml = progress_0.current_micro_lesson_id

        # Record completion of initial_ml
        progress_1 = self.course_service.record_micro_lesson_completion(learner_id, initial_ml)
        self.assertIn(initial_ml, progress_1.completed_micro_lesson_ids)
        self.assertNotEqual(progress_1.current_micro_lesson_id, initial_ml, "Resume position must advance.")
        self.assertEqual(progress_1.resume_position["micro_lesson_id"], progress_1.current_micro_lesson_id)

    def test_7_level_progress_calculation_formula(self):
        """
        Verify exact level progress formula:
        Percentage Completed = (Completed Micro Lessons in Level / Total Micro Lessons in Level) * 100
        """
        learner_id = "test_learner_calc_01"
        a1_nodes = self.repository.get_all_micro_lessons_in_level("A1")
        total_nodes = len(a1_nodes)

        # Initially 0% completed
        summary_0 = self.course_service.calculate_level_progress(learner_id, "A1")
        self.assertIsInstance(summary_0, LevelProgressSummary)
        self.assertEqual(summary_0.completed_micro_lessons, 0)
        self.assertEqual(summary_0.percentage_completed, 0.0)

        # Complete 2 nodes
        self.course_service.record_micro_lesson_completion(learner_id, a1_nodes[0].micro_lesson_id)
        self.course_service.record_micro_lesson_completion(learner_id, a1_nodes[1].micro_lesson_id)

        summary_1 = self.course_service.calculate_level_progress(learner_id, "A1")
        expected_percentage = round((2 / total_nodes) * 100, 2)
        self.assertEqual(summary_1.completed_micro_lessons, 2)
        self.assertEqual(summary_1.percentage_completed, expected_percentage)
        self.assertEqual(summary_1.remaining_micro_lessons, total_nodes - 2)

    def test_8_completed_does_not_equal_mastered(self):
        """
        Verify course progression completion is distinct from learner mastery state.
        """
        learner_id = "test_learner_mastery_sep"
        a1_nodes = self.repository.get_all_micro_lessons_in_level("A1")
        ml_id = a1_nodes[0].micro_lesson_id
        g_target_id = a1_nodes[0].grammar_target_ids[0]

        # Record course node completion
        self.course_service.record_micro_lesson_completion(learner_id, ml_id)

        progress = self.course_service.get_learner_progress(learner_id)
        self.assertIn(ml_id, progress.completed_micro_lesson_ids)

        # Check that learner mastery state was NOT automatically modified to mastered
        snapshot = self.learner_service.get_learner_snapshot(learner_id)
        g_state = self.learner_service.get_grammar_state(learner_id, g_target_id)
        if g_state:
            self.assertNotEqual(g_state.status, LearningStatus.mastered, "Course completion must NOT alter mastery without evaluation.")

    def test_9_integration_with_learning_decision_service(self):
        """
        Verify LearningDecisionService uses Course Architecture to locate next authorized course target.
        """
        learner_id = "test_learner_decision_integration"
        decision = self.decision_service.determine_next_learning_decision(
            learner_id=learner_id, requested_level="A1"
        )
        self.assertIsNotNone(decision)
        self.assertIn("COURSE_PROGRESSION_NEXT_TARGET", decision.reason_codes)
        self.assertGreater(len(decision.selected_target_grammar_ids), 0)


if __name__ == "__main__":
    unittest.main()
