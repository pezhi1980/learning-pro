# backend/curriculum/source_models.py
"""
ROLE: CURRICULUM SOURCE DATA MODELS

This module defines normalized internal data structures representing curriculum source information.
It must preserve original identity, traceability, and exact source values extracted from PDFs.
"""

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


class CurriculumSourceDocument(BaseModel):
    source_id: str
    language: str = "en"
    source_type: Literal["grammar", "vocabulary"]
    document_level: str
    filename: str
    file_path: str
    sha256: Optional[str] = None
    page_count: Optional[int] = None


class GrammarSourceItem(BaseModel):
    source_item_id: str
    grammar_code: str
    label: str
    document_level: str
    core_inventory_raw: Optional[str] = None
    source_id: str
    page: Optional[int] = None
    row_number: Optional[int] = None
    raw_text: Optional[str] = None


class VocabularySourceItem(BaseModel):
    source_item_id: str
    lexeme: str
    document_level: str
    part_of_speech: Optional[str] = None
    guideword: Optional[str] = None
    source_id: str
    page: Optional[int] = None
    row_number: Optional[int] = None
    raw_text: Optional[str] = None


class IngestionReport(BaseModel):
    filename: str
    source_id: str
    source_type: str
    document_level: str
    page_count: int
    parsed_count: int
    issue_count: int = 0
    issues: List[str] = Field(default_factory=list)
