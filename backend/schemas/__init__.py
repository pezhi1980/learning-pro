# backend/schemas/__init__.py
"""
Backend Schemas Package
──────────────────────
Exports all public schema models and contracts for Backend content pipeline.
"""

from .agent_input import (
    AgentInput,
    CurriculumAssignmentRequest,
    GenerationConstraints,
    GenerationMode,
    GrammarTarget,
    LearnerErrorContext,
    SourceReference,
    TaskDifficulty,
    VocabularySenseTarget,
    VocabularyTarget,
)
from .agent_output import (
    AgentOutput,
    CoverageItem,
    ExampleItem,
    ExerciseItem,
    ExplanationBlock,
    TargetTrace,
)
from .error_schema import (
    BackendError,
    ErrorDetail,
    ErrorType,
)
from .lesson_schema import (
    Lesson,
    LessonStatus,
    ValidationIssue,
    ValidationResult,
)

__all__ = [
    # agent_input
    "GenerationMode",
    "TaskDifficulty",
    "SourceReference",
    "GrammarTarget",
    "VocabularySenseTarget",
    "VocabularyTarget",
    "LearnerErrorContext",
    "GenerationConstraints",
    "AgentInput",
    "CurriculumAssignmentRequest",
    # agent_output
    "TargetTrace",
    "ExplanationBlock",
    "ExampleItem",
    "ExerciseItem",
    "CoverageItem",
    "AgentOutput",
    # lesson_schema
    "LessonStatus",
    "ValidationIssue",
    "ValidationResult",
    "Lesson",
    # error_schema
    "ErrorType",
    "ErrorDetail",
    "BackendError",
]
