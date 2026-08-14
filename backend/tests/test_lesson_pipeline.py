# backend/tests/test_lesson_pipeline.py
"""
Deterministic pipeline unit tests for LessonGenerationService using a Mock ContentAgent.
Covers Stage 25 (Cases 1-12), failure injection, and end-to-end traceability tests.
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
from backend.schemas import (
    AgentInput,
    AgentOutput,
    CoverageItem,
    CurriculumAssignmentRequest,
    ExampleItem,
    ExerciseItem,
    ExplanationBlock,
    GenerationMode,
    LessonStatus,
    TargetTrace,
    TaskDifficulty,
)
from backend.services import (
    CurriculumAssignmentError,
    LessonGenerationService,
)


class MockContentAgent:
    """
    Fake Content Generation Agent for deterministic unit testing without calling real AI APIs.
    """

    def __init__(self, stub_output: AgentOutput):
        self.stub_output = stub_output
        self.invoked = False
        self.last_input = None

    async def generate(self, agent_input: AgentInput) -> AgentOutput:
        self.invoked = True
        self.last_input = agent_input
        # Ensure stub output request_id matches agent_input request_id
        out_dict = self.stub_output.model_dump()
        out_dict["request_id"] = agent_input.request_id
        out_dict["generation_mode"] = agent_input.generation_mode
        return AgentOutput(**out_dict)


class TestLessonGenerationPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.curriculum_service = CurriculumService()

    def _create_valid_stub_output(self, request_id: str = "req_p1") -> AgentOutput:
        return AgentOutput(
            request_id=request_id,
            generation_mode=GenerationMode.grammar_micro_lesson,
            title="Verb To Be",
            explanations=[
                ExplanationBlock(
                    id="exp_1",
                    title="Intro",
                    content="Explanation content",
                    targets=TargetTrace(
                        learning_object_id="grammar:en:A1:PP.I_am:1",
                        grammar_codes=["PP.I_am"],
                        vocabulary_items=[],
                        vocabulary_sense_ids=[],
                    ),
                )
            ],
            examples=[
                ExampleItem(
                    id="ex_1",
                    sentence="I am a student.",
                    translation="Man yak daneshjoo hastam.",
                    breakdown="I=Pronoun, am=Verb",
                    targets=TargetTrace(
                        learning_object_id="grammar:en:A1:PP.I_am:1",
                        grammar_codes=["PP.I_am"],
                        vocabulary_items=[],
                        vocabulary_sense_ids=[],
                    ),
                )
            ],
            exercises=[
                ExerciseItem(
                    id="ex_item_1",
                    exercise_type="multiple_choice",
                    prompt="Select correct form: ___ a student.",
                    options=["I am", "You are"],
                    correct_answer="I am",
                    explanation="I am is the correct present form for first person.",
                    targets=TargetTrace(
                        learning_object_id="grammar:en:A1:PP.I_am:1",
                        grammar_codes=["PP.I_am"],
                        vocabulary_items=[],
                        vocabulary_sense_ids=[],
                    ),
                )
            ],
            coverage=[
                CoverageItem(
                    learning_object_id="grammar:en:A1:PP.I_am:1",
                    explained=True,
                    example_covered=True,
                    exercise_covered=True,
                )
            ],
        )

    # ── CASE 1: Valid Assignment + Valid Output -> LessonStatus.validated ────────
    def test_case_1_valid_pipeline_passes(self):
        req = CurriculumAssignmentRequest(
            request_id="req_case1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )
        stub = self._create_valid_stub_output("req_case1")
        agent = MockContentAgent(stub)
        service = LessonGenerationService(agent=agent, curriculum_service=self.curriculum_service)

        lesson = asyncio_run(service.generate_lesson(req))

        self.assertTrue(agent.invoked)
        self.assertEqual(lesson.status, LessonStatus.validated)
        self.assertEqual(lesson.request_id, "req_case1")

    # ── CASE 2: Agent Omits Assigned Target -> LessonStatus.rejected ─────────
    def test_case_2_omitted_target_rejected(self):
        req = CurriculumAssignmentRequest(
            request_id="req_case2",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )
        # Stub output omits the target in traces and coverage
        stub = AgentOutput(
            request_id="req_case2",
            generation_mode=GenerationMode.grammar_micro_lesson,
            explanations=[],
            coverage=[],
        )
        agent = MockContentAgent(stub)
        service = LessonGenerationService(agent=agent, curriculum_service=self.curriculum_service)

        lesson = asyncio_run(service.generate_lesson(req))

        self.assertEqual(lesson.status, LessonStatus.rejected)
        self.assertIn("coverage_validator", lesson.validation_results)
        self.assertFalse(lesson.validation_results["coverage_validator"].passed)

    # ── CASE 3: Agent Invents Grammar Target -> LessonStatus.rejected ─────────
    def test_case_3_invented_grammar_target_rejected(self):
        req = CurriculumAssignmentRequest(
            request_id="req_case3",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )
        stub = self._create_valid_stub_output("req_case3")
        # Add invented grammar code claim in trace
        stub.explanations[0].targets.grammar_codes.append("UNASSIGNED_INVENTED_CODE")

        agent = MockContentAgent(stub)
        service = LessonGenerationService(agent=agent, curriculum_service=self.curriculum_service)

        lesson = asyncio_run(service.generate_lesson(req))

        self.assertEqual(lesson.status, LessonStatus.rejected)
        self.assertFalse(lesson.validation_results["curriculum_validator"].passed)

    # ── CASE 4: Agent Invents Vocabulary Target -> LessonStatus.rejected ──────
    def test_case_4_invented_vocabulary_target_rejected(self):
        req = CurriculumAssignmentRequest(
            request_id="req_case4",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )
        stub = self._create_valid_stub_output("req_case4")
        stub.explanations[0].targets.vocabulary_items.append("UnassignedWord")

        agent = MockContentAgent(stub)
        service = LessonGenerationService(agent=agent, curriculum_service=self.curriculum_service)

        lesson = asyncio_run(service.generate_lesson(req))

        self.assertEqual(lesson.status, LessonStatus.rejected)
        self.assertFalse(lesson.validation_results["curriculum_validator"].passed)

    # ── CASE 5: Agent Uses Unauthorized Sense -> LessonStatus.rejected ────────
    def test_case_5_unauthorized_sense_rejected(self):
        req = CurriculumAssignmentRequest(
            request_id="req_case5",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )
        stub = self._create_valid_stub_output("req_case5")
        stub.explanations[0].targets.vocabulary_sense_ids.append("vocabulary:en:C1:abandon:1:sense")

        agent = MockContentAgent(stub)
        service = LessonGenerationService(agent=agent, curriculum_service=self.curriculum_service)

        lesson = asyncio_run(service.generate_lesson(req))

        self.assertEqual(lesson.status, LessonStatus.rejected)
        self.assertFalse(lesson.validation_results["curriculum_validator"].passed)

    # ── CASE 7: False Coverage Claim -> LessonStatus.rejected ─────────────────
    def test_case_7_false_coverage_claim_rejected(self):
        req = CurriculumAssignmentRequest(
            request_id="req_case7",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )
        stub = self._create_valid_stub_output("req_case7")
        # Add coverage claim for target that has no content trace
        stub.coverage.append(
            CoverageItem(learning_object_id="vocabulary:en:A2:ability:1", explained=True, example_covered=True, exercise_covered=True)
        )

        agent = MockContentAgent(stub)
        service = LessonGenerationService(agent=agent, curriculum_service=self.curriculum_service)

        lesson = asyncio_run(service.generate_lesson(req))

        self.assertEqual(lesson.status, LessonStatus.rejected)
        self.assertFalse(lesson.validation_results["coverage_validator"].passed)

    # ── CASE 8: Exercise Targets Unassigned Curriculum -> LessonStatus.rejected ─
    def test_case_8_exercise_unassigned_target_rejected(self):
        req = CurriculumAssignmentRequest(
            request_id="req_case8",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )
        stub = self._create_valid_stub_output("req_case8")
        stub.exercises[0].targets.grammar_codes.append("UNASSIGNED_EX_GRAMMAR")

        agent = MockContentAgent(stub)
        service = LessonGenerationService(agent=agent, curriculum_service=self.curriculum_service)

        lesson = asyncio_run(service.generate_lesson(req))

        self.assertEqual(lesson.status, LessonStatus.rejected)
        self.assertFalse(lesson.validation_results["exercise_validator"].passed)

    # ── CASE 10 & 11: Ambiguous Assignment Fails Before Agent Invocation ──────
    def test_case_10_11_ambiguous_assignment_fails_before_agent(self):
        req = CurriculumAssignmentRequest(
            request_id="req_case10",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["PP.aren"],  # Ambiguous!
        )
        stub = self._create_valid_stub_output("req_case10")
        agent = MockContentAgent(stub)
        service = LessonGenerationService(agent=agent, curriculum_service=self.curriculum_service)

        with self.assertRaises(CurriculumAssignmentError):
            asyncio_run(service.generate_lesson(req))

        # Agent MUST NOT be invoked if assignment fails
        self.assertFalse(agent.invoked)

    # ── CASE 12: Rejected Lesson Never Receives Validated Status ──────────────
    def test_case_12_rejected_lesson_never_validated(self):
        req = CurriculumAssignmentRequest(
            request_id="req_case12",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )
        stub = self._create_valid_stub_output("req_case12")
        stub.exercises[0].options = ["I am", "I am"]  # Duplicate options failure

        agent = MockContentAgent(stub)
        service = LessonGenerationService(agent=agent, curriculum_service=self.curriculum_service)

        lesson = asyncio_run(service.generate_lesson(req))

        self.assertNotEqual(lesson.status, LessonStatus.validated)
        self.assertEqual(lesson.status, LessonStatus.rejected)


def asyncio_run(coro):
    import asyncio
    return asyncio.run(coro)


if __name__ == "__main__":
    unittest.main()
