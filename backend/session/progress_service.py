# backend/session/progress_service.py
"""
ROLE: PROGRESS SERVICE

Orchestrates progress tracking and completion events across:
- Micro Lesson completion
- Topic completion
- Unit completion
- Level completion
- Session completion
Integrates with CourseService and LearningHistoryService.
PRESERVES: completed != mastered.
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from backend.course import CourseService, LearnerCourseProgress
from backend.session.daily_session_service import DailySessionService
from backend.session.learning_history_service import LearningHistoryService
from backend.session.session_models import CompletionEvent, CompletionType, DailyLearningSession, SessionStatus


class ProgressService:
    """
    Central completion and progression tracking service.
    """

    def __init__(
        self,
        course_service: Optional[CourseService] = None,
        daily_session_service: Optional[DailySessionService] = None,
        history_service: Optional[LearningHistoryService] = None,
    ):
        self.course_service = course_service or CourseService()
        self.daily_session_service = daily_session_service or DailySessionService()
        self.history_service = history_service or LearningHistoryService()

    def complete_micro_lesson(
        self, learner_id: str, micro_lesson_id: str
    ) -> LearnerCourseProgress:
        """
        Records Micro Lesson completion in CourseService, checks for Topic/Unit/Level completion,
        and logs CompletionEvents in LearningHistoryService.
        """
        # Record completion in CourseService
        course_progress = self.course_service.record_micro_lesson_completion(learner_id, micro_lesson_id)

        # Log Micro Lesson completion event
        event = CompletionEvent(
            event_id=f"evt:ml:{learner_id}:{micro_lesson_id}",
            learner_id=learner_id,
            completion_type=CompletionType.micro_lesson,
            target_id=micro_lesson_id,
        )
        self.history_service.record_completion_event(event)

        # Check for Topic completion
        ml_node = self.course_service.get_micro_lesson(micro_lesson_id)
        if ml_node:
            self._check_and_record_topic_completion(learner_id, ml_node.topic_id, course_progress)

        return course_progress

    def complete_session(self, session_id: str) -> DailyLearningSession:
        """
        Records Daily Learning Session completion and logs CompletionEvent.
        """
        session = self.daily_session_service.complete_session(session_id)

        event = CompletionEvent(
            event_id=f"evt:sess:{session.learner_id}:{session.session_id}",
            learner_id=session.learner_id,
            completion_type=CompletionType.session,
            target_id=session.session_id,
            metadata={
                "duration_minutes": session.total_estimated_duration_minutes,
                "activities_completed": len(session.completed_activity_ids),
            },
        )
        self.history_service.record_completion_event(event)
        return session

    def _check_and_record_topic_completion(
        self, learner_id: str, topic_id: str, course_progress: LearnerCourseProgress
    ) -> None:
        parts = topic_id.split(":")
        if len(parts) >= 3:
            level_code = parts[1]
            unit_id = f"unit:{parts[1]}:{parts[2]}"
            level_obj = self.course_service.get_level(level_code)

            if level_obj:
                for unit in level_obj.units:
                    if unit.unit_id == unit_id:
                        for topic in unit.topics:
                            if topic.topic_id == topic_id:
                                # If all micro lessons in topic are complete
                                if all(
                                    ml.micro_lesson_id in course_progress.completed_micro_lesson_ids
                                    for ml in topic.micro_lessons
                                ):
                                    # Log Topic Completion Event
                                    t_event = CompletionEvent(
                                        event_id=f"evt:topic:{learner_id}:{topic_id}",
                                        learner_id=learner_id,
                                        completion_type=CompletionType.topic,
                                        target_id=topic_id,
                                    )
                                    self.history_service.record_completion_event(t_event)
                                    self._check_and_record_unit_completion(learner_id, unit, course_progress)

    def _check_and_record_unit_completion(
        self, learner_id: str, unit: Any, course_progress: LearnerCourseProgress
    ) -> None:
        # Check if all topics in unit are complete
        all_ml_ids = [ml.micro_lesson_id for t in unit.topics for ml in t.micro_lessons]
        if all(ml_id in course_progress.completed_micro_lesson_ids for ml_id in all_ml_ids):
            u_event = CompletionEvent(
                event_id=f"evt:unit:{learner_id}:{unit.unit_id}",
                learner_id=learner_id,
                completion_type=CompletionType.unit,
                target_id=unit.unit_id,
            )
            self.history_service.record_completion_event(u_event)
            self._check_and_record_level_completion(learner_id, unit.level_code, course_progress)

    def _check_and_record_level_completion(
        self, learner_id: str, level_code: str, course_progress: LearnerCourseProgress
    ) -> None:
        level_nodes = self.course_service.repository.get_all_micro_lessons_in_level(level_code)
        if all(node.micro_lesson_id in course_progress.completed_micro_lesson_ids for node in level_nodes):
            l_event = CompletionEvent(
                event_id=f"evt:level:{learner_id}:{level_code}",
                learner_id=learner_id,
                completion_type=CompletionType.level,
                target_id=level_code,
            )
            self.history_service.record_completion_event(l_event)
