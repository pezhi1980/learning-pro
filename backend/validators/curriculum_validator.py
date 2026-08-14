# backend/validators/curriculum_validator.py
"""
ROLE: CURRICULUM BOUNDARY VALIDATOR

This validator ensures that generated content does not introduce unauthorized curriculum targets.

CORE RULES:
1. Supporting language is permitted in natural sentences.
2. Supporting language must not become an unauthorized teaching or testing target.
3. Validate that every intentionally taught or tested target belongs to the Backend-assigned target set.
4. Reject invented or unassigned Grammar targets, Vocabulary targets, or Vocabulary Senses.
5. Allowed supporting content must not be promoted into target content.
"""

from typing import Set
from backend.schemas.agent_input import AgentInput
from backend.schemas.agent_output import AgentOutput
from backend.schemas.lesson_schema import ValidationIssue, ValidationResult


class CurriculumValidator:
    """
    Validates curriculum boundaries: rejects unauthorized or invented targets claimed in TargetTrace.
    """

    def __init__(self, validator_name: str = "curriculum_validator"):
        self.validator_name = validator_name

    def validate(self, input_data: AgentInput, output: AgentOutput) -> ValidationResult:
        issues = []

        # Authorized target sets
        assigned_grammar_codes: Set[str] = {g.grammar_code for g in input_data.target_grammar}
        assigned_grammar_ids: Set[str] = {g.learning_object_id for g in input_data.target_grammar}
        allowed_grammar_codes: Set[str] = set(input_data.allowed_grammar_codes)

        assigned_vocab_items: Set[str] = {v.item.lower().strip() for v in input_data.target_vocabulary}
        assigned_vocab_ids: Set[str] = {v.learning_object_id for v in input_data.target_vocabulary}
        allowed_vocab_items: Set[str] = {v.lower().strip() for v in input_data.allowed_vocabulary_items}

        assigned_sense_ids: Set[str] = set()
        for v in input_data.target_vocabulary:
            for s in v.senses:
                assigned_sense_ids.add(s.sense_id)

        allowed_sense_ids: Set[str] = set(input_data.allowed_vocabulary_sense_ids)

        # Collect all claimed traces in explanations, examples, and exercises
        traced_blocks = []
        for exp in output.explanations:
            traced_blocks.append(("explanation", exp.id, exp.targets))
        for ex in output.examples:
            traced_blocks.append(("example", ex.id, ex.targets))
        for ex_item in output.exercises:
            traced_blocks.append(("exercise", ex_item.id, ex_item.targets))

        for block_type, block_id, trace in traced_blocks:
            # 1. Check Grammar Code claims
            for g_code in trace.grammar_codes:
                if g_code not in assigned_grammar_codes:
                    if g_code in allowed_grammar_codes:
                        issues.append(
                            ValidationIssue(
                                validator=self.validator_name,
                                code="ALLOWED_GRAMMAR_PROMOTED_TO_TARGET",
                                message=f"{block_type.title()} '{block_id}' claims allowed supporting Grammar '{g_code}' as a teaching target",
                                target_id=g_code,
                                exercise_id=block_id if block_type == "exercise" else None,
                            )
                        )
                    else:
                        issues.append(
                            ValidationIssue(
                                validator=self.validator_name,
                                code="UNAUTHORIZED_GRAMMAR_TARGET",
                                message=f"{block_type.title()} '{block_id}' claims unassigned Grammar target '{g_code}'",
                                target_id=g_code,
                                exercise_id=block_id if block_type == "exercise" else None,
                            )
                        )

            # 2. Check Vocabulary Item claims
            for v_item in trace.vocabulary_items:
                norm_v = v_item.lower().strip()
                if norm_v not in assigned_vocab_items:
                    if norm_v in allowed_vocab_items:
                        issues.append(
                            ValidationIssue(
                                validator=self.validator_name,
                                code="ALLOWED_VOCABULARY_PROMOTED_TO_TARGET",
                                message=f"{block_type.title()} '{block_id}' claims allowed supporting Vocabulary '{v_item}' as a target",
                                target_id=v_item,
                                exercise_id=block_id if block_type == "exercise" else None,
                            )
                        )
                    else:
                        issues.append(
                            ValidationIssue(
                                validator=self.validator_name,
                                code="UNAUTHORIZED_VOCABULARY_TARGET",
                                message=f"{block_type.title()} '{block_id}' claims unassigned Vocabulary target '{v_item}'",
                                target_id=v_item,
                                exercise_id=block_id if block_type == "exercise" else None,
                            )
                        )

            # 3. Check Vocabulary Sense claims
            for s_id in trace.vocabulary_sense_ids:
                if s_id not in assigned_sense_ids:
                    if s_id in allowed_sense_ids:
                        issues.append(
                            ValidationIssue(
                                validator=self.validator_name,
                                code="ALLOWED_SENSE_PROMOTED_TO_TARGET",
                                message=f"{block_type.title()} '{block_id}' claims allowed Vocabulary Sense '{s_id}' as a target",
                                target_id=s_id,
                                exercise_id=block_id if block_type == "exercise" else None,
                            )
                        )
                    else:
                        issues.append(
                            ValidationIssue(
                                validator=self.validator_name,
                                code="UNAUTHORIZED_VOCABULARY_SENSE_TARGET",
                                message=f"{block_type.title()} '{block_id}' claims unassigned Vocabulary Sense '{s_id}'",
                                target_id=s_id,
                                exercise_id=block_id if block_type == "exercise" else None,
                            )
                        )

            # 4. Check Learning Object ID claim if present
            if trace.learning_object_id:
                lo_id = trace.learning_object_id
                clean_lo = lo_id.replace(":sense", "")
                is_authorized_lo = (
                    lo_id in assigned_grammar_ids or
                    lo_id in assigned_vocab_ids or
                    clean_lo in assigned_vocab_ids or
                    lo_id in assigned_sense_ids or
                    lo_id in assigned_grammar_codes
                )
                if not is_authorized_lo:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="UNAUTHORIZED_LEARNING_OBJECT_ID",
                            message=f"{block_type.title()} '{block_id}' claims unassigned learning object ID '{lo_id}'",
                            target_id=lo_id,
                            exercise_id=block_id if block_type == "exercise" else None,
                        )
                    )

        passed = len(issues) == 0
        return ValidationResult(passed=passed, issues=issues)
