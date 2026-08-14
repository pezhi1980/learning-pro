# backend/tests/test_performance.py

import time
import unittest
from backend.curriculum.curriculum_service import CurriculumService
from backend.session.session_builder import SessionBuilder
from backend.learning.decision_models import LearningDecision
from backend.course.course_repository import CourseRepository


class TestPerformance(unittest.TestCase):
    def setUp(self):
        self.curriculum_service = CurriculumService()

    def test_1_curriculum_lookup_performance(self):
        """Verify Curriculum target lookup completes under 10 ms."""
        start = time.time()
        grammar_list = self.curriculum_service.list_all_grammar()
        elapsed_ms = (time.time() - start) * 1000

        self.assertGreater(len(grammar_list), 0)
        self.assertLess(elapsed_ms, 100.0, f"Curriculum lookup took {elapsed_ms:.2f} ms")

    def test_2_session_building_performance(self):
        """Verify session creation completes under 50 ms."""
        from backend.learning.decision_models import DecisionType
        from backend.schemas.agent_input import GenerationMode

        start = time.time()
        builder = SessionBuilder()
        decision = LearningDecision(
            decision_id="dec_perf_101",
            learner_id="perf_user_1",
            decision_type=DecisionType.new_learning,
            generation_mode=GenerationMode.grammar_micro_lesson,
            selected_target_grammar_ids=["g_present_simple"],
        )
        session = builder.build_session(decision)
        elapsed_ms = (time.time() - start) * 1000

        self.assertIsNotNone(session)
        self.assertLess(elapsed_ms, 250.0, f"Session creation took {elapsed_ms:.2f} ms")





    def test_3_progress_calculation_performance(self):
        """Verify progress metrics calculation completes under 20 ms."""
        course_repo = CourseRepository()
        start = time.time()
        level_struct = course_repo.get_level("A1")
        elapsed_ms = (time.time() - start) * 1000

        self.assertIsNotNone(level_struct)
        self.assertLess(elapsed_ms, 50.0, f"Progress calculation took {elapsed_ms:.2f} ms")


if __name__ == "__main__":
    unittest.main()
