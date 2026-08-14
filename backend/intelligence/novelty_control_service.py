# backend/intelligence/novelty_control_service.py
"""
ROLE: NOVELTY CONTROL SERVICE

Prevents cognitive overload by controlling simultaneous unknown Grammar/Vocabulary/Task complexity.
Enforces cognitive load caps:
- Max 1 primary new Grammar target per activity block
- Max 2 new Vocabulary targets per activity block
- Max task complexity index <= 1.5
"""

import logging
from typing import Any, Dict, List, Set, Tuple

logger = logging.getLogger(__name__)


class NoveltyControlService:
    """
    Evaluates and enforces cognitive load caps on proposed learning sessions.
    """

    MAX_NEW_GRAMMAR_TARGETS: int = 1
    MAX_NEW_VOCAB_TARGETS: int = 2
    MAX_TASK_COMPLEXITY: float = 1.5

    def validate_session_novelty(
        self,
        proposed_grammar_target_ids: List[str],
        proposed_vocab_target_ids: List[str],
        task_complexity_index: float,
        known_target_ids: Set[str],
    ) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        Validates whether a proposed activity block respects cognitive load caps.
        """
        new_grammar = [g for g in proposed_grammar_target_ids if g not in known_target_ids]
        new_vocab = [v for v in proposed_vocab_target_ids if v not in known_target_ids]

        violations: List[str] = []

        if len(new_grammar) > self.MAX_NEW_GRAMMAR_TARGETS:
            violations.append(
                f"Cognitive Overload: {len(new_grammar)} new Grammar targets proposed (Max allowed: {self.MAX_NEW_GRAMMAR_TARGETS})."
            )

        if len(new_vocab) > self.MAX_NEW_VOCAB_TARGETS:
            violations.append(
                f"Cognitive Overload: {len(new_vocab)} new Vocabulary targets proposed (Max allowed: {self.MAX_NEW_VOCAB_TARGETS})."
            )

        if task_complexity_index > self.MAX_TASK_COMPLEXITY:
            violations.append(
                f"Cognitive Overload: Task complexity index {task_complexity_index} exceeds max cap ({self.MAX_TASK_COMPLEXITY})."
            )

        is_valid = len(violations) == 0

        stats = {
            "new_grammar_count": len(new_grammar),
            "new_vocab_count": len(new_vocab),
            "task_complexity_index": task_complexity_index,
            "is_valid": is_valid,
        }

        return is_valid, violations, stats
