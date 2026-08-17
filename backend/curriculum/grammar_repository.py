# backend/curriculum/grammar_repository.py
"""
ROLE: GRAMMAR SOURCE REPOSITORY

This module provides deterministic read-only access to authoritative Grammar curriculum source data
extracted from the official Grammar Profile PDFs (A1–C2).
"""

import hashlib
import os
import re
from typing import Dict, List, Optional
import pdfplumber
import pypdf

from .source_models import CurriculumSourceDocument, GrammarSourceItem, IngestionReport


class GrammarRepositoryError(Exception):
    """Controlled exception for Grammar repository errors."""
    pass


class GrammarRepository:
    """
    Authoritative read-only repository for Grammar source data.
    """

    def __init__(self, search_directories: Optional[List[str]] = None):
        if search_directories is None:
            # Default search paths: backend/data/pdfs and workspace root
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            backend_data = os.path.join(base_dir, "backend", "data", "pdfs")
            english_data = os.path.join(base_dir, "English Grammar and vocabulary")
            search_directories = [backend_data, english_data, base_dir]

        self.search_directories = search_directories
        self._by_id: Dict[str, GrammarSourceItem] = {}
        self._by_code: Dict[str, List[GrammarSourceItem]] = {}
        self._by_level: Dict[str, List[GrammarSourceItem]] = {}
        self._documents: Dict[str, CurriculumSourceDocument] = {}
        self._reports: List[IngestionReport] = []
        self._initialized = False

        self.load_sources()

    def _calculate_sha256(self, filepath: str) -> str:
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def _find_pdf(self, filename: str) -> Optional[str]:
        for dir_path in self.search_directories:
            target = os.path.join(dir_path, filename)
            if os.path.isfile(target):
                return target
        return None

    def _parse_grammar_cell(self, cell_text: str):
        text = cell_text.strip()
        m_num = re.search(r'\b(\d+)\b', text)
        if not m_num:
            return None
        row_num = int(m_num.group(1))

        m_core = re.search(r'\b(A1-\(A2\)-B1|A1-A2|A1-B1|A1-B2|A2-B1|B1-B2|B2-C1|B1-C1|B2\*|A1|A2|B1|B2|C1|C2|N\/A)\b', text)
        core_inv = m_core.group(1) if m_core else "N/A"

        # Match shorthand code immediately following row number e.g. '85 CL_after.etc' or '1 PP.I_am'
        m_code = re.search(r'\b\d+\s+([A-Za-z0-9_\.-]+)\b', text)
        if m_code and len(m_code.group(1)) > 1:
            code = m_code.group(1)
        else:
            m_code_fallback = re.search(r'\b([A-Z0-9_]+(?:\.[A-Za-z0-9_\'-]+)+)\b', text)
            code = m_code_fallback.group(1) if m_code_fallback else ""

        # Extract label
        label = text
        if code and code in text:
            idx = text.find(code) + len(code)
            label = text[idx:].strip()
            if m_core and m_core.group(0) in label:
                c_idx = label.rfind(m_core.group(0))
                label = label[:c_idx].strip()

        return row_num, code, label, core_inv

    def load_sources(self):
        if self._initialized:
            return

        levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        missing_files = []

        for level in levels:
            filename = f"Grammar_Profile_Level_{level}.pdf"
            filepath = self._find_pdf(filename)
            if not filepath:
                missing_files.append(filename)
                continue

            sha256 = self._calculate_sha256(filepath)
            source_id = f"doc:grammar:en:{level}"

            reader = pypdf.PdfReader(filepath)
            page_count = len(reader.pages)

            doc = CurriculumSourceDocument(
                source_id=source_id,
                language="en",
                source_type="grammar",
                document_level=level,
                filename=filename,
                file_path=filepath,
                sha256=sha256,
                page_count=page_count,
            )
            self._documents[source_id] = doc
            self._by_level[level] = []

            parsed_items = 0
            issues = []

            with pdfplumber.open(filepath) as pdf:
                for p_idx, page in enumerate(pdf.pages, 1):
                    tables = page.extract_tables()
                    for t in tables:
                        for row in t:
                            if not row or not any(row):
                                continue
                            full_text = " ".join([c.strip().replace("\n", " ") for c in row if c])
                            if "SHORTHAND" in full_text or "GRAMMATICAL" in full_text or full_text in ("#", "# SHORTHAND CODE"):
                                continue

                            res = self._parse_grammar_cell(full_text)
                            if not res or not res[1]:
                                issues.append(f"Page {p_idx}: Could not extract code from row text: {repr(full_text)}")
                                continue

                            row_num, code, label, core_inv = res
                            item_id = f"grammar:en:{level}:{code}:{row_num}"

                            item = GrammarSourceItem(
                                source_item_id=item_id,
                                grammar_code=code,
                                label=label or code,
                                document_level=level,
                                core_inventory_raw=core_inv,
                                source_id=source_id,
                                page=p_idx,
                                row_number=row_num,
                                raw_text=full_text,
                            )

                            self._by_id[item_id] = item
                            if code not in self._by_code:
                                self._by_code[code] = []
                            self._by_code[code].append(item)
                            self._by_level[level].append(item)
                            parsed_items += 1

            report = IngestionReport(
                filename=filename,
                source_id=source_id,
                source_type="grammar",
                document_level=level,
                page_count=page_count,
                parsed_count=parsed_items,
                issue_count=len(issues),
                issues=issues,
            )
            self._reports.append(report)

        if missing_files:
            raise GrammarRepositoryError(f"Missing required Grammar PDF source files: {missing_files}")

        self._initialized = True

    def get_by_id(self, source_item_id: str) -> Optional[GrammarSourceItem]:
        return self._by_id.get(source_item_id)

    def get_by_code(self, grammar_code: str) -> Optional[GrammarSourceItem]:
        matches = self._by_code.get(grammar_code, [])
        if not matches:
            return None
        return matches[0]

    def find_all_by_code(self, grammar_code: str) -> List[GrammarSourceItem]:
        return self._by_code.get(grammar_code, [])

    def exists(self, grammar_code: str) -> bool:
        return grammar_code in self._by_code and len(self._by_code[grammar_code]) > 0

    def list_by_level(self, level: str) -> List[GrammarSourceItem]:
        return self._by_level.get(level, [])

    def list_all(self) -> List[GrammarSourceItem]:
        return list(self._by_id.values())

    def get_source_document(self, source_id: str) -> Optional[CurriculumSourceDocument]:
        return self._documents.get(source_id)

    def list_source_documents(self) -> List[CurriculumSourceDocument]:
        return list(self._documents.values())

    def get_ingestion_reports(self) -> List[IngestionReport]:
        return self._reports
