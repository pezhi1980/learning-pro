# backend/tests/test_assignment.py
"""
Unit tests for backend.services.curriculum_assignment_service.
"""

import os
import sys
import unittest

# Add both backend parent directory and backend directory to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.schemas import (
    AgentInput,
    CurriculumAssignmentRequest,
    GenerationMode,
    TaskDifficulty,
)
from backend.services import (
    CurriculumAssignmentError,
    CurriculumAssignmentService,
)


class TestCurriculumAssignmentService(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.assignment_service = CurriculumAssignmentService()

    def test_1_valid_grammar_source_id_resolves(self):
        req = CurriculumAssignmentRequest(
            request_id="req_g1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )
        agent_input = self.assignment_service.build_agent_input(req)
        self.assertEqual(len(agent_input.target_grammar), 1)
        self.assertEqual(agent_input.target_grammar[0].grammar_code, "PP.I_am")
        self.assertEqual(agent_input.target_grammar[0].source.source_type, "grammar")

    def test_2_unknown_grammar_source_id_fails(self):
        req = CurriculumAssignmentRequest(
            request_id="req_g2",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["grammar:en:A1:NON_EXISTENT_CODE:999"],
        )
        with self.assertRaises(CurriculumAssignmentError) as ctx:
            self.assignment_service.build_agent_input(req)
        self.assertIn("not found", ctx.exception.message)

    def test_3_valid_vocabulary_source_item_resolves(self):
        req = CurriculumAssignmentRequest(
            request_id="req_v1",
            generation_mode=GenerationMode.vocabulary_lesson,
            task_difficulty=TaskDifficulty.selection,
            target_vocabulary_ids=["vocabulary:en:A2:ability:1"],
        )
        agent_input = self.assignment_service.build_agent_input(req)
        self.assertEqual(len(agent_input.target_vocabulary), 1)
        self.assertEqual(agent_input.target_vocabulary[0].item, "Ability")

    def test_4_vocabulary_part_of_speech_preserved(self):
        target = self.assignment_service.resolve_vocabulary_target("vocabulary:en:A2:ability:1")
        self.assertEqual(target.part_of_speech, "NOUN")

    def test_5_vocabulary_guideword_preserved(self):
        target = self.assignment_service.resolve_vocabulary_target("vocabulary:en:C1:abandon:1")
        self.assertEqual(len(target.senses), 1)
        self.assertEqual(target.senses[0].guideword, "STOP DOING")

    def test_6_multiple_senses_not_automatically_merged(self):
        # Acknowledge has two C1 senses: ACCEPT (row 16) and SAY RECEIVED (row 17)
        t1 = self.assignment_service.resolve_vocabulary_target("vocabulary:en:C1:acknowledge:16")
        t2 = self.assignment_service.resolve_vocabulary_target("vocabulary:en:C1:acknowledge:17")
        self.assertNotEqual(t1.learning_object_id, t2.learning_object_id)
        self.assertEqual(t1.senses[0].guideword, "ACCEPT")
        self.assertEqual(t2.senses[0].guideword, "SAY RECEIVED")

    def test_7_target_vocabulary_sense_unrelated_lexeme_fails(self):
        with self.assertRaises(CurriculumAssignmentError):
            self.assignment_service.resolve_vocabulary_sense(
                identifier="vocabulary:en:C1:abandon:1",
                parent_lexeme="DifferentWord",
            )

    def test_8_allowed_grammar_kept_separate_from_target_grammar(self):
        req = CurriculumAssignmentRequest(
            request_id="req_sep1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
            allowed_grammar_ids=["grammar:en:A1:DT.a.an:37"],
        )
        agent_input = self.assignment_service.build_agent_input(req)
        self.assertEqual(len(agent_input.target_grammar), 1)
        self.assertEqual(len(agent_input.allowed_grammar_codes), 1)
        self.assertEqual(agent_input.allowed_grammar_codes[0], "DT.a.an")
        self.assertNotIn("DT.a.an", [g.grammar_code for g in agent_input.target_grammar])

    def test_9_allowed_vocabulary_kept_separate_from_target_vocabulary(self):
        req = CurriculumAssignmentRequest(
            request_id="req_sep2",
            generation_mode=GenerationMode.vocabulary_lesson,
            task_difficulty=TaskDifficulty.selection,
            target_vocabulary_ids=["vocabulary:en:A2:ability:1"],
            allowed_vocabulary_ids=["vocabulary:en:A1:about:2"],
        )
        agent_input = self.assignment_service.build_agent_input(req)
        self.assertEqual(len(agent_input.target_vocabulary), 1)
        self.assertEqual(len(agent_input.allowed_vocabulary_items), 1)
        self.assertEqual(agent_input.allowed_vocabulary_items[0], "About")

    def test_10_exact_duplicate_target_ids_do_not_produce_duplicates(self):
        req = CurriculumAssignmentRequest(
            request_id="req_dup1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1", "grammar:en:A1:PP.I_am:1"],
        )
        agent_input = self.assignment_service.build_agent_input(req)
        self.assertEqual(len(agent_input.target_grammar), 1)

    def test_11_different_source_item_ids_surface_content_not_merged(self):
        # Acknowledge ACCEPT vs SAY RECEIVED
        req = CurriculumAssignmentRequest(
            request_id="req_diff1",
            generation_mode=GenerationMode.vocabulary_lesson,
            task_difficulty=TaskDifficulty.selection,
            target_vocabulary_ids=["vocabulary:en:C1:acknowledge:16", "vocabulary:en:C1:acknowledge:17"],
        )
        agent_input = self.assignment_service.build_agent_input(req)
        self.assertEqual(len(agent_input.target_vocabulary), 2)

    def test_12_grammar_code_ambiguity_not_arbitrarily_resolved(self):
        # PP.aren exists in multiple levels/rows
        with self.assertRaises(CurriculumAssignmentError) as ctx:
            self.assignment_service.resolve_grammar_target("PP.aren")
        self.assertIn("ambiguous", ctx.exception.message)

    def test_13_grammar_micro_lesson_without_grammar_target_fails(self):
        req = CurriculumAssignmentRequest(
            request_id="req_fail1",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.recognition,
            target_grammar_ids=[],
        )
        with self.assertRaises(CurriculumAssignmentError):
            self.assignment_service.build_agent_input(req)

    def test_14_vocabulary_lesson_without_vocabulary_target_fails(self):
        req = CurriculumAssignmentRequest(
            request_id="req_fail2",
            generation_mode=GenerationMode.vocabulary_lesson,
            task_difficulty=TaskDifficulty.recognition,
            target_vocabulary_ids=[],
        )
        with self.assertRaises(CurriculumAssignmentError):
            self.assignment_service.build_agent_input(req)

    def test_15_no_ai_or_network_dependency_exists(self):
        req = CurriculumAssignmentRequest(
            request_id="req_no_ai",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.construction,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )
        agent_input = self.assignment_service.build_agent_input(req)
        self.assertIsInstance(agent_input, AgentInput)

    def test_16_agent_input_passes_pydantic_validation(self):
        req = CurriculumAssignmentRequest(
            request_id="req_valid_pyd",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.production,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )
        agent_input = self.assignment_service.build_agent_input(req)
        dumped = agent_input.model_dump()
        reconstructed = AgentInput(**dumped)
        self.assertEqual(reconstructed.request_id, "req_valid_pyd")

    def test_17_every_source_reference_comes_from_authoritative_curriculum(self):
        req = CurriculumAssignmentRequest(
            request_id="req_auth_src",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.recognition,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )
        agent_input = self.assignment_service.build_agent_input(req)
        src = agent_input.target_grammar[0].source
        self.assertEqual(src.source_id, "doc:grammar:en:A1")
        self.assertEqual(src.source_type, "grammar")
        self.assertEqual(src.source_item_id, "grammar:en:A1:PP.I_am:1")


if __name__ == "__main__":
    unittest.main()
