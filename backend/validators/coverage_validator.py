# backend/validators/coverage_validator.py
"""
ROLE: ASSIGNED TARGET COVERAGE VALIDATOR

This validator ensures that every target assigned by the Backend has been meaningfully covered
in generated content according to generation mode requirements.

CORE RULES:
1. Required assigned target coverage is 100%.
2. Compare ASSIGNED TARGETS in AgentInput vs MEANINGFULLY COVERED TARGETS in AgentOutput.
3. Every assigned target must have structural evidence (TargetTrace) in explanations, examples, or exercises.
4. False coverage claims without corresponding content fail.
5. Missing any mandatory assigned target causes validation failure.
"""

from typing import Dict, Set
from backend.schemas.agent_input import AgentInput, GenerationMode
from backend.schemas.agent_output import AgentOutput
from backend.schemas.lesson_schema import ValidationIssue, ValidationResult


class CoverageValidator:
    """
    Validates 100% target coverage between AgentInput and AgentOutput.
    """

    def __init__(self, validator_name: str = "coverage_validator"):
        self.validator_name = validator_name

    def validate(self, input_data: AgentInput, output: AgentOutput) -> ValidationResult:
        issues = []

        # 1. Collect all target traces from AgentOutput
        traced_grammar_codes: Set[str] = set()
        traced_vocab_items: Set[str] = set()
        traced_vocab_senses: Set[str] = set()
        traced_learning_objects: Set[str] = set()

        all_blocks = []
        for exp in output.explanations:
            all_blocks.append(exp.targets)
        for ex in output.examples:
            all_blocks.append(ex.targets)
        for ex_item in output.exercises:
            all_blocks.append(ex_item.targets)

        for trace in all_blocks:
            if trace.learning_object_id:
                traced_learning_objects.add(trace.learning_object_id)
            for g in trace.grammar_codes:
                traced_grammar_codes.add(g)
            for v in trace.vocabulary_items:
                traced_vocab_items.add(v.lower().strip())
            for s in trace.vocabulary_sense_ids:
                traced_vocab_senses.add(s)

        # Build coverage item map
        coverage_map: Dict[str, bool] = {
            c.learning_object_id: (c.explained or c.example_covered or c.exercise_covered)
            for c in output.coverage
        }

        # 2. Check Grammar Target Coverage
        for g_target in input_data.target_grammar:
            lo_id = g_target.learning_object_id
            g_code = g_target.grammar_code

            has_trace = (lo_id in traced_learning_objects) or (g_code in traced_grammar_codes)
            has_cov_claim = coverage_map.get(lo_id, False)

            if not has_trace:
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="MISSING_GRAMMAR_COVERAGE",
                        message=f"Assigned Grammar target '{g_code}' ({lo_id}) is not covered in content traces",
                        target_id=lo_id,
                    )
                )

            if not has_cov_claim:
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="MISSING_COVERAGE_DECLARATION",
                        message=f"Assigned Grammar target '{g_code}' ({lo_id}) lacks coverage declaration in AgentOutput.coverage",
                        target_id=lo_id,
                    )
                )

        # 3. Check Vocabulary Target Coverage
        for v_target in input_data.target_vocabulary:
            lo_id = v_target.learning_object_id
            v_item = v_target.item.lower().strip()

            has_trace = (lo_id in traced_learning_objects) or (v_item in traced_vocab_items)
            has_cov_claim = coverage_map.get(lo_id, False)

            if not has_trace:
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="MISSING_VOCABULARY_COVERAGE",
                        message=f"Assigned Vocabulary target '{v_target.item}' ({lo_id}) is not covered in content traces",
                        target_id=lo_id,
                    )
                )

            if not has_cov_claim:
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="MISSING_COVERAGE_DECLARATION",
                        message=f"Assigned Vocabulary target '{v_target.item}' ({lo_id}) lacks coverage declaration in AgentOutput.coverage",
                        target_id=lo_id,
                    )
                )

            # Check explicit sense coverage if assigned
            for s_target in v_target.senses:
                s_id = s_target.sense_id
                s_traced = (s_id in traced_vocab_senses) or (s_id in traced_learning_objects)
                if not s_traced:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="MISSING_VOCABULARY_SENSE_COVERAGE",
                            message=f"Assigned Vocabulary Sense '{s_id}' for '{v_target.item}' is not covered in content traces",
                            target_id=s_id,
                        )
                    )

        # 4. Cross-check CoverageItem claims against actual content (detect false claims)
        for cov in output.coverage:
            lo_id = cov.learning_object_id
            if cov.explained or cov.example_covered or cov.exercise_covered:
                clean_id = lo_id.replace(":sense", "")
                is_actually_traced = (
                    lo_id in traced_learning_objects or
                    clean_id in traced_learning_objects or
                    lo_id in traced_grammar_codes or
                    lo_id.lower().strip() in traced_vocab_items or
                    lo_id in traced_vocab_senses
                )
                if not is_actually_traced:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="FALSE_COVERAGE_CLAIM",
                            message=f"CoverageItem claims target '{lo_id}' is covered, but no traced content block exists",
                            target_id=lo_id,
                        )
                    )

        passed = len(issues) == 0
        return ValidationResult(passed=passed, issues=issues)
