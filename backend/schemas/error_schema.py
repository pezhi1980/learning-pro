# backend/schemas/error_schema.py
"""
ROLE: STANDARD ERROR CONTRACT

This module defines structured errors for curriculum and content generation failures.

CORE RULES
1. Errors must be machine-readable.
2. Errors should distinguish between specific failure types in the generation pipeline.
3. Errors must contain context without exposing sensitive system secrets or credentials.
4. Validation failures remain explicit, structured, and non-silent.
"""

from enum import Enum
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ErrorType(str, Enum):
    invalid_input = "invalid_input"
    missing_source = "missing_source"
    unknown_grammar_code = "unknown_grammar_code"
    unknown_vocabulary_item = "unknown_vocabulary_item"
    unknown_vocabulary_sense = "unknown_vocabulary_sense"
    agent_generation_failure = "agent_generation_failure"
    invalid_agent_output = "invalid_agent_output"
    coverage_failure = "coverage_failure"
    curriculum_violation = "curriculum_violation"
    exercise_validation_failure = "exercise_validation_failure"
    conflicting_input = "conflicting_input"
    internal_error = "internal_error"


class ErrorDetail(BaseModel):
    field: Optional[str] = None
    target_id: Optional[str] = None
    exercise_id: Optional[str] = None
    expected: Optional[Any] = None
    received: Optional[Any] = None


class BackendError(BaseModel):
    request_id: Optional[str] = None
    error_type: ErrorType
    error_code: str
    message: str
    details: List[ErrorDetail] = Field(default_factory=list)
    retryable: bool = False
