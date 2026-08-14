# backend/course/course_repository.py
"""
ROLE: COURSE REPOSITORY

Constructs and manages the authoritative Course Hierarchy (Level -> Unit -> Topic -> Micro Lesson)
dynamically over PDF-backed CurriculumService items for levels A1, A2, B1, B2, C1, C2.
Maintains prerequisite definitions and learner course progress state.
"""

from typing import Dict, List, Optional
from backend.curriculum import CurriculumService
from backend.course.course_models import (
    SUPPORTED_LEVELS,
    CourseLevel,
    CourseTopic,
    CourseUnit,
    LearnerCourseProgress,
    MicroLessonNode,
    PrerequisiteRule,
)


class CourseRepository:
    """
    Repository organizing PDF curriculum into deterministic Course Structure (Level -> Unit -> Topic -> Micro Lesson)
    and managing learner course progress.
    """

    def __init__(self, curriculum_service: Optional[CurriculumService] = None):
        self.curriculum_service = curriculum_service or CurriculumService()
        self._levels_cache: Dict[str, CourseLevel] = {}
        self._prerequisites: List[PrerequisiteRule] = []
        self._learner_progress: Dict[str, LearnerCourseProgress] = {}
        self._build_course_structure()

    def _build_course_structure(self) -> None:
        """
        Builds the 4-tier hierarchy for all supported levels (A1-C2) using authoritative PDF curriculum targets.
        """
        for level_code in SUPPORTED_LEVELS:
            grammar_items = self.curriculum_service.list_grammar_by_level(level_code)
            vocab_items = self.curriculum_service.list_vocabulary_by_level(level_code)

            # Sort items to ensure stable ordering across runs
            grammar_items = sorted(grammar_items, key=lambda g: (g.grammar_code, g.source_item_id))
            vocab_items = sorted(vocab_items, key=lambda v: (v.lexeme, v.source_item_id))

            units: List[CourseUnit] = []
            
            # Divide level items into manageable units (e.g. 10 grammar items per unit or chunked)
            unit_chunk_size = max(1, (len(grammar_items) + 4) // 5) if grammar_items else 10
            
            unit_idx = 1
            for g_offset in range(0, len(grammar_items), unit_chunk_size):
                u_grammar = grammar_items[g_offset : g_offset + unit_chunk_size]
                
                # Pair with corresponding slice of vocabulary items
                v_start = int((g_offset / max(1, len(grammar_items))) * len(vocab_items))
                v_end = int(((g_offset + unit_chunk_size) / max(1, len(grammar_items))) * len(vocab_items))
                u_vocab = vocab_items[v_start:v_end]

                unit_id = f"unit:{level_code}:{unit_idx}"
                unit_title = f"{level_code} Unit {unit_idx}"

                topics: List[CourseTopic] = []
                topic_chunk_size = max(1, (len(u_grammar) + 1) // 2)
                
                topic_idx = 1
                for t_offset in range(0, len(u_grammar), topic_chunk_size):
                    t_grammar = u_grammar[t_offset : t_offset + topic_chunk_size]
                    
                    topic_id = f"topic:{level_code}:{unit_idx}:{topic_idx}"
                    topic_title = f"{unit_title} - Topic {topic_idx}"

                    micro_lessons: List[MicroLessonNode] = []
                    ml_idx = 1
                    for g_item in t_grammar:
                        ml_id = f"ml:{level_code}:{unit_idx}:{topic_idx}:{ml_idx}"
                        
                        # Select supporting vocab items for this micro lesson
                        sub_v_items = u_vocab[
                            (ml_idx - 1) * 3 : ml_idx * 3
                        ]
                        vocab_ids = [
                            f"{v.source_item_id}:sense" if v.guideword else v.source_item_id
                            for v in sub_v_items
                        ]

                        micro_lesson = MicroLessonNode(
                            micro_lesson_id=ml_id,
                            topic_id=topic_id,
                            unit_id=unit_id,
                            level_code=level_code,
                            title=f"Micro Lesson: {g_item.label or g_item.grammar_code}",
                            order=ml_idx,
                            grammar_target_ids=[g_item.source_item_id],
                            vocabulary_target_ids=vocab_ids,
                            prerequisite_ids=[],
                        )
                        micro_lessons.append(micro_lesson)
                        ml_idx += 1

                    topic = CourseTopic(
                        topic_id=topic_id,
                        unit_id=unit_id,
                        level_code=level_code,
                        title=topic_title,
                        order=topic_idx,
                        micro_lessons=micro_lessons,
                    )
                    topics.append(topic)
                    topic_idx += 1

                unit = CourseUnit(
                    unit_id=unit_id,
                    level_code=level_code,
                    title=unit_title,
                    order=unit_idx,
                    topics=topics,
                )
                units.append(unit)
                unit_idx += 1

            level_obj = CourseLevel(
                level_code=level_code,
                title=f"CEFR Level {level_code}",
                description=f"Authoritative course structure for CEFR {level_code}",
                units=units,
            )
            self._levels_cache[level_code] = level_obj

    # ── Level & Structure API ───────────────────────────────────────────────

    def get_level(self, level_code: str) -> Optional[CourseLevel]:
        if level_code not in SUPPORTED_LEVELS:
            return None
        return self._levels_cache.get(level_code)

    def list_supported_levels(self) -> List[str]:
        return list(SUPPORTED_LEVELS)

    def get_micro_lesson(self, micro_lesson_id: str) -> Optional[MicroLessonNode]:
        parts = micro_lesson_id.split(":")
        if len(parts) >= 2:
            level_code = parts[1]
            level_obj = self.get_level(level_code)
            if level_obj:
                for unit in level_obj.units:
                    for topic in unit.topics:
                        for ml in topic.micro_lessons:
                            if ml.micro_lesson_id == micro_lesson_id:
                                return ml
        return None

    def get_all_micro_lessons_in_level(self, level_code: str) -> List[MicroLessonNode]:
        level_obj = self.get_level(level_code)
        if not level_obj:
            return []
        
        result: List[MicroLessonNode] = []
        for unit in level_obj.units:
            for topic in unit.topics:
                result.extend(topic.micro_lessons)
        return result

    # ── Prerequisites API ───────────────────────────────────────────────────

    def add_prerequisite_rule(self, rule: PrerequisiteRule) -> None:
        self._prerequisites.append(rule)
        # Update micro lesson node if cached
        ml_target = self.get_micro_lesson(rule.target_micro_lesson_id)
        if ml_target and rule.source_micro_lesson_id not in ml_target.prerequisite_ids:
            ml_target.prerequisite_ids.append(rule.source_micro_lesson_id)

    def list_prerequisite_rules(self) -> List[PrerequisiteRule]:
        return list(self._prerequisites)

    def get_prerequisites_for_target(self, target_micro_lesson_id: str) -> List[PrerequisiteRule]:
        return [p for p in self._prerequisites if p.target_micro_lesson_id == target_micro_lesson_id]

    # ── Learner Progress Persistence ────────────────────────────────────────

    def get_learner_progress(self, learner_id: str) -> LearnerCourseProgress:
        if learner_id not in self._learner_progress:
            # Initialize with default unlocked first micro lesson of A1
            a1_level = self.get_level("A1")
            first_ml_id = None
            first_unit_id = None
            first_topic_id = None

            if a1_level and a1_level.units:
                first_unit_id = a1_level.units[0].unit_id
                if a1_level.units[0].topics:
                    first_topic_id = a1_level.units[0].topics[0].topic_id
                    if a1_level.units[0].topics[0].micro_lessons:
                        first_ml_id = a1_level.units[0].topics[0].micro_lessons[0].micro_lesson_id

            unlocked = [first_ml_id] if first_ml_id else []

            progress = LearnerCourseProgress(
                learner_id=learner_id,
                current_level="A1",
                current_unit_id=first_unit_id,
                current_topic_id=first_topic_id,
                current_micro_lesson_id=first_ml_id,
                completed_micro_lesson_ids=[],
                unlocked_micro_lesson_ids=unlocked,
                resume_position={
                    "level_code": "A1",
                    "unit_id": first_unit_id,
                    "topic_id": first_topic_id,
                    "micro_lesson_id": first_ml_id,
                },
            )
            self._learner_progress[learner_id] = progress

        return self._learner_progress[learner_id]

    def save_learner_progress(self, progress: LearnerCourseProgress) -> None:
        self._learner_progress[progress.learner_id] = progress
