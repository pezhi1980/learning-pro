# backend/curriculum/vocabulary_repository.py
"""
ROLE: VOCABULARY SOURCE REPOSITORY

This module provides deterministic read-only access to Vocabulary curriculum source data
extracted from official Vocabulary Level PDFs (A1–C2).
"""

import hashlib
import os
import re
from typing import Dict, List, Optional
import pypdf

from .source_models import CurriculumSourceDocument, IngestionReport, VocabularySourceItem


class VocabularyRepositoryError(Exception):
    """Controlled exception for Vocabulary repository errors."""
    pass


class VocabularyRepository:
    """
    Authoritative read-only repository for Vocabulary source data.
    """

    def __init__(self, search_directories: Optional[List[str]] = None):
        if search_directories is None:
            base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            backend_data = os.path.join(base_dir, "backend", "data", "pdfs")
            search_directories = [backend_data, base_dir]

        self.search_directories = search_directories
        self._by_id: Dict[str, VocabularySourceItem] = {}
        self._by_lexeme: Dict[str, List[VocabularySourceItem]] = {}
        self._by_level: Dict[str, List[VocabularySourceItem]] = {}
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

    def _slugify(self, text: str) -> str:
        s = text.lower().strip()
        s = re.sub(r'[^a-z0-9]+', '_', s)
        return s.strip('_')

    def load_sources(self):
        if self._initialized:
            return

        levels = ["A1", "A2", "B1", "B2", "C1", "C2"]
        missing_files = []

        for level in levels:
            filename = f"Vocabulary_Level_{level}.pdf"
            filepath = self._find_pdf(filename)
            if not filepath:
                missing_files.append(filename)
                continue

            sha256 = self._calculate_sha256(filepath)
            source_id = f"doc:vocabulary:en:{level}"

            reader = pypdf.PdfReader(filepath)
            page_count = len(reader.pages)

            doc = CurriculumSourceDocument(
                source_id=source_id,
                language="en",
                source_type="vocabulary",
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

            if level in ("A1", "A2", "B1", "B2"):
                # Parse A1-B2 Vocabulary (BASE WORD + PART OF SPEECH)
                for p_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if not text:
                        continue
                    lines = [l.strip() for l in text.split("\n") if l.strip()]
                    cleaned = [
                        l for l in lines
                        if l not in ("#", "BASE WORD", "PART OF SPEECH")
                        and not l.startswith("Engelish vocabulary")
                        and not l.startswith("English vocabulary")
                    ]

                    i = 0
                    while i < len(cleaned):
                        line = cleaned[i]
                        if line.isdigit():
                            row_num = int(line)
                            if i + 2 < len(cleaned) and not cleaned[i + 1].isdigit():
                                lexeme = cleaned[i + 1]
                                pos = cleaned[i + 2]
                                item_slug = self._slugify(lexeme)
                                item_id = f"vocabulary:en:{level}:{item_slug}:{row_num}"

                                item = VocabularySourceItem(
                                    source_item_id=item_id,
                                    lexeme=lexeme,
                                    document_level=level,
                                    part_of_speech=pos if pos else None,
                                    guideword=None,
                                    source_id=source_id,
                                    page=p_num,
                                    row_number=row_num,
                                    raw_text=f"{row_num} {lexeme} {pos}",
                                )
                                self._register_item(item, level)
                                parsed_items += 1
                                i += 3
                                continue
                            elif i + 1 < len(cleaned) and not cleaned[i + 1].isdigit():
                                lexeme = cleaned[i + 1]
                                item_slug = self._slugify(lexeme)
                                item_id = f"vocabulary:en:{level}:{item_slug}:{row_num}"

                                item = VocabularySourceItem(
                                    source_item_id=item_id,
                                    lexeme=lexeme,
                                    document_level=level,
                                    part_of_speech=None,
                                    guideword=None,
                                    source_id=source_id,
                                    page=p_num,
                                    row_number=row_num,
                                    raw_text=f"{row_num} {lexeme}",
                                )
                                self._register_item(item, level)
                                parsed_items += 1
                                i += 2
                                continue
                        # Try single-line match fallback
                        m = re.match(r"^(\d+)\s+(.+?)\s+([A-Z\s,\/]+)$", line)
                        if m:
                            row_num = int(m.group(1))
                            lexeme = m.group(2)
                            pos = m.group(3)
                            item_slug = self._slugify(lexeme)
                            item_id = f"vocabulary:en:{level}:{item_slug}:{row_num}"

                            item = VocabularySourceItem(
                                source_item_id=item_id,
                                lexeme=lexeme,
                                document_level=level,
                                part_of_speech=pos,
                                guideword=None,
                                source_id=source_id,
                                page=p_num,
                                row_number=row_num,
                                raw_text=line,
                            )
                            self._register_item(item, level)
                            parsed_items += 1
                            i += 1
                            continue
                        i += 1

            else:
                # Parse C1-C2 Vocabulary (BASE WORD + GUIDEWORD)
                for p_num, page in enumerate(reader.pages, 1):
                    text = page.extract_text()
                    if not text:
                        continue
                    lines = [l.strip() for l in text.split("\n") if l.strip()]
                    for line in lines:
                        if line in ("#", "BASE WORD", "GUIDEWORD", "# BASE WORD GUIDEWORD") or "vocabulary" in line.lower():
                            continue
                        m = re.match(r"^(\d+)\s+(.+?)\s+(.+)$", line)
                        if m:
                            row_num = int(m.group(1))
                            lexeme = m.group(2)
                            guideword = m.group(3)
                            if guideword == "—" or guideword == "":
                                guideword = None

                            item_slug = self._slugify(lexeme)
                            item_id = f"vocabulary:en:{level}:{item_slug}:{row_num}"

                            item = VocabularySourceItem(
                                source_item_id=item_id,
                                lexeme=lexeme,
                                document_level=level,
                                part_of_speech=None,
                                guideword=guideword,
                                source_id=source_id,
                                page=p_num,
                                row_number=row_num,
                                raw_text=line,
                            )
                            self._register_item(item, level)
                            parsed_items += 1
                        else:
                            issues.append(f"Page {p_num}: Unparsed line: {repr(line)}")

            report = IngestionReport(
                filename=filename,
                source_id=source_id,
                source_type="vocabulary",
                document_level=level,
                page_count=page_count,
                parsed_count=parsed_items,
                issue_count=len(issues),
                issues=issues,
            )
            self._reports.append(report)

        if missing_files:
            raise VocabularyRepositoryError(f"Missing required Vocabulary PDF source files: {missing_files}")

        self._initialized = True

    def _register_item(self, item: VocabularySourceItem, level: str):
        self._by_id[item.source_item_id] = item

        norm_lex = item.lexeme.lower().strip()
        if norm_lex not in self._by_lexeme:
            self._by_lexeme[norm_lex] = []
        self._by_lexeme[norm_lex].append(item)

        if level not in self._by_level:
            self._by_level[level] = []
        self._by_level[level].append(item)

    def get_by_id(self, source_item_id: str) -> Optional[VocabularySourceItem]:
        return self._by_id.get(source_item_id)

    def find_by_lexeme(self, lexeme: str) -> List[VocabularySourceItem]:
        norm_lex = lexeme.lower().strip()
        return self._by_lexeme.get(norm_lex, [])

    def find_by_lexeme_and_guideword(self, lexeme: str, guideword: str) -> Optional[VocabularySourceItem]:
        matches = self.find_by_lexeme(lexeme)
        norm_guide = guideword.lower().strip()
        for item in matches:
            if item.guideword and item.guideword.lower().strip() == norm_guide:
                return item
        return None

    def exists(self, source_item_id: str) -> bool:
        return source_item_id in self._by_id

    def list_by_level(self, level: str) -> List[VocabularySourceItem]:
        return self._by_level.get(level, [])

    def list_all(self) -> List[VocabularySourceItem]:
        return list(self._by_id.values())

    def get_source_document(self, source_id: str) -> Optional[CurriculumSourceDocument]:
        return self._documents.get(source_id)

    def list_source_documents(self) -> List[CurriculumSourceDocument]:
        return list(self._documents.values())

    def get_ingestion_reports(self) -> List[IngestionReport]:
        return self._reports
