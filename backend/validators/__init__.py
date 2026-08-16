# backend/validators/__init__.py
"""
Backend Validators Package
───────────────────────────
Exports all 5 deterministic content pipeline validators:
1. OutputValidator
2. SourceValidator
3. CoverageValidator
4. CurriculumValidator
5. ExerciseValidator
"""

from typing import Any, Dict, Optional, Tuple
from backend.curriculum import CurriculumService
from backend.schemas.agent_input import AgentInput
from backend.schemas.agent_output import AgentOutput
from backend.schemas.lesson_schema import ValidationResult
from .coverage_validator import CoverageValidator
from .curriculum_validator import CurriculumValidator
from .exercise_validator import ExerciseValidator
from .output_validator import OutputValidator
from .source_validator import SourceValidator
from .grammar_content_validator import GrammarContentValidator


def validate_all(
    input_data: AgentInput,
    raw_or_parsed_output: Any,
    curriculum_service: Optional[CurriculumService] = None,
) -> Tuple[Optional[AgentOutput], Dict[str, ValidationResult]]:
    """
    Runs the complete 5-stage validation pipeline in strict order:
    1. OutputValidator
    2. SourceValidator
    3. CoverageValidator
    4. CurriculumValidator
    5. ExerciseValidator

    Returns tuple of (parsed AgentOutput or None, dict of {validator_name: ValidationResult}).
    If OutputValidator fails, downstream validators are skipped for safety.
    """
    results: Dict[str, ValidationResult] = {}

    # Stage 1: OutputValidator
    output_val = OutputValidator()
    agent_output, res_output = output_val.validate(raw_or_parsed_output)
    results["output_validator"] = res_output

    if not res_output.passed or agent_output is None:
        return None, results

    # Stage 2: SourceValidator
    source_val = SourceValidator(curriculum_service=curriculum_service)
    results["source_validator"] = source_val.validate(agent_output)

    # Stage 3: CoverageValidator
    coverage_val = CoverageValidator()
    results["coverage_validator"] = coverage_val.validate(input_data, agent_output)

    # Stage 4: CurriculumValidator
    curriculum_val = CurriculumValidator()
    results["curriculum_validator"] = curriculum_val.validate(input_data, agent_output)

    # Stage 5: ExerciseValidator
    exercise_val = ExerciseValidator()
    results["exercise_validator"] = exercise_val.validate(input_data, agent_output)

    return agent_output, results


__all__ = [
    "OutputValidator",
    "SourceValidator",
    "CoverageValidator",
    "CurriculumValidator",
    "ExerciseValidator",
    "validate_all",
]
