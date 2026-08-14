# backend/course/__init__.py
"""
ROLE: COURSE ARCHITECTURE PACKAGE

Defines the complete Course Hierarchy (Level -> Unit -> Topic -> Micro Lesson),
deterministic course progression tracking, prerequisite rules engine, and level progress calculation services.
Organizes PDF-backed Curriculum targets without redefining curriculum authority.
"""

from .course_models import (
    SUPPORTED_LEVELS,
    CourseLevel,
    CourseUnit,
    CourseTopic,
    MicroLessonNode,
    PrerequisiteRule,
    LearnerCourseProgress,
    LevelProgressSummary,
)
from .course_repository import CourseRepository
from .prerequisite_service import PrerequisiteService
from .course_service import CourseService

__all__ = [
    "SUPPORTED_LEVELS",
    "CourseLevel",
    "CourseUnit",
    "CourseTopic",
    "MicroLessonNode",
    "PrerequisiteRule",
    "LearnerCourseProgress",
    "LevelProgressSummary",
    "CourseRepository",
    "PrerequisiteService",
    "CourseService",
]

