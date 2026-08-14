# backend/course/course_service.py
"""
ROLE: COURSE SERVICE

Central orchestration service for Course Navigation, Course Progression, Level Progress Calculations,
and Resume Position tracking.
Composes data from CourseRepository, PrerequisiteService, and LearnerService.
Course Architecture NEVER calls ContentAgent directly.
"""

from typing import Any, Dict, List, Optional
from backend.course.course_models import (
    CourseLevel,
    CourseTopic,
    CourseUnit,
    LearnerCourseProgress,
    LevelProgressSummary,
    MicroLessonNode,
)
from backend.course.course_repository import CourseRepository
from backend.course.prerequisite_service import PrerequisiteService
from backend.learner import LearnerService


class CourseService:
    """
    Service layer orchestrating course hierarchy navigation, progress calculation, and prerequisite enforcement.
    """

    def __init__(
        self,
        repository: Optional[CourseRepository] = None,
        prerequisite_service: Optional[PrerequisiteService] = None,
        learner_service: Optional[LearnerService] = None,
    ):
        self.repository = repository or CourseRepository()
        self.prereq_service = prerequisite_service or PrerequisiteService(repository=self.repository)
        self.learner_service = learner_service or LearnerService()

    # ── Hierarchy Access ───────────────────────────────────────────────────

    def get_level(self, level_code: str) -> Optional[CourseLevel]:
        return self.repository.get_level(level_code)

    def list_supported_levels(self) -> List[str]:
        return self.repository.list_supported_levels()

    def get_micro_lesson(self, micro_lesson_id: str) -> Optional[MicroLessonNode]:
        return self.repository.get_micro_lesson(micro_lesson_id)

    # ── Course Progression & Resume Position ───────────────────────────────

    def get_learner_progress(self, learner_id: str) -> LearnerCourseProgress:
        progress = self.repository.get_learner_progress(learner_id)
        # Update unlocked status dynamically
        self._update_unlocked_lessons(progress)
        return progress

    def record_micro_lesson_completion(
        self, learner_id: str, micro_lesson_id: str
    ) -> LearnerCourseProgress:
        """
        Records completion of a micro lesson for a learner.
        Unlocks downstream micro lessons and advances resume position.
        PRESERVES: completed != mastered.
        """
        progress = self.repository.get_learner_progress(learner_id)
        if micro_lesson_id not in progress.completed_micro_lesson_ids:
            progress.completed_micro_lesson_ids.append(micro_lesson_id)

        self._update_unlocked_lessons(progress)
        self._advance_resume_position(progress, micro_lesson_id)
        self.repository.save_learner_progress(progress)
        return progress

    def get_next_course_target(
        self, learner_id: str, level_code: str = "A1"
    ) -> Optional[MicroLessonNode]:
        """
        Locates the next unlocked, uncompleted MicroLessonNode in course sequence for the given level.
        Used by LearningDecisionService to align session selection with course progression.
        """
        progress = self.get_learner_progress(learner_id)
        level_nodes = self.repository.get_all_micro_lessons_in_level(level_code)

        for node in level_nodes:
            if node.micro_lesson_id not in progress.completed_micro_lesson_ids:
                if self.prereq_service.is_micro_lesson_unlocked(
                    node.micro_lesson_id, progress.completed_micro_lesson_ids
                ):
                    return node

        # Fallback to any unlocked node across all levels
        for lvl in self.list_supported_levels():
            for node in self.repository.get_all_micro_lessons_in_level(lvl):
                if node.micro_lesson_id not in progress.completed_micro_lesson_ids:
                    if self.prereq_service.is_micro_lesson_unlocked(
                        node.micro_lesson_id, progress.completed_micro_lesson_ids
                    ):
                        return node

        return None

    # ── Level Progress Calculations ────────────────────────────────────────

    def calculate_level_progress(self, learner_id: str, level_code: str) -> LevelProgressSummary:
        """
        Calculates exact level progress for a given learner and CEFR level (A1-C2).
        
        PROGRESS FORMULA:
        Percentage Completed = (Completed Micro Lessons in Level / Total Micro Lessons in Level) * 100
        """
        progress = self.get_learner_progress(learner_id)
        all_nodes = self.repository.get_all_micro_lessons_in_level(level_code)
        level_obj = self.get_level(level_code)

        total_micro_lessons = len(all_nodes)
        completed_in_level = [
            node.micro_lesson_id
            for node in all_nodes
            if node.micro_lesson_id in progress.completed_micro_lesson_ids
        ]
        completed_micro_lessons_count = len(completed_in_level)

        percentage_completed = (
            round((completed_micro_lessons_count / total_micro_lessons) * 100, 2)
            if total_micro_lessons > 0
            else 0.0
        )

        total_units = len(level_obj.units) if level_obj else 0
        total_topics = sum(len(u.topics) for u in level_obj.units) if level_obj else 0

        # Calculate completed topics & units
        completed_topics_count = 0
        completed_units_count = 0

        if level_obj:
            for unit in level_obj.units:
                unit_fully_completed = True
                for topic in unit.topics:
                    topic_completed = len(topic.micro_lessons) > 0 and all(
                        ml.micro_lesson_id in progress.completed_micro_lesson_ids
                        for ml in topic.micro_lessons
                    )
                    if topic_completed:
                        completed_topics_count += 1
                    else:
                        unit_fully_completed = False

                if unit_fully_completed and len(unit.topics) > 0:
                    completed_units_count += 1

        # Fetch mastery and review summaries from LearnerService
        snapshot = self.learner_service.get_learner_snapshot(learner_id)
        review_due = self.learner_service.get_review_due_items(learner_id)

        mastery_summary = {
            "total_grammar_items": snapshot.get("total_grammar_items", 0),
            "mastered_grammar_count": snapshot.get("mastered_grammar_count", 0),
            "total_vocabulary_items": snapshot.get("total_vocabulary_items", 0),
            "mastered_vocabulary_count": snapshot.get("mastered_vocabulary_count", 0),
        }

        review_summary = {
            "grammar_review_due_count": len(review_due.get("grammar", [])),
            "vocabulary_review_due_count": len(review_due.get("vocabulary", [])),
            "total_review_due_count": len(review_due.get("grammar", [])) + len(review_due.get("vocabulary", [])),
        }

        next_target = self.get_next_course_target(learner_id, level_code)

        return LevelProgressSummary(
            learner_id=learner_id,
            level_code=level_code,
            total_units=total_units,
            completed_units=completed_units_count,
            total_topics=total_topics,
            completed_topics=completed_topics_count,
            total_micro_lessons=total_micro_lessons,
            completed_micro_lessons=completed_micro_lessons_count,
            percentage_completed=percentage_completed,
            current_unit_id=next_target.unit_id if next_target else (progress.current_unit_id),
            current_topic_id=next_target.topic_id if next_target else (progress.current_topic_id),
            current_micro_lesson_id=next_target.micro_lesson_id if next_target else (progress.current_micro_lesson_id),
            remaining_micro_lessons=total_micro_lessons - completed_micro_lessons_count,
            mastery_summary=mastery_summary,
            review_summary=review_summary,
            progress_formula_description=(
                f"Percentage Completed = ({completed_micro_lessons_count} completed / {total_micro_lessons} total) * 100 = {percentage_completed}%"
            ),
        )

    # ── Internal Helper Methods ────────────────────────────────────────────

    def _update_unlocked_lessons(self, progress: LearnerCourseProgress) -> None:
        """
        Dynamically updates unlocked_micro_lesson_ids based on prerequisite rules.
        """
        all_nodes = self.repository.get_all_micro_lessons_in_level(progress.current_level)
        for lvl in self.list_supported_levels():
            for node in self.repository.get_all_micro_lessons_in_level(lvl):
                if node.micro_lesson_id not in progress.unlocked_micro_lesson_ids:
                    if self.prereq_service.is_micro_lesson_unlocked(
                        node.micro_lesson_id, progress.completed_micro_lesson_ids
                    ):
                        progress.unlocked_micro_lesson_ids.append(node.micro_lesson_id)

    def _advance_resume_position(
        self, progress: LearnerCourseProgress, completed_ml_id: str
    ) -> None:
        """
        Advances learner's resume position to the next logical uncompleted course node.
        """
        next_node = self.get_next_course_target(progress.learner_id, progress.current_level)
        if next_node:
            progress.current_level = next_node.level_code
            progress.current_unit_id = next_node.unit_id
            progress.current_topic_id = next_node.topic_id
            progress.current_micro_lesson_id = next_node.micro_lesson_id
            progress.resume_position = {
                "level_code": next_node.level_code,
                "unit_id": next_node.unit_id,
                "topic_id": next_node.topic_id,
                "micro_lesson_id": next_node.micro_lesson_id,
            }
