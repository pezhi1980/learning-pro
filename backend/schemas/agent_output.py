# backend/schemas/agent_output.py
"""
ROLE: AGENT OUTPUT CONTRACT

This module defines the exact output structure permitted from the Content Generation Agent.

CORE RULES
1. Agent output must be machine-validated.
2. Output should contain only fields explicitly permitted by the schema.
3. Output should preserve traceability between generated content and assigned targets.
4. AgentOutput must NOT contain Agent-controlled validation fields (e.g. valid, approved).
5. Strict configuration is enabled to reject unexpected fields.
"""

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field
from .agent_input import GenerationMode


class TargetTrace(BaseModel):
    learning_object_id: Optional[str] = None
    grammar_codes: List[str] = Field(default_factory=list)
    vocabulary_items: List[str] = Field(default_factory=list)
    vocabulary_sense_ids: List[str] = Field(default_factory=list)


class ExplanationBlock(BaseModel):
    id: str
    title: Optional[str] = None
    content: str
    targets: TargetTrace


class ExampleItem(BaseModel):
    id: str
    sentence: str
    translation: Optional[str] = None
    breakdown: Optional[str] = None
    targets: TargetTrace


class ExerciseItem(BaseModel):
    id: str
    exercise_type: str
    prompt: str
    options: List[str] = Field(default_factory=list)
    correct_answer: Any
    explanation: Optional[str] = None
    targets: TargetTrace


class CoverageItem(BaseModel):
    learning_object_id: str
    explained: bool
    example_covered: bool
    exercise_covered: bool


class AgentOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    request_id: str
    generation_mode: GenerationMode
    title: Optional[str] = None

    explanations: List[ExplanationBlock] = Field(default_factory=list)
    examples: List[ExampleItem] = Field(default_factory=list)
    exercises: List[ExerciseItem] = Field(default_factory=list)

    coverage: List[CoverageItem] = Field(default_factory=list)
