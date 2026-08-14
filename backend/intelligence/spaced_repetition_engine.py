# backend/intelligence/spaced_repetition_engine.py
"""
ROLE: SPACED REPETITION ENGINE

Implements an evidence-based deterministic spaced repetition algorithm.
Schedules review items using:
- success history & consecutive correct
- failure history & consecutive incorrect
- stability (S in days)
- elapsed time since last practice
- lapses (times fallen from mastered state)
- retrieval success probability R = exp(-elapsed / S)
- active error patterns

Algorithm is strictly deterministic, documented, and replaceable.
Does NOT claim unproven scientific optimality.
"""

import math
import logging
from datetime import datetime, timedelta, timezone
from typing import Tuple

logger = logging.getLogger(__name__)


class SpacedRepetitionEngine:
    """
    Evidence-based deterministic spaced repetition scheduler.
    """

    MIN_STABILITY_DAYS: float = 0.5
    MAX_STABILITY_DAYS: float = 365.0

    def compute_next_schedule(
        self,
        current_stability: float,
        is_correct: bool,
        overall_mastery: float,
        consecutive_correct: int,
        consecutive_incorrect: int,
        lapses: int,
        last_practiced_at: datetime,
    ) -> Tuple[float, int, float, datetime]:
        """
        Calculates new stability, updated lapse count, estimated retrieval probability R, and next review_due_at timestamp.
        """
        now = datetime.now(timezone.utc)

        if last_practiced_at.tzinfo is None:
            last_practiced_at = last_practiced_at.replace(tzinfo=timezone.utc)

        elapsed_seconds = max(0.0, (now - last_practiced_at).total_seconds())
        elapsed_days = elapsed_seconds / 86400.0

        current_s = max(self.MIN_STABILITY_DAYS, current_stability)

        # Retrieval success probability: R = exp(-elapsed_days / S)
        retrieval_probability = round(math.exp(-elapsed_days / current_s), 4)

        if is_correct:
            # Expand interval upon successful retrieval
            mastery_factor = max(0.2, overall_mastery)
            streak_bonus = min(2.0, 1.0 + 0.15 * consecutive_correct)
            new_stability = current_s * (1.0 + 1.20 * mastery_factor * streak_bonus)
            new_lapses = lapses
        else:
            # Lapse occurs: stability drops sharply to reset learning interval
            new_stability = max(self.MIN_STABILITY_DAYS, current_s * 0.40)
            new_lapses = lapses + 1 if overall_mastery >= 0.70 else lapses

        new_stability = round(min(self.MAX_STABILITY_DAYS, new_stability), 2)
        review_due_at = now + timedelta(days=new_stability)

        return new_stability, new_lapses, retrieval_probability, review_due_at
