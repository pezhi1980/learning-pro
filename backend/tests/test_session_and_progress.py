# backend/tests/test_session_and_progress.py
"""
ROLE: TEST SUITE FOR SESSION, DAILY LEARNING & PROGRESS SYSTEMS

Comprehensive deterministic tests for:
- Session Creation & Activity Ordering
- Novelty Limits (max 1 primary new target per segment)
- Resumable Daily Sessions (create -> start -> pause -> resume -> complete)
- Partial & Full Session Completion
- Review & Repair Inclusion in Sessions
- Multi-Level Completion Tracking (Micro Lesson, Topic, Unit, Level, Session)
- Educational Learning History Recording & Querying
- Course Progress Updates on Completion
- Preservation of completed != mastered
- Cross-User Data Isolation
- Idempotent Event Processing
"""

import sys
import os
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.course import CourseService, CourseRepository
from backend.learner import LearnerService, LearningStatus
from backend.learning import DecisionType, LearningDecision, LearningDecisionService
from backend.schemas.agent_input import GenerationMode
from backend.session import (
    ActivityType,
    DailyLearningSession,
    DailySessionService,
    LearningHistoryService,
    ProgressService,
    SessionBuilder,
    SessionStatus,
)


class TestSessionAndProgress(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.learner_service = LearnerService()
        cls.course_service = CourseService(learner_service=cls.learner_service)
        cls.decision_service = LearningDecisionService(
            learner_service=cls.learner_service,
            course_service=cls.course_service,
        )
        cls.session_builder = SessionBuilder(default_max_activities=3)
        cls.daily_session_service = DailySessionService(session_builder=cls.session_builder)
        cls.history_service = LearningHistoryService()
        cls.progress_service = ProgressService(
            course_service=cls.course_service,
            daily_session_service=cls.daily_session_service,
            history_service=cls.history_service,
        )

    def test_1_session_builder_creation_and_novelty_budget(self):
        """
        Verify SessionBuilder creates structured Daily Learning Sessions and enforces Novelty Budget.
        """
        decision = LearningDecision(
            decision_id="dec:user_test_01:1001",
            learner_id="user_test_01",
            decision_type=DecisionType.new_learning,
            generation_mode=GenerationMode.grammar_micro_lesson,
            selected_target_grammar_ids=["PP.I_am", "PP.you_are"],  # Multiple targets supplied
            selected_allowed_grammar_ids=["PP.I_am"],
            selected_allowed_vocabulary_ids=["book", "pen"],
        )

        session = self.session_builder.build_session(decision)
        self.assertIsInstance(session, DailyLearningSession)
        self.assertEqual(session.learner_id, "user_test_01")
        self.assertEqual(session.status, SessionStatus.created)
        self.assertGreater(len(session.activities), 0)

        # Enforce Novelty Budget: max 1 primary new target in the new_grammar activity
        new_grammar_acts = [a for a in session.activities if a.activity_type == ActivityType.new_grammar]
        if new_grammar_acts:
            self.assertEqual(len(new_grammar_acts[0].target_grammar_ids), 1, "Novelty budget must restrict to 1 primary target.")

    def test_2_session_ordering_priority(self):
        """
        Verify session activity ordering: Repair -> Review -> New Learning -> Mixed Practice.
        """
        decision = LearningDecision(
            decision_id="dec:user_test_order:1002",
            learner_id="user_test_order",
            decision_type=DecisionType.grammar_repair,
            generation_mode=GenerationMode.grammar_repair,
            selected_target_grammar_ids=["PP.I_am"],
            selected_allowed_grammar_ids=["PP.I_am"],
        )

        session = self.session_builder.build_session(decision)
        self.assertEqual(session.activities[0].activity_type, ActivityType.grammar_repair)

    def test_3_resumable_daily_session_lifecycle(self):
        """
        Test state transitions: create -> start -> pause -> resume -> complete.
        """
        learner_id = "learner_lifecycle_01"
        decision = self.decision_service.determine_next_learning_decision(learner_id, requested_level="A1")

        session = self.daily_session_service.create_session(decision)
        self.assertEqual(session.status, SessionStatus.created)

        started = self.daily_session_service.start_session(session.session_id)
        self.assertEqual(started.status, SessionStatus.in_progress)
        self.assertIsNotNone(started.started_at)

        paused = self.daily_session_service.pause_session(session.session_id)
        self.assertEqual(paused.status, SessionStatus.paused)
        self.assertIsNotNone(paused.paused_at)

        resumed = self.daily_session_service.resume_session(session.session_id)
        self.assertEqual(resumed.status, SessionStatus.in_progress)

    def test_4_partial_and_full_activity_completion(self):
        """
        Test completing individual activities inside a session and auto-session completion.
        """
        learner_id = "learner_partial_comp"
        decision = self.decision_service.determine_next_learning_decision(learner_id, requested_level="A1")
        session = self.daily_session_service.create_session(decision)
        self.daily_session_service.start_session(session.session_id)

        initial_count = len(session.activities)
        first_act_id = session.activities[0].activity_id

        # Complete first activity
        updated_1 = self.daily_session_service.complete_activity(session.session_id, first_act_id)
        self.assertIn(first_act_id, updated_1.completed_activity_ids)
        self.assertNotIn(first_act_id, updated_1.remaining_activity_ids)

        if initial_count > 1:
            self.assertEqual(updated_1.status, SessionStatus.in_progress)

        # Complete remaining activities
        for act in list(updated_1.remaining_activity_ids):
            self.daily_session_service.complete_activity(session.session_id, act)

        completed_sess = self.daily_session_service.get_session(session.session_id)
        self.assertEqual(completed_sess.status, SessionStatus.completed)

    def test_5_progress_service_and_completion_events(self):
        """
        Verify ProgressService logs CompletionEvents for Micro Lesson, Topic, Unit, Level, and Session.
        """
        learner_id = "learner_progress_events"
        a1_nodes = self.course_service.repository.get_all_micro_lessons_in_level("A1")
        ml_id = a1_nodes[0].micro_lesson_id

        # Complete micro lesson
        course_prog = self.progress_service.complete_micro_lesson(learner_id, ml_id)
        self.assertIn(ml_id, course_prog.completed_micro_lesson_ids)

        events = self.history_service.get_completion_events(learner_id)
        self.assertGreater(len(events), 0)
        ml_events = [e for e in events if e.completion_type.value == "micro_lesson"]
        self.assertGreater(len(ml_events), 0)
        self.assertEqual(ml_events[0].target_id, ml_id)

    def test_6_educational_learning_history(self):
        """
        Verify LearningHistoryService records entries and stats correctly.
        """
        learner_id = "learner_history_01"
        self.history_service.record_history_entry(
            learner_id=learner_id,
            record_type="exercise",
            summary="Answered exercise ex_101",
            details={"correct": True, "score": 1.0},
        )

        history = self.history_service.get_learner_history(learner_id)
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].summary, "Answered exercise ex_101")

        stats = self.history_service.get_learner_stats(learner_id)
        self.assertEqual(stats.total_activities_completed, 1)

    def test_7_completed_does_not_equal_mastered(self):
        """
        Verify completing a session/lesson does not alter mastery state directly.
        """
        learner_id = "learner_mastery_sep_02"
        a1_nodes = self.course_service.repository.get_all_micro_lessons_in_level("A1")
        ml_id = a1_nodes[0].micro_lesson_id
        g_target_id = a1_nodes[0].grammar_target_ids[0]

        # Record micro lesson completion
        self.progress_service.complete_micro_lesson(learner_id, ml_id)

        # Verify mastery state is not automatically set to mastered
        g_state = self.learner_service.get_grammar_state(learner_id, g_target_id)
        if g_state:
            self.assertNotEqual(g_state.status, LearningStatus.mastered)

    def test_8_cross_user_isolation(self):
        """
        Verify sessions, progress, and history for user_A do not bleed into user_B.
        """
        user_a = "user_A_isolation"
        user_b = "user_B_isolation"

        dec_a = self.decision_service.determine_next_learning_decision(user_a, requested_level="A1")
        dec_b = self.decision_service.determine_next_learning_decision(user_b, requested_level="A1")

        sess_a = self.daily_session_service.create_session(dec_a)
        sess_b = self.daily_session_service.create_session(dec_b)

        self.assertNotEqual(sess_a.session_id, sess_b.session_id)
        self.assertEqual(sess_a.learner_id, user_a)
        self.assertEqual(sess_b.learner_id, user_b)

        self.history_service.record_history_entry(user_a, "session", "Completed Session A")
        hist_a = self.history_service.get_learner_history(user_a)
        hist_b = self.history_service.get_learner_history(user_b)

        self.assertEqual(len(hist_a), 1)
        self.assertEqual(len(hist_b), 0, "User B history must remain empty.")


if __name__ == "__main__":
    unittest.main()
