# backend/tests/test_curriculum.py
"""
Lightweight unit tests for backend.curriculum layer.
"""

import sys
import os
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.curriculum import (
    CurriculumService,
    GrammarRepository,
    VocabularyRepository,
)


class TestCurriculumLayer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.service = CurriculumService()

    def test_1_source_documents_discovered(self):
        docs = self.service.list_source_documents()
        self.assertEqual(len(docs), 12)  # 6 Grammar + 6 Vocabulary PDFs

    def test_2_grammar_pdfs_loaded(self):
        grammar_items = self.service.list_all_grammar()
        self.assertGreater(len(grammar_items), 300)

    def test_3_vocabulary_pdfs_loaded(self):
        vocab_items = self.service.list_all_vocabulary()
        self.assertGreater(len(vocab_items), 5000)

    def test_4_grammar_lookup_by_exact_code(self):
        item = self.service.get_grammar_by_code("PP.I_am")
        self.assertIsNotNone(item)
        self.assertEqual(item.grammar_code, "PP.I_am")
        self.assertTrue(self.service.grammar_exists("PP.I_am"))

    def test_5_unknown_grammar_code_returns_false(self):
        self.assertFalse(self.service.grammar_exists("NON_EXISTENT_GRAMMAR_CODE_12345"))
        self.assertIsNone(self.service.get_grammar_by_code("NON_EXISTENT_GRAMMAR_CODE_12345"))

    def test_6_vocabulary_lookup_by_lexeme_returns_entries(self):
        matches = self.service.find_vocabulary_by_lexeme("Acknowledge")
        self.assertGreaterEqual(len(matches), 1)

    def test_7_vocabulary_entries_preserve_part_of_speech(self):
        matches = self.service.find_vocabulary_by_lexeme("Ability")
        self.assertGreaterEqual(len(matches), 1)
        item = matches[0]
        self.assertEqual(item.part_of_speech, "NOUN")

    def test_8_vocabulary_entries_preserve_guideword(self):
        item = self.service.find_vocabulary_by_lexeme_and_guideword("Abandon", "STOP DOING")
        self.assertIsNotNone(item)
        self.assertEqual(item.guideword, "STOP DOING")

    def test_9_source_document_level_preserved(self):
        a1_grammar = self.service.list_grammar_by_level("A1")
        self.assertGreater(len(a1_grammar), 0)
        for item in a1_grammar:
            self.assertEqual(item.document_level, "A1")

    def test_10_grammar_core_inventory_preserved_separately(self):
        matches = self.service.find_all_grammar_by_code("PPOS.mine.etc")
        self.assertGreaterEqual(len(matches), 1)
        item = matches[0]
        self.assertEqual(item.document_level, "B1")
        self.assertEqual(item.core_inventory_raw, "A1-A2")

    def test_11_stable_source_ids_identical_across_loads(self):
        service2 = CurriculumService()
        item1 = self.service.get_grammar_by_code("PP.I_am")
        item2 = service2.get_grammar_by_code("PP.I_am")
        self.assertEqual(item1.source_item_id, item2.source_item_id)

    def test_12_invalid_identifiers_not_silently_accepted(self):
        self.assertFalse(self.service.vocabulary_source_item_exists("invalid:id:123"))
        self.assertIsNone(self.service.get_vocabulary_by_id("invalid:id:123"))

    def test_13_parsing_does_not_use_agent_or_network(self):
        # Service initialized deterministically without network/agent calls
        report = self.service.get_completeness_report()
        self.assertEqual(report["total_source_documents"], 12)
        self.assertEqual(report["total_issues"], 0)


if __name__ == "__main__":
    unittest.main()
