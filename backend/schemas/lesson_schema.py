# backend/schemas/lesson_schema.py
"""
ROLE: LESSON DATA CONTRACT

This module defines the canonical Backend representation of a generated lesson AFTER generation.

CORE RULES
1. The lesson model must be independent from raw AI response formatting.
2. A Lesson must NOT automatically become "validated" simply because AgentOutput successfully parses.
3. The lesson object represents the lifecycle of generated content across validation stages.
"""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from .agent_input import GenerationMode, GrammarTarget, VocabularyTarget
from .agent_output import AgentOutput


class LessonStatus(str, Enum):
    generated = "generated"
    validating = "validating"
    validated = "validated"
    rejected = "rejected"


class ValidationIssue(BaseModel):
    validator: str
    code: str
    message: str
    target_id: Optional[str] = None
    exercise_id: Optional[str] = None


class ValidationResult(BaseModel):
    passed: bool
    issues: List[ValidationIssue] = Field(default_factory=list)


class Lesson(BaseModel):
    lesson_id: str
    request_id: str
    target_language: str
    native_language: Optional[str] = None
    generation_mode: GenerationMode

    assigned_grammar: List[GrammarTarget] = Field(default_factory=list)
    assigned_vocabulary: List[VocabularyTarget] = Field(default_factory=list)

    content: AgentOutput

    status: LessonStatus = LessonStatus.generated
    validation_results: Dict[str, ValidationResult] = Field(default_factory=dict)
