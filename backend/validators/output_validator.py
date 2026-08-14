# backend/validators/output_validator.py
"""
ROLE: STRUCTURAL OUTPUT VALIDATOR

This validator verifies the structural integrity of Content Generation Agent output
against the AgentOutput Pydantic schema before deeper curriculum validation.

CORE RULES:
1. Validate Agent output structure before curriculum validation.
2. Candidate output must strictly conform to AgentOutput schema.
3. Reject missing required fields, invalid types, forbidden additional fields (strict mode).
4. Reject malformed TargetTrace, CoverageItem, and ExerciseItem structures.
5. Structural validation does NOT make curriculum decisions.
"""

from typing import Any, Dict, Optional, Tuple
from pydantic import ValidationError

from backend.schemas.agent_output import AgentOutput
from backend.schemas.lesson_schema import ValidationIssue, ValidationResult


class OutputValidator:
    """
    Validates structural compliance of raw or parsed candidate Agent output.
    """

    def __init__(self, validator_name: str = "output_validator"):
        self.validator_name = validator_name

    def validate(self, raw_or_parsed_output: Any) -> Tuple[Optional[AgentOutput], ValidationResult]:
        """
        Validates raw dictionary or candidate object against AgentOutput.
        Returns tuple of (parsed AgentOutput or None, ValidationResult).
        """
        issues = []

        if isinstance(raw_or_parsed_output, AgentOutput):
            agent_output = raw_or_parsed_output
        elif isinstance(raw_or_parsed_output, dict):
            try:
                agent_output = AgentOutput(**raw_or_parsed_output)
            except ValidationError as ve:
                for err in ve.errors():
                    loc_str = ".".join(str(loc) for loc in err["loc"])
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="STRUCTURAL_VALIDATION_ERROR",
                            message=f"Field '{loc_str}': {err['msg']}",
                            target_id=loc_str,
                        )
                    )
                return None, ValidationResult(passed=False, issues=issues)
            except Exception as e:
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="JSON_PARSING_ERROR",
                        message=f"Failed to parse output structure: {str(e)}",
                    )
                )
                return None, ValidationResult(passed=False, issues=issues)
        else:
            issues.append(
                ValidationIssue(
                    validator=self.validator_name,
                    code="INVALID_OUTPUT_TYPE",
                    message=f"Expected dict or AgentOutput, received {type(raw_or_parsed_output).__name__}",
                )
            )
            return None, ValidationResult(passed=False, issues=issues)

        # Additional structural checks on TargetTrace and exercises
        for idx, exp in enumerate(agent_output.explanations):
            if not isinstance(exp.id, str) or not exp.id.strip():
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="EMPTY_EXPLANATION_ID",
                        message=f"Explanation at index {idx} has an empty or invalid ID",
                    )
                )

        for idx, ex in enumerate(agent_output.exercises):
            if not isinstance(ex.id, str) or not ex.id.strip():
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="EMPTY_EXERCISE_ID",
                        message=f"Exercise at index {idx} has an empty or invalid ID",
                        exercise_id=ex.id,
                    )
                )

        passed = len(issues) == 0
        return agent_output if passed else None, ValidationResult(passed=passed, issues=issues)
