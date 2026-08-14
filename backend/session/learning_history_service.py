# backend/session/learning_history_service.py
"""
ROLE: LEARNING HISTORY SERVICE

Stores and retrieves learner-facing educational history:
- Completed sessions
- Lesson activity records
- Exercise responses
- Reviews & repairs history
- Completion events (micro lessons, topics, units, levels, sessions)
- Aggregate learner stats
Does not duplicate raw infrastructure logs.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.session.session_models import CompletionEvent, LearnerHistoryRecord, LearnerStats


class LearningHistoryService:
    """
    Manages educational history and aggregate stats for learners.
    """

    def __init__(self):
        self._history: Dict[str, List[LearnerHistoryRecord]] = {}
        self._completion_events: Dict[str, List[CompletionEvent]] = {}
        self._stats: Dict[str, LearnerStats] = {}

    def record_history_entry(
        self,
        learner_id: str,
        record_type: str,
        summary: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> LearnerHistoryRecord:
        """
        Records an educational history entry for a learner.
        """
        now = datetime.now(timezone.utc)
        record_id = f"hist:{learner_id}:{int(now.timestamp())}:{len(self._history.get(learner_id, []))}"
        record = LearnerHistoryRecord(
            record_id=record_id,
            learner_id=learner_id,
            record_type=record_type,
            summary=summary,
            timestamp=now,
            details=details or {},
        )

        if learner_id not in self._history:
            self._history[learner_id] = []
        self._history[learner_id].append(record)

        self._update_stats_on_record(learner_id, record_type, details or {})
        return record

    def record_completion_event(self, event: CompletionEvent) -> CompletionEvent:
        """
        Records a CompletionEvent (Micro Lesson, Topic, Unit, Level, Session).
        """
        if event.learner_id not in self._completion_events:
            self._completion_events[event.learner_id] = []
        self._completion_events[event.learner_id].append(event)

        self.record_history_entry(
            learner_id=event.learner_id,
            record_type="completion",
            summary=f"Completed {event.completion_type.value}: {event.target_id}",
            details={"completion_type": event.completion_type.value, "target_id": event.target_id},
        )
        return event

    def get_learner_history(
        self,
        learner_id: str,
        limit: int = 50,
        offset: int = 0,
        record_type: Optional[str] = None,
    ) -> List[LearnerHistoryRecord]:
        """
        Retrieves paginated history for a learner, optionally filtered by record_type.
        """
        user_records = self._history.get(learner_id, [])
        if record_type:
            user_records = [r for r in user_records if r.record_type == record_type]

        # Sort descending by timestamp
        sorted_records = sorted(user_records, key=lambda r: r.timestamp, reverse=True)
        return sorted_records[offset : offset + limit]

    def get_completion_events(self, learner_id: str) -> List[CompletionEvent]:
        return self._completion_events.get(learner_id, [])

    def get_learner_stats(self, learner_id: str) -> LearnerStats:
        if learner_id not in self._stats:
            self._stats[learner_id] = LearnerStats(learner_id=learner_id)
        return self._stats[learner_id]

    def _update_stats_on_record(self, learner_id: str, record_type: str, details: Dict[str, Any]) -> None:
        stats = self.get_learner_stats(learner_id)
        stats.last_active_at = datetime.now(timezone.utc)

        if record_type == "session":
            stats.total_sessions_completed += 1
            stats.total_time_spent_minutes += details.get("duration_minutes", 15)
        elif record_type == "completion" and details.get("completion_type") == "micro_lesson":
            stats.total_micro_lessons_completed += 1
        elif record_type == "exercise":
            stats.total_activities_completed += 1
