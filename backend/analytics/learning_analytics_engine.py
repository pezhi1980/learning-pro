# backend/analytics/learning_analytics_engine.py
"""
ROLE: LEARNING ANALYTICS ENGINE

Computes aggregate learning performance metrics:
- accuracy (% correct exercise responses)
- completion (% started lessons completed)
- retention (review recall success rate)
- review success rate
- drop-off rate (% abandoned sessions)
- difficult targets identification

CORE RULE: Analytics does NOT become learner mastery truth or Curriculum authority.
"""

import logging
from typing import Any, Dict, List, Optional
from backend.analytics.analytics_event_service import AnalyticsEventService
from backend.analytics.analytics_models import AnalyticsEventType

logger = logging.getLogger(__name__)


class LearningAnalyticsEngine:
    """
    Engine computing aggregate learning performance metrics from event telemetry.
    """

    def __init__(self, event_service: Optional[AnalyticsEventService] = None):
        self.event_service = event_service or AnalyticsEventService()

    def compute_learner_metrics(self, learner_id: str) -> Dict[str, Any]:
        """
        Computes aggregate metrics for learner_id.
        """
        events = self.event_service.get_events(learner_id=learner_id, limit=1000)

        exercise_events = [e for e in events if e.event_type == AnalyticsEventType.exercise_answered]
        started_events = [e for e in events if e.event_type == AnalyticsEventType.lesson_started]
        completed_events = [e for e in events if e.event_type == AnalyticsEventType.lesson_completed]
        abandoned_events = [e for e in events if e.event_type == AnalyticsEventType.session_abandoned]
        review_events = [e for e in events if e.event_type == AnalyticsEventType.review_completed]

        total_answers = len(exercise_events)
        correct_answers = sum(1 for e in exercise_events if e.payload.get("is_correct", False))
        accuracy = round((correct_answers / total_answers * 100.0), 2) if total_answers > 0 else 0.0

        total_started = len(started_events)
        total_completed = len(completed_events)
        completion_rate = round((total_completed / total_started * 100.0), 2) if total_started > 0 else 0.0

        total_abandoned = len(abandoned_events)
        drop_off_rate = round((total_abandoned / total_started * 100.0), 2) if total_started > 0 else 0.0

        total_reviews = len(review_events)
        successful_reviews = sum(1 for e in review_events if e.payload.get("success", False))
        review_success_rate = round((successful_reviews / total_reviews * 100.0), 2) if total_reviews > 0 else 0.0

        # Difficult targets calculation
        target_counts: Dict[str, Dict[str, int]] = {}
        for e in exercise_events:
            t_id = e.target_id or "unknown"
            if t_id not in target_counts:
                target_counts[t_id] = {"total": 0, "correct": 0}
            target_counts[t_id]["total"] += 1
            if e.payload.get("is_correct", False):
                target_counts[t_id]["correct"] += 1

        difficult_targets = []
        for t_id, stats in target_counts.items():
            acc = (stats["correct"] / stats["total"]) if stats["total"] > 0 else 1.0
            if acc < 0.50 and stats["total"] >= 2:
                difficult_targets.append({"target_id": t_id, "accuracy": round(acc * 100.0, 1)})

        return {
            "learner_id": learner_id,
            "total_exercises_answered": total_answers,
            "accuracy_percentage": accuracy,
            "completion_rate_percentage": completion_rate,
            "drop_off_rate_percentage": drop_off_rate,
            "review_success_rate_percentage": review_success_rate,
            "difficult_targets": difficult_targets,
        }
