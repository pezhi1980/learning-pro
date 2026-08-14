# backend/course/course_models.py
"""
ROLE: COURSE ARCHITECTURE DATA MODELS

Defines normalized internal data structures for the Course Hierarchy:
Level -> Unit -> Topic -> Micro Lesson
Also defines models for Prerequisite rules, Learner Course Progress, and Level Progress Summaries.
All educational targets reference authoritative PDF Curriculum items.
"""

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field


SUPPORTED_LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"]


class MicroLessonNode(BaseModel):
    micro_lesson_id: str
    topic_id: str
    unit_id: str
    level_code: str
    title: str
    order: int
    grammar_target_ids: List[str] = Field(default_factory=list)
    vocabulary_target_ids: List[str] = Field(default_factory=list)
    prerequisite_ids: List[str] = Field(default_factory=list)


class CourseTopic(BaseModel):
    topic_id: str
    unit_id: str
    level_code: str
    title: str
    order: int
    micro_lessons: List[MicroLessonNode] = Field(default_factory=list)


class CourseUnit(BaseModel):
    unit_id: str
    level_code: str
    title: str
    order: int
    topics: List[CourseTopic] = Field(default_factory=list)


class CourseLevel(BaseModel):
    level_code: str  # A1, A2, B1, B2, C1, C2
    title: str
    description: Optional[str] = None
    units: List[CourseUnit] = Field(default_factory=list)


class PrerequisiteRule(BaseModel):
    rule_id: str
    source_micro_lesson_id: str  # Required prerequisite
    target_micro_lesson_id: str  # Dependent item
    relationship: Literal["requires", "builds_on"]
    description: Optional[str] = None


class LearnerCourseProgress(BaseModel):
    learner_id: str
    current_level: str = "A1"
    current_unit_id: Optional[str] = None
    current_topic_id: Optional[str] = None
    current_micro_lesson_id: Optional[str] = None
    completed_micro_lesson_ids: List[str] = Field(default_factory=list)
    unlocked_micro_lesson_ids: List[str] = Field(default_factory=list)
    resume_position: Dict[str, Optional[str]] = Field(default_factory=dict)
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class LevelProgressSummary(BaseModel):
    learner_id: str
    level_code: str
    total_units: int
    completed_units: int
    total_topics: int
    completed_topics: int
    total_micro_lessons: int
    completed_micro_lessons: int
    percentage_completed: float
    current_unit_id: Optional[str] = None
    current_topic_id: Optional[str] = None
    current_micro_lesson_id: Optional[str] = None
    remaining_micro_lessons: int
    mastery_summary: Dict[str, Any] = Field(default_factory=dict)
    review_summary: Dict[str, Any] = Field(default_factory=dict)
    progress_formula_description: str = (
        "Percentage Completed = (Completed Micro Lessons in Level / Total Micro Lessons in Level) * 100"
    )
