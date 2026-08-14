# backend/schemas/agent_input.py
"""
ROLE: AGENT INPUT CONTRACT

This module defines the exact structured input accepted by the Content Generation Agent.

CORE RULES
1. Agent input must be explicit and structured.
2. The Agent must never be required to infer its own curriculum targets.
3. Input should clearly distinguish target content, allowed supporting content, and runtime constraints.
4. Required fields must not silently default when omission could change curriculum meaning.
5. This schema validates DATA SHAPE. Curriculum authority is implemented separately.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class GenerationMode(str, Enum):
    grammar_micro_lesson = "grammar_micro_lesson"
    vocabulary_lesson = "vocabulary_lesson"
    grammar_repair = "grammar_repair"
    vocabulary_repair = "vocabulary_repair"
    smart_review = "smart_review"
    mixed_practice = "mixed_practice"


class TaskDifficulty(str, Enum):
    recognition = "recognition"
    selection = "selection"
    controlled_recall = "controlled_recall"
    construction = "construction"
    production = "production"


class SourceReference(BaseModel):
    source_id: str
    source_type: str
    level: Optional[str] = None
    source_item_id: str
    page: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class GrammarTarget(BaseModel):
    learning_object_id: str
    grammar_code: str
    label: str
    source: SourceReference


class VocabularySenseTarget(BaseModel):
    sense_id: str
    guideword: Optional[str] = None
    definition_hint: Optional[str] = None
    source: SourceReference


class VocabularyTarget(BaseModel):
    learning_object_id: str
    item: str
    part_of_speech: Optional[str] = None
    source: SourceReference
    senses: List[VocabularySenseTarget] = Field(default_factory=list)


class LearnerErrorContext(BaseModel):
    error_code: str
    description: Optional[str] = None
    occurrences: Optional[int] = None


class GenerationConstraints(BaseModel):
    example_count: Optional[int] = None
    exercise_count: Optional[int] = None
    include_breakdown: Optional[bool] = None
    max_explanation_length: Optional[int] = None


class AgentInput(BaseModel):
    request_id: str
    target_language: str
    native_language: Optional[str] = None
    generation_mode: GenerationMode

    target_grammar: List[GrammarTarget] = Field(default_factory=list)
    allowed_grammar_codes: List[str] = Field(default_factory=list)

    target_vocabulary: List[VocabularyTarget] = Field(default_factory=list)
    allowed_vocabulary_items: List[str] = Field(default_factory=list)
    allowed_vocabulary_sense_ids: List[str] = Field(default_factory=list)

    task_difficulty: TaskDifficulty
    learner_errors: List[LearnerErrorContext] = Field(default_factory=list)
    constraints: GenerationConstraints = Field(default_factory=GenerationConstraints)


class CurriculumAssignmentRequest(BaseModel):
    request_id: str
    target_language: str = "en"
    native_language: Optional[str] = None
    generation_mode: GenerationMode
    task_difficulty: TaskDifficulty

    target_grammar_ids: List[str] = Field(default_factory=list)
    allowed_grammar_ids: List[str] = Field(default_factory=list)

    target_vocabulary_ids: List[str] = Field(default_factory=list)
    allowed_vocabulary_ids: List[str] = Field(default_factory=list)

    target_vocabulary_sense_ids: List[str] = Field(default_factory=list)
    allowed_vocabulary_sense_ids: List[str] = Field(default_factory=list)

    learner_errors: List[LearnerErrorContext] = Field(default_factory=list)
    constraints: GenerationConstraints = Field(default_factory=GenerationConstraints)

