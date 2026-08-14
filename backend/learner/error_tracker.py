# backend/learner/error_tracker.py
"""
ROLE: ERROR TRACKER

Tracks recurring error patterns for learners based on EvaluationResult error codes.
Increments occurrence counts, updates last_seen timestamps, and adjusts severity deterministically.
Error tracking never authorizes unassigned curriculum.
"""

from __future__ import annotations
from datetime import datetime, timezone

from typing import TYPE_CHECKING, List, Optional
from backend.learner.knowledge_models import LearnerErrorPattern
from backend.learner.learner_repository import LearnerRepository

if TYPE_CHECKING:
    from backend.evaluation.evaluation_models import EvaluationResult


class ErrorTracker:
    """
    Tracks and maintains learner error patterns.
    """

    def __init__(self, repository: Optional[LearnerRepository] = None):
        self.repository = repository or LearnerRepository()

    def process_evaluation_errors(self, eval_result: "EvaluationResult") -> List[LearnerErrorPattern]:

        if eval_result.correct or not eval_result.error_codes:
            return []

        now = eval_result.evaluated_at or datetime.now(timezone.utc)
        updated_patterns = []

        for err_code in eval_result.error_codes:
            category = self._determine_category(err_code)
            target_lo_id = eval_result.target_learning_object_ids[0] if eval_result.target_learning_object_ids else "unknown"

            # Find existing matching error pattern
            existing = None
            for p in self.repository.get_error_patterns(eval_result.learner_id, active_only=False):
                if p.error_code == err_code and p.target_learning_object_id == target_lo_id:
                    existing = p
                    break

            if existing:
                existing.occurrence_count += 1
                existing.last_seen_at = now
                existing.active = True
                existing.severity_score = min(1.0, round(existing.severity_score + 0.1, 2))
                existing.last_context = f"Learner answered '{eval_result.learner_answer}' instead of '{eval_result.expected_answer}'"
                pattern = self.repository.save_error_pattern(existing)
            else:
                pattern = LearnerErrorPattern(
                    error_id=f"err:{eval_result.learner_id}:{err_code}:{len(self.repository.get_error_patterns(eval_result.learner_id))+1}",
                    learner_id=eval_result.learner_id,
                    error_code=err_code,
                    category=category,
                    target_learning_object_id=target_lo_id,
                    grammar_code=eval_result.tested_grammar_codes[0] if eval_result.tested_grammar_codes else None,
                    vocabulary_source_item_id=eval_result.tested_vocabulary_items[0] if eval_result.tested_vocabulary_items else None,
                    vocabulary_sense_id=eval_result.tested_vocabulary_sense_ids[0] if eval_result.tested_vocabulary_sense_ids else None,
                    occurrence_count=1,
                    first_seen_at=now,
                    last_seen_at=now,
                    last_context=f"Learner answered '{eval_result.learner_answer}' instead of '{eval_result.expected_answer}'",
                    active=True,
                    severity_score=0.5,
                )
                pattern = self.repository.save_error_pattern(pattern)

            updated_patterns.append(pattern)

        return updated_patterns

    def _determine_category(self, error_code: str) -> str:
        code_lower = error_code.lower()
        if "grammar" in code_lower:
            return "grammar"
        elif "sense" in code_lower:
            return "sense_confusion"
        elif "vocab" in code_lower:
            return "vocabulary"
        elif "spelling" in code_lower:
            return "spelling"
        return "general"
