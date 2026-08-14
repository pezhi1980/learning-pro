# backend/validators/exercise_validator.py
"""
ROLE: EXERCISE VALIDATOR

This validator performs deterministic validation of generated exercise structures,
options integrity, correct answers, and exercise curriculum targeting.

CORE RULES:
1. Every exercise must have a unique ID.
2. Every exercise must identify its intended curriculum target.
3. Tested targets must belong to Backend-assigned curriculum.
4. Correct answer must exist and be valid.
5. Choice-based exercises: correct_answer must match an option string.
6. Duplicate options causing structural ambiguity are rejected.
7. Empty prompts or empty options fail.
8. No structural ambiguity permitted.
"""

from typing import Set
from backend.schemas.agent_input import AgentInput
from backend.schemas.agent_output import AgentOutput
from backend.schemas.lesson_schema import ValidationIssue, ValidationResult


class ExerciseValidator:
    """
    Validates exercise structural safety, option integrity, correct answers, and targets.
    """

    def __init__(self, validator_name: str = "exercise_validator"):
        self.validator_name = validator_name

    def validate(self, input_data: AgentInput, output: AgentOutput) -> ValidationResult:
        issues = []
        seen_exercise_ids: Set[str] = set()

        assigned_grammar_codes: Set[str] = {g.grammar_code for g in input_data.target_grammar}
        assigned_vocab_items: Set[str] = {v.item.lower().strip() for v in input_data.target_vocabulary}
        assigned_sense_ids: Set[str] = set()
        for v in input_data.target_vocabulary:
            for s in v.senses:
                assigned_sense_ids.add(s.sense_id)

        for idx, ex in enumerate(output.exercises):
            ex_id = ex.id

            # 1. Unique Exercise ID check
            if ex_id in seen_exercise_ids:
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="DUPLICATE_EXERCISE_ID",
                        message=f"Duplicate exercise ID '{ex_id}' at index {idx}",
                        exercise_id=ex_id,
                    )
                )
            seen_exercise_ids.add(ex_id)

            # 2. Non-empty Prompt check
            if not ex.prompt or not str(ex.prompt).strip():
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="EMPTY_EXERCISE_PROMPT",
                        message=f"Exercise '{ex_id}' has an empty or whitespace prompt",
                        exercise_id=ex_id,
                    )
                )

            # 3. Correct Answer presence check
            if ex.correct_answer is None or str(ex.correct_answer).strip() == "":
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="MISSING_CORRECT_ANSWER",
                        message=f"Exercise '{ex_id}' has no correct answer specified",
                        exercise_id=ex_id,
                    )
                )

            # 4. Options integrity & correct_answer matching for choice exercises
            if ex.options:
                cleaned_options = [str(o).strip() for o in ex.options]

                # Empty option value check
                if any(len(o) == 0 for o in cleaned_options):
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="EMPTY_OPTION_VALUE",
                            message=f"Exercise '{ex_id}' contains an empty option string",
                            exercise_id=ex_id,
                        )
                    )

                # Duplicate options check (structural ambiguity)
                if len(cleaned_options) != len(set(cleaned_options)):
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="DUPLICATE_EXERCISE_OPTIONS",
                            message=f"Exercise '{ex_id}' contains duplicate options creating structural ambiguity",
                            exercise_id=ex_id,
                        )
                    )

                # Correct answer matching check
                if ex.correct_answer is not None:
                    ans_str = str(ex.correct_answer).strip()
                    if ans_str not in cleaned_options:
                        issues.append(
                            ValidationIssue(
                                validator=self.validator_name,
                                code="CORRECT_ANSWER_NOT_IN_OPTIONS",
                                message=f"Exercise '{ex_id}' correct_answer '{ans_str}' is not among available options: {cleaned_options}",
                                exercise_id=ex_id,
                            )
                        )

            # 5. Targeted exercise check
            trace = ex.targets
            has_target = (
                bool(trace.learning_object_id) or
                bool(trace.grammar_codes) or
                bool(trace.vocabulary_items) or
                bool(trace.vocabulary_sense_ids)
            )

            if not has_target:
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="UNSPECIFIED_EXERCISE_TARGET",
                        message=f"Exercise '{ex_id}' does not specify any target curriculum claim in TargetTrace",
                        exercise_id=ex_id,
                    )
                )

            # 6. Target Authorization check
            for g_code in trace.grammar_codes:
                if g_code not in assigned_grammar_codes:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="UNAUTHORIZED_EXERCISE_GRAMMAR_TARGET",
                            message=f"Exercise '{ex_id}' tests unassigned Grammar Code '{g_code}'",
                            target_id=g_code,
                            exercise_id=ex_id,
                        )
                    )

            for v_item in trace.vocabulary_items:
                norm_v = v_item.lower().strip()
                if norm_v not in assigned_vocab_items:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="UNAUTHORIZED_EXERCISE_VOCABULARY_TARGET",
                            message=f"Exercise '{ex_id}' tests unassigned Vocabulary item '{v_item}'",
                            target_id=v_item,
                            exercise_id=ex_id,
                        )
                    )

            for s_id in trace.vocabulary_sense_ids:
                if s_id not in assigned_sense_ids:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="UNAUTHORIZED_EXERCISE_SENSE_TARGET",
                            message=f"Exercise '{ex_id}' tests unassigned Vocabulary Sense '{s_id}'",
                            target_id=s_id,
                            exercise_id=ex_id,
                        )
                    )

        passed = len(issues) == 0
        return ValidationResult(passed=passed, issues=issues)
