"""
backend/validators/grammar_content_validator.py — Completeness & Quality Validator for Grammar Content.

ROLE: GRAMMAR CONTENT VALIDATOR
Performs deterministic validation of grammar explanation content structures, completeness,
and internal non-duplication across tips and common mistakes.

CORE RULES:
1. explanation: non-empty, minimum 3 sentences.
2. comparison: non-empty, stored in its own field (not empty).
3. examples_json: minimum 8 items, each with non-empty target, native, and breakdown fields.
4. tips_json: minimum 3 items.
5. common_mistakes_json: minimum 3 items.
6. Near-duplication: no two tips (or common mistakes) share > 80% word overlap.
"""

import re
from typing import Dict, List, Any, Set
from backend.schemas.lesson_schema import ValidationIssue, ValidationResult


class GrammarContentValidator:
    """
    Validates completeness and structural integrity of grammar explanation content.
    """

    def __init__(self, validator_name: str = "grammar_content_validator"):
        self.validator_name = validator_name

    def validate(self, content: Dict[str, Any]) -> ValidationResult:
        issues: List[ValidationIssue] = []

        # 1. Explanation Check (non-empty & min 3 sentences)
        explanation = str(content.get("explanation", "")).strip()
        if not explanation:
            issues.append(
                ValidationIssue(
                    validator=self.validator_name,
                    code="EMPTY_EXPLANATION",
                    message="Grammar explanation field is empty.",
                )
            )
        else:
            sentences = [s for s in re.split(r'[.!?۔\n]+', explanation) if s.strip()]
            if len(sentences) < 3:
                issues.append(
                    ValidationIssue(
                        validator=self.validator_name,
                        code="INSUFFICIENT_EXPLANATION_SENTENCES",
                        message=f"Explanation must contain at least 3 sentences (found {len(sentences)}).",
                    )
                )

        # 2. Comparison Check (non-empty)
        comparison = str(content.get("comparison", "")).strip()
        if not comparison:
            issues.append(
                ValidationIssue(
                    validator=self.validator_name,
                    code="EMPTY_COMPARISON",
                    message="Grammar comparison field is empty or missing from its dedicated column.",
                )
            )

        # 3. Examples Check (min 8 items & complete fields)
        examples = content.get("examples_json") or []
        if not isinstance(examples, list) or len(examples) < 8:
            issues.append(
                ValidationIssue(
                    validator=self.validator_name,
                    code="INSUFFICIENT_EXAMPLES",
                    message=f"examples_json must contain at least 8 items (found {len(examples) if isinstance(examples, list) else 0}).",
                )
            )
        else:
            for idx, ex in enumerate(examples):
                if not isinstance(ex, dict):
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="INVALID_EXAMPLE_FORMAT",
                            message=f"Example at index {idx} is not a valid dictionary object.",
                        )
                    )
                    continue

                target = str(ex.get("target", "")).strip()
                native = str(ex.get("native", "")).strip()
                breakdown = str(ex.get("breakdown", "")).strip()

                if not target or not native or not breakdown:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="INCOMPLETE_EXAMPLE_FIELDS",
                            message=f"Example at index {idx} missing required fields (target, native, or breakdown).",
                        )
                    )

        # 4. Tips Check (min 3 items & distinct)
        tips = content.get("tips_json") or []
        if not isinstance(tips, list) or len(tips) < 3:
            issues.append(
                ValidationIssue(
                    validator=self.validator_name,
                    code="INSUFFICIENT_TIPS",
                    message=f"tips_json must contain at least 3 items (found {len(tips) if isinstance(tips, list) else 0}).",
                )
            )
        else:
            tip_texts: Set[str] = set()
            for idx, item in enumerate(tips):
                if not isinstance(item, dict):
                    continue
                tip_str = str(item.get("tip", "")).strip()
                if not tip_str:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="EMPTY_TIP_TEXT",
                            message=f"Tip at index {idx} is empty.",
                        )
                    )
                    continue

                is_dup, reason = self._check_similarity(tip_str, tip_texts)
                if is_dup:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="DUPLICATE_TIP",
                            message=f"Tip at index {idx} is too similar to another tip ({reason}).",
                        )
                    )
                else:
                    tip_texts.add(tip_str)

        # 5. Common Mistakes Check (min 3 items & distinct)
        mistakes = content.get("common_mistakes_json") or []
        if not isinstance(mistakes, list) or len(mistakes) < 3:
            issues.append(
                ValidationIssue(
                    validator=self.validator_name,
                    code="INSUFFICIENT_COMMON_MISTAKES",
                    message=f"common_mistakes_json must contain at least 3 items (found {len(mistakes) if isinstance(mistakes, list) else 0}).",
                )
            )
        else:
            mistake_texts: Set[str] = set()
            for idx, item in enumerate(mistakes):
                if not isinstance(item, dict):
                    continue
                wrong_str = str(item.get("wrong", "")).strip()
                reason_str = str(item.get("reason", "")).strip()
                combined = f"{wrong_str} {reason_str}".strip()

                if not wrong_str:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="EMPTY_MISTAKE_TEXT",
                            message=f"Common mistake at index {idx} missing 'wrong' field.",
                        )
                    )
                    continue

                is_dup, reason = self._check_similarity(combined, mistake_texts)
                if is_dup:
                    issues.append(
                        ValidationIssue(
                            validator=self.validator_name,
                            code="DUPLICATE_COMMON_MISTAKE",
                            message=f"Common mistake at index {idx} is too similar to another mistake ({reason}).",
                        )
                    )
                else:
                    mistake_texts.add(combined)

        return ValidationResult(passed=len(issues) == 0, issues=issues)

    def _check_similarity(self, text: str, existing_set: Set[str]) -> tuple[bool, str]:
        """Check if text has > 80% word overlap with any text in existing_set."""
        normalized_new = text.lower().strip().replace("  ", " ")
        if not normalized_new:
            return False, "OK"

        new_words = set(normalized_new.split())
        for existing in existing_set:
            normalized_existing = existing.lower().strip().replace("  ", " ")
            if normalized_new == normalized_existing:
                return True, "Exact duplicate"

            existing_words = set(normalized_existing.split())
            if len(new_words) > 2 and len(existing_words) > 2:
                overlap = len(new_words & existing_words)
                similarity = overlap / max(len(new_words), len(existing_words))
                if similarity > 0.80:
                    return True, f"High similarity: {similarity:.0%}"

        return False, "OK"
