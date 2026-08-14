# backend/tests/test_schemas.py
"""
Lightweight schema tests for backend.schemas models.
"""

import sys
import os
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from pydantic import ValidationError
from backend.schemas import (
    AgentInput,
    AgentOutput,
    BackendError,
    CoverageItem,
    ErrorDetail,
    ErrorType,
    ExampleItem,
    ExerciseItem,
    ExplanationBlock,
    GenerationConstraints,
    GenerationMode,
    GrammarTarget,
    Lesson,
    LessonStatus,
    SourceReference,
    TargetTrace,
    TaskDifficulty,
    VocabularySenseTarget,
    VocabularyTarget,
)


class TestSchemas(unittest.TestCase):

    def test_1_valid_agent_input_creation(self):
        source = SourceReference(
            source_id="pdf_a1",
            source_type="pdf",
            level="A1",
            source_item_id="gram_01",
        )
        grammar_target = GrammarTarget(
            learning_object_id="lo_g1",
            grammar_code="verb_to_be",
            label="Verb To Be Present",
            source=source,
        )
        agent_input = AgentInput(
            request_id="req_001",
            target_language="en",
            native_language="fa",
            generation_mode=GenerationMode.grammar_micro_lesson,
            target_grammar=[grammar_target],
            task_difficulty=TaskDifficulty.controlled_recall,
        )
        self.assertEqual(agent_input.request_id, "req_001")
        self.assertEqual(agent_input.generation_mode, GenerationMode.grammar_micro_lesson)
        self.assertEqual(len(agent_input.target_grammar), 1)

    def test_2_invalid_generation_mode_rejected(self):
        with self.assertRaises(ValidationError):
            AgentInput(
                request_id="req_002",
                target_language="en",
                generation_mode="invalid_mode_name",  # Should raise ValidationError
                task_difficulty=TaskDifficulty.selection,
            )

    def test_3_vocabulary_target_multiple_explicit_senses(self):
        source1 = SourceReference(source_id="v_pdf", source_type="pdf", source_item_id="item_bank")
        source2 = SourceReference(source_id="v_pdf", source_type="pdf", source_item_id="item_bank_s2")
        
        sense1 = VocabularySenseTarget(sense_id="bank_financial", guideword="financial institution", source=source1)
        sense2 = VocabularySenseTarget(sense_id="bank_river", guideword="side of river", source=source2)
        
        vocab = VocabularyTarget(
            learning_object_id="lo_v1",
            item="bank",
            part_of_speech="noun",
            source=source1,
            senses=[sense1, sense2],
        )
        self.assertEqual(len(vocab.senses), 2)
        self.assertEqual(vocab.senses[0].sense_id, "bank_financial")
        self.assertEqual(vocab.senses[1].sense_id, "bank_river")

    def test_4_agent_output_preserves_target_traceability(self):
        trace = TargetTrace(
            learning_object_id="lo_g1",
            grammar_codes=["verb_to_be"],
            vocabulary_items=["be"],
            vocabulary_sense_ids=["be_exist"],
        )
        exp = ExplanationBlock(id="exp_1", title="Intro", content="Explanation content", targets=trace)
        output = AgentOutput(
            request_id="req_003",
            generation_mode=GenerationMode.grammar_micro_lesson,
            explanations=[exp],
        )
        self.assertEqual(output.explanations[0].targets.learning_object_id, "lo_g1")
        self.assertIn("verb_to_be", output.explanations[0].targets.grammar_codes)

    def test_5_unexpected_agent_output_properties_rejected(self):
        with self.assertRaises(ValidationError):
            AgentOutput(
                request_id="req_004",
                generation_mode=GenerationMode.grammar_micro_lesson,
                valid=True,  # Unexpected extra field -> forbidden by extra="forbid"
            )

    def test_6_lesson_exists_in_generated_state(self):
        trace = TargetTrace(learning_object_id="lo_g1")
        output = AgentOutput(request_id="req_005", generation_mode=GenerationMode.grammar_micro_lesson)
        lesson = Lesson(
            lesson_id="les_001",
            request_id="req_005",
            target_language="en",
            generation_mode=GenerationMode.grammar_micro_lesson,
            content=output,
        )
        self.assertEqual(lesson.status, LessonStatus.generated)
        self.assertNotEqual(lesson.status, LessonStatus.validated)

    def test_7_backend_error_serialization(self):
        err = BackendError(
            request_id="req_006",
            error_type=ErrorType.missing_source,
            error_code="ERR_SRC_404",
            message="Source PDF reference not found",
            details=[ErrorDetail(field="grammar_code", target_id="TA.MISSING")],
            retryable=False,
        )
        err_dict = err.model_dump()
        self.assertEqual(err_dict["error_type"], "missing_source")
        self.assertEqual(err_dict["details"][0]["target_id"], "TA.MISSING")


if __name__ == "__main__":
    unittest.main()
