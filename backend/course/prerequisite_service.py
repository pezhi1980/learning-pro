# backend/course/prerequisite_service.py
"""
ROLE: PREREQUISITE SERVICE

Evaluates prerequisite rules (`requires` and `builds_on`) and unlocking criteria for Course Nodes.
Never uses AI to fabricate prerequisite relationships.
Enforces deterministic validation based on explicit repository rules and sequential node ordering.
"""

from typing import List, Optional, Tuple
from backend.course.course_models import PrerequisiteRule
from backend.course.course_repository import CourseRepository


class PrerequisiteService:
    """
    Evaluates prerequisite rules and unlocking criteria deterministically.
    """

    def __init__(self, repository: Optional[CourseRepository] = None):
        self.repository = repository or CourseRepository()

    def add_prerequisite_rule(
        self,
        source_micro_lesson_id: str,
        target_micro_lesson_id: str,
        relationship: str = "requires",
        description: Optional[str] = None,
    ) -> PrerequisiteRule:
        """
        Admin-ready mechanism to register an explicit prerequisite rule.
        """
        if relationship not in ("requires", "builds_on"):
            raise ValueError(f"Invalid relationship type '{relationship}'. Must be 'requires' or 'builds_on'.")

        rule = PrerequisiteRule(
            rule_id=f"prereq:{source_micro_lesson_id}->{target_micro_lesson_id}",
            source_micro_lesson_id=source_micro_lesson_id,
            target_micro_lesson_id=target_micro_lesson_id,
            relationship=relationship,  # type: ignore
            description=description,
        )
        self.repository.add_prerequisite_rule(rule)
        return rule

    def validate_prerequisites(
        self, target_micro_lesson_id: str, completed_micro_lesson_ids: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validates whether all required prerequisites for a target micro lesson are fulfilled.
        Returns tuple (is_unlocked, unfulfilled_prerequisite_ids).
        """
        completed_set = set(completed_micro_lesson_ids)
        unfulfilled: List[str] = []

        # 1. Check explicit prerequisite rules
        explicit_rules = self.repository.get_prerequisites_for_target(target_micro_lesson_id)
        for rule in explicit_rules:
            if rule.relationship == "requires":
                if rule.source_micro_lesson_id not in completed_set:
                    unfulfilled.append(rule.source_micro_lesson_id)

        # 2. Check sequential topic ordering fallback if no explicit rules
        ml_node = self.repository.get_micro_lesson(target_micro_lesson_id)
        if ml_node:
            # If explicit prerequisite_ids are on the node
            for prereq_id in ml_node.prerequisite_ids:
                if prereq_id not in completed_set and prereq_id not in unfulfilled:
                    unfulfilled.append(prereq_id)

            # If it's not the first item in the topic and has no explicit rules, require previous item in topic
            if ml_node.order > 1 and not explicit_rules and not ml_node.prerequisite_ids:
                prev_id = f"{ml_node.topic_id.replace('topic:', 'ml:')}:{ml_node.order - 1}"
                # If prev_id exists and isn't completed
                prev_node = self.repository.get_micro_lesson(prev_id)
                if prev_node and prev_node.micro_lesson_id not in completed_set:
                    unfulfilled.append(prev_node.micro_lesson_id)

        is_unlocked = len(unfulfilled) == 0
        return is_unlocked, unfulfilled

    def is_micro_lesson_unlocked(
        self, target_micro_lesson_id: str, completed_micro_lesson_ids: List[str]
    ) -> bool:
        """
        Determines if a micro lesson is unlocked based on completed micro lessons.
        """
        is_unlocked, _ = self.validate_prerequisites(target_micro_lesson_id, completed_micro_lesson_ids)
        return is_unlocked
