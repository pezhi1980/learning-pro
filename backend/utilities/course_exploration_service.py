# backend/utilities/course_exploration_service.py
"""
ROLE: COURSE EXPLORATION SERVICE

Provides hierarchy browsing across Units, Topics, Micro-lessons, and CEFR levels (A1-C2).
"""

import logging
from typing import Any, Dict, List, Optional
from backend.course import CourseRepository
from backend.curriculum import CurriculumService

logger = logging.getLogger(__name__)


class CourseExplorationService:
    """
    Service exploring course structure and curriculum layout.
    """

    def __init__(
        self,
        course_repository: Optional[CourseRepository] = None,
        curriculum_service: Optional[CurriculumService] = None,
    ):
        self.course_repository = course_repository or CourseRepository()
        self.curriculum_service = curriculum_service or CurriculumService()

    def explore_level_structure(self, level: str) -> Dict[str, Any]:
        """
        Returns full hierarchy of units and topics for CEFR level.
        """
        level_obj = self.course_repository.get_level(level.upper())
        units = level_obj.units if level_obj else []

        unit_list = []
        for u in units:
            unit_list.append({
                "unit_id": u.unit_id,
                "title": u.title,
                "level": u.level_code,
                "topics_count": len(u.topics),
                "topics": [{"topic_id": t.topic_id, "title": t.title} for t in u.topics],
            })


        return {
            "level": level.upper(),
            "total_units": len(unit_list),
            "units": unit_list,
        }

