# backend/tests/test_closed_loop.py
"""
End-to-End Closed-Loop Integration Test.
Verifies the complete closed educational loop:
Authorized PDFs
  ↓
Curriculum Layer
  ↓
Learner Knowledge Model
  ↓
Learning Decision Engine
  ↓
CurriculumAssignmentService
  ↓
LessonGenerationService
  ↓
ContentAgent (Mock)
  ↓
Backend Validators
  ↓
Validated Lesson
  ↓
Learner submits exercise answer
  ↓
Answer Evaluation
  ↓
Mastery / Error / Review Update
  ↓
Learner Knowledge Model
  ↓
Next Learning Decision
"""

import asyncio
import os
import sys
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.curriculum import CurriculumService
from backend.evaluation import EvaluationService
from backend.learner import LearnerRepository, LearnerService, LearningStatus
from backend.learning import DecisionType, LearningDecisionService
from backend.schemas import (
    AgentInput,
    AgentOutput,
    CoverageItem,
    ExampleItem,
    ExerciseItem,
    ExplanationBlock,
    GenerationMode,
    LessonStatus,
    TargetTrace,
)
from backend.services import CurriculumAssignmentService, LessonGenerationService


class MockContentAgent:
    """
    Fake Content Generation Agent returning structured AgentOutput for closed loop testing.
    """

    async def generate(self, agent_input: AgentInput) -> AgentOutput:
        g_id = agent_input.target_grammar[0].learning_object_id if agent_input.target_grammar else "grammar:en:A1:PP.I_am:1"
        g_code = agent_input.target_grammar[0].grammar_code if agent_input.target_grammar else "PP.I_am"

        return AgentOutput(
            request_id=agent_input.request_id,
            generation_mode=agent_input.generation_mode,
            title="Verb To Be Lesson",
            explanations=[
                ExplanationBlock(
                    id="exp_1",
                    title="Explanation",
                    content="I am is present tense first person singular.",
                    targets=TargetTrace(learning_object_id=g_id, grammar_codes=[g_code]),
                )
            ],
            examples=[
                ExampleItem(
                    id="ex_1",
                    sentence="I am happy.",
                    translation="Man khoshhal hastam.",
                    breakdown="I=Pronoun, am=Verb",
                    targets=TargetTrace(learning_object_id=g_id, grammar_codes=[g_code]),
                )
            ],
            exercises=[
                ExerciseItem(
                    id="ex_item_100",
                    exercise_type="multiple_choice",
                    prompt="Select correct form: ___ happy.",
                    options=["I am", "You are"],
                    correct_answer="I am",
                    explanation="I am is correct.",
                    targets=TargetTrace(learning_object_id=g_id, grammar_codes=[g_code]),
                )
            ],
            coverage=[
                CoverageItem(
                    learning_object_id=g_id,
                    explained=True,
                    example_covered=True,
                    exercise_covered=True,
                )
            ],
        )


class TestClosedLoop(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.curriculum_service = CurriculumService()

    def test_complete_closed_educational_loop(self):
        # Setup Services
        repo = LearnerRepository()
        learner_service = LearnerService(repository=repo)
        decision_service = LearningDecisionService(learner_service=learner_service)
        assignment_service = CurriculumAssignmentService(curriculum_service=self.curriculum_service)
        agent = MockContentAgent()
        generation_service = LessonGenerationService(
            assignment_service=assignment_service,
            agent=agent,
            curriculum_service=self.curriculum_service,
        )
        evaluation_service = EvaluationService(repository=repo)

        learner_id = "learner_loop_1"

        # ── STEP 1: Determine Next Learning Decision ──────────────────────────
        decision = decision_service.determine_next_learning_decision(learner_id, requested_level="A1")
        self.assertEqual(decision.decision_type, DecisionType.new_learning)
        target_g_id = decision.selected_target_grammar_ids[0]

        # ── STEP 2: Convert to Assignment Request & Generate Lesson ──────────
        assignment_req = decision_service.to_assignment_request(decision)
        lesson = asyncio.run(generation_service.generate_lesson(assignment_req))

        self.assertEqual(lesson.status, LessonStatus.validated)
        self.assertIsNotNone(lesson.content)
        self.assertEqual(len(lesson.content.exercises), 1)

        # ── STEP 3: Learner Submits Exercise Answer ────────────────────────────
        ex_to_answer = lesson.content.exercises[0]
        eval_result = evaluation_service.submit_answer(
            learner_id=learner_id,
            lesson_id=lesson.lesson_id,
            exercise=ex_to_answer,
            learner_answer="I am",
            submission_id="sub_loop_001",
        )

        self.assertTrue(eval_result.correct)
        self.assertEqual(eval_result.score, 1.0)

        # ── STEP 4: Verify Learner State Updated in Knowledge Model ───────────
        g_state = repo.get_grammar_state(learner_id, target_g_id)
        self.assertIsNotNone(g_state)
        self.assertEqual(g_state.attempt_count, 1)
        self.assertEqual(g_state.correct_count, 1)
        self.assertGreater(g_state.overall_mastery, 0.0)

        # ── STEP 5: Next Learning Decision Uses Updated State ───────────────────
        next_decision = decision_service.determine_next_learning_decision(learner_id, requested_level="A1")
        self.assertIsNotNone(next_decision)
        # Verify next decision selected a DIFFERENT unstudied target
        self.assertNotEqual(next_decision.selected_target_grammar_ids, decision.selected_target_grammar_ids)


if __name__ == "__main__":
    unittest.main()
