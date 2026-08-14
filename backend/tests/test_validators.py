# backend/tests/test_validators.py
"""
Deterministic unit tests for all 5 Backend validators:
1. OutputValidator
2. SourceValidator
3. CoverageValidator
4. CurriculumValidator
5. ExerciseValidator
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
    ExampleItem,
    ExerciseItem,
    ExplanationBlock,
    GenerationMode,
    GrammarTarget,
    SourceReference,
    TargetTrace,
    TaskDifficulty,
    VocabularySenseTarget,
    VocabularyTarget,
)
from backend.validators import (
    CoverageValidator,
    CurriculumValidator,
    ExerciseValidator,
    OutputValidator,
    SourceValidator,
)


class TestValidators(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.curriculum_service = CurriculumService()

        # Shared valid SourceReferences
        cls.g_source = SourceReference(
            source_id="doc:grammar:en:A1",
            source_type="grammar",
            level="A1",
            source_item_id="grammar:en:A1:PP.I_am:1",
        )
        cls.v_source = SourceReference(
            source_id="doc:vocabulary:en:A2",
            source_type="vocabulary",
            level="A2",
            source_item_id="vocabulary:en:A2:ability:1",
        )
        cls.s_source = SourceReference(
            source_id="doc:vocabulary:en:C1",
            source_type="vocabulary",
            level="C1",
            source_item_id="vocabulary:en:C1:abandon:1",
        )

        cls.g_target = GrammarTarget(
            learning_object_id="grammar:en:A1:PP.I_am:1",
            grammar_code="PP.I_am",
            label="I am",
            source=cls.g_source,
        )
        cls.v_target = VocabularyTarget(
            learning_object_id="vocabulary:en:A2:ability:1",
            item="Ability",
            part_of_speech="NOUN",
            source=cls.v_source,
        )

        cls.s_target = VocabularySenseTarget(
            sense_id="vocabulary:en:C1:abandon:1:sense",
            guideword="STOP DOING",
            source=cls.s_source,
        )
        cls.v_sense_target = VocabularyTarget(
            learning_object_id="vocabulary:en:C1:abandon:1",
            item="Abandon",
            source=cls.s_source,
            senses=[cls.s_target],
        )

        cls.valid_input = AgentInput(
            request_id="req_val1",
            target_language="en",
            generation_mode=GenerationMode.grammar_micro_lesson,
            target_grammar=[cls.g_target],
            target_vocabulary=[cls.v_target],
            task_difficulty=TaskDifficulty.controlled_recall,
        )

    # ── 1. OutputValidator Tests ──────────────────────────────────────────────
    def test_output_validator_valid_output(self):
        val = OutputValidator()
        out_dict = {
            "request_id": "req_val1",
            "generation_mode": "grammar_micro_lesson",
            "title": "Verb To Be",
            "explanations": [{
                "id": "exp_1",
                "content": "Explanation",
                "targets": {"grammar_codes": ["PP.I_am"]},
            }],
            "examples": [{
                "id": "ex_1",
                "sentence": "I am a student.",
                "targets": {"grammar_codes": ["PP.I_am"]},
            }],
            "exercises": [{
                "id": "ex_item_1",
                "exercise_type": "multiple_choice",
                "prompt": "___ a student.",
                "options": ["I am", "You are"],
                "correct_answer": "I am",
                "targets": {"grammar_codes": ["PP.I_am"]},
            }],
            "coverage": [{
                "learning_object_id": "grammar:en:A1:PP.I_am:1",
                "explained": True,
                "example_covered": True,
                "exercise_covered": True,
            }],
        }
        agent_out, res = val.validate(out_dict)
        self.assertTrue(res.passed)
        self.assertIsNotNone(agent_out)

    def test_output_validator_extra_forbidden_field_fails(self):
        val = OutputValidator()
        out_dict = {
            "request_id": "req_val1",
            "generation_mode": "grammar_micro_lesson",
            "extra_unauthorized_field": "forbidden",
        }
        agent_out, res = val.validate(out_dict)
        self.assertFalse(res.passed)
        self.assertIsNone(agent_out)

    # ── 2. SourceValidator Tests ──────────────────────────────────────────────
    def test_source_validator_valid_claims(self):
        val = SourceValidator(curriculum_service=self.curriculum_service)
        output = AgentOutput(
            request_id="req_val1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            explanations=[ExplanationBlock(
                id="exp_1",
                content="Content",
                targets=TargetTrace(grammar_codes=["PP.I_am"], vocabulary_items=["Ability"]),
            )],
            coverage=[CoverageItem(learning_object_id="grammar:en:A1:PP.I_am:1", explained=True, example_covered=True, exercise_covered=True)],
        )
        res = val.validate(output)
        self.assertTrue(res.passed)

    def test_source_validator_unknown_grammar_claim_fails(self):
        val = SourceValidator(curriculum_service=self.curriculum_service)
        output = AgentOutput(
            request_id="req_val1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            explanations=[ExplanationBlock(
                id="exp_1",
                content="Content",
                targets=TargetTrace(grammar_codes=["NON_EXISTENT_GRAMMAR_123"]),
            )],
        )
        res = val.validate(output)
        self.assertFalse(res.passed)
        self.assertEqual(res.issues[0].code, "UNKNOWN_GRAMMAR_CODE")

    # ── 3. CoverageValidator Tests ────────────────────────────────────────────
    def test_coverage_validator_100_percent_coverage_passes(self):
        val = CoverageValidator()
        output = AgentOutput(
            request_id="req_val1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            explanations=[
                ExplanationBlock(
                    id="exp_1",
                    content="Grammar Content",
                    targets=TargetTrace(learning_object_id="grammar:en:A1:PP.I_am:1", grammar_codes=["PP.I_am"]),
                ),
                ExplanationBlock(
                    id="exp_2",
                    content="Vocabulary Content",
                    targets=TargetTrace(learning_object_id="vocabulary:en:A2:ability:1", vocabulary_items=["Ability"]),
                ),
            ],
            coverage=[
                CoverageItem(learning_object_id="grammar:en:A1:PP.I_am:1", explained=True, example_covered=True, exercise_covered=True),
                CoverageItem(learning_object_id="vocabulary:en:A2:ability:1", explained=True, example_covered=True, exercise_covered=True),
            ],
        )
        res = val.validate(self.valid_input, output)
        self.assertTrue(res.passed)

    def test_coverage_validator_missing_target_fails(self):
        val = CoverageValidator()
        output = AgentOutput(
            request_id="req_val1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            explanations=[],  # No content tracing grammar target
            coverage=[],
        )
        res = val.validate(self.valid_input, output)
        self.assertFalse(res.passed)
        codes = [i.code for i in res.issues]
        self.assertIn("MISSING_GRAMMAR_COVERAGE", codes)

    # ── 4. CurriculumValidator Tests ──────────────────────────────────────────
    def test_curriculum_validator_unassigned_teaching_claim_fails(self):
        val = CurriculumValidator()
        output = AgentOutput(
            request_id="req_val1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            explanations=[ExplanationBlock(
                id="exp_1",
                content="Content",
                targets=TargetTrace(grammar_codes=["UNASSIGNED_CODE"]),
            )],
        )
        res = val.validate(self.valid_input, output)
        self.assertFalse(res.passed)
        self.assertEqual(res.issues[0].code, "UNAUTHORIZED_GRAMMAR_TARGET")

    # ── 5. ExerciseValidator Tests ───────────────────────────────────────────
    def test_exercise_validator_valid_exercise(self):
        val = ExerciseValidator()
        ex = ExerciseItem(
            id="ex_1",
            exercise_type="multiple_choice",
            prompt="Choose correct form:",
            options=["I am", "You are"],
            correct_answer="I am",
            targets=TargetTrace(grammar_codes=["PP.I_am"]),
        )
        output = AgentOutput(
            request_id="req_val1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            exercises=[ex],
        )
        res = val.validate(self.valid_input, output)
        self.assertTrue(res.passed)

    def test_exercise_validator_correct_answer_not_in_options_fails(self):
        val = ExerciseValidator()
        ex = ExerciseItem(
            id="ex_1",
            exercise_type="multiple_choice",
            prompt="Choose correct form:",
            options=["Option A", "Option B"],
            correct_answer="Option C",  # Not in options!
            targets=TargetTrace(grammar_codes=["PP.I_am"]),
        )
        output = AgentOutput(
            request_id="req_val1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            exercises=[ex],
        )
        res = val.validate(self.valid_input, output)
        self.assertFalse(res.passed)
        codes = [i.code for i in res.issues]
        self.assertIn("CORRECT_ANSWER_NOT_IN_OPTIONS", codes)

    def test_exercise_validator_duplicate_options_fails(self):
        val = ExerciseValidator()
        ex = ExerciseItem(
            id="ex_1",
            exercise_type="multiple_choice",
            prompt="Choose correct form:",
            options=["Option A", "Option A"],  # Duplicate!
            correct_answer="Option A",
            targets=TargetTrace(grammar_codes=["PP.I_am"]),
        )
        output = AgentOutput(
            request_id="req_val1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            exercises=[ex],
        )
        res = val.validate(self.valid_input, output)
        self.assertFalse(res.passed)
        codes = [i.code for i in res.issues]
        self.assertIn("DUPLICATE_EXERCISE_OPTIONS", codes)


if __name__ == "__main__":
    unittest.main()
