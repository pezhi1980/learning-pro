# backend/validators/source_validator.py
"""
ROLE: SOURCE AUTHORITY VALIDATOR

This validator verifies that all curriculum identifiers claimed by generated content
refer to authorized source data in the Curriculum Service.

CORE RULES:
1. Never trust Agent-declared source validity.
2. Independently validate all curriculum identifiers against Curriculum Service.
3. Validate Grammar Codes, Vocabulary Items, Vocabulary Senses, and Coverage items.
4. Fail if unknown or unauthorized curriculum identifiers are referenced.
5. Never auto-correct or substitute unknown identifiers.
"""

from typing import Optional
from backend.curriculum import CurriculumService
from backend.schemas.agent_output import AgentOutput
from backend.schemas.lesson_schema import ValidationIssue, ValidationResult


class SourceValidator:
    """
    Validates that all curriculum targets claimed in AgentOutput exist in authoritative source data.
    """

    def __init__(self, curriculum_service: Optional[CurriculumService] = None, validator_name: str = "source_validator"):
        self.curriculum_service = curriculum_service or CurriculumService()
        self.validator_name = validator_name

    def validate(self, output: AgentOutput) -> ValidationResult:
        issues = []

        # Collect all blocks with TargetTrace
        traced_blocks = []
        for exp in output.explanations:
            traced_blocks.append(("explanation", exp.id, exp.targets))
        for ex in output.examples:
            traced_blocks.append(("example", ex.id, ex.targets))
        for ex_item in output.exercises:
            traced_blocks.append(("exercise", ex_item.id, ex_item.targets))

        for block_type, block_id, trace in traced_blocks:
            # 1. Validate claimed Grammar Codes
            for g_code in trace.grammar_codes:
                if not self.curriculum_service.grammar_exists(g_code):
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="UNKNOWN_GRAMMAR_CODE",
                            message=f"{block_type.title()} '{block_id}' claims unknown Grammar Code '{g_code}'",
                            target_id=g_code,
                            exercise_id=block_id if block_type == "exercise" else None,
                        )
                    )

            # 2. Validate claimed Vocabulary Items
            for v_item in trace.vocabulary_items:
                matches = self.curriculum_service.find_vocabulary_by_lexeme(v_item)
                if not matches:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="UNKNOWN_VOCABULARY_ITEM",
                            message=f"{block_type.title()} '{block_id}' claims unknown Vocabulary item '{v_item}'",
                            target_id=v_item,
                            exercise_id=block_id if block_type == "exercise" else None,
                        )
                    )

            # 3. Validate claimed Vocabulary Sense IDs
            for s_id in trace.vocabulary_sense_ids:
                clean_s_id = s_id.replace(":sense", "")
                sense_item = self.curriculum_service.get_vocabulary_by_id(clean_s_id)
                if not sense_item:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="UNKNOWN_VOCABULARY_SENSE",
                            message=f"{block_type.title()} '{block_id}' claims unknown Vocabulary Sense ID '{s_id}'",
                            target_id=s_id,
                            exercise_id=block_id if block_type == "exercise" else None,
                        )
                    )

        # 4. Validate CoverageItem learning_object_ids
        for cov in output.coverage:
            lo_id = cov.learning_object_id
            clean_id = lo_id.replace(":sense", "")
            exists_as_grammar = self.curriculum_service.grammar_exists(lo_id) or (self.curriculum_service.get_grammar_by_id(lo_id) is not None)
            exists_as_vocab = (self.curriculum_service.get_vocabulary_by_id(clean_id) is not None) or len(self.curriculum_service.find_vocabulary_by_lexeme(lo_id)) > 0

            if not (exists_as_grammar or exists_as_vocab):
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="UNKNOWN_COVERAGE_TARGET",
                        message=f"Coverage item claims unknown learning object ID '{lo_id}'",
                        target_id=lo_id,
                    )
                )

        passed = len(issues) == 0
        return ValidationResult(passed=passed, issues=issues)
