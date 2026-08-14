# backend/learning/learning_decision_service.py
"""
ROLE: LEARNING DECISION SERVICE

Primary Learning Decision Engine that decides WHAT a learner should study next.
Considers current learner state, active error patterns, review due dates, and PDF-backed curriculum sequence.
Converts LearningDecision into CurriculumAssignmentRequest for generation orchestration.
ContentAgent is NEVER called by this service.
"""

from datetime import datetime, timezone
from typing import Optional
from backend.course import CourseService
from backend.learner import LearnerService
from backend.learning.decision_models import DecisionType, LearningDecision
from backend.learning.learning_config import LearningConfig
from backend.learning.target_selection_service import TargetSelectionService
from backend.schemas.agent_input import CurriculumAssignmentRequest, GenerationMode, TaskDifficulty


class LearningDecisionService:
    """
    Central Learning Decision Engine orchestrating target selection and session decision generation.
    """

    def __init__(
        self,
        learner_service: Optional[LearnerService] = None,
        target_selector: Optional[TargetSelectionService] = None,
        config: Optional[LearningConfig] = None,
        course_service: Optional[CourseService] = None,
    ):
        self.learner_service = learner_service or LearnerService()
        self.target_selector = target_selector or TargetSelectionService(learner_service=self.learner_service)
        self.config = config or LearningConfig()
        self.course_service = course_service or CourseService(learner_service=self.learner_service)


    def determine_next_learning_decision(
        self,
        learner_id: str,
        target_language: str = "en",
        native_language: str = "fa",
        requested_level: str = "A1",
    ) -> LearningDecision:
        """
        Determines the optimal next learning decision for a learner according to priority order:
        1. Active Repair Needs
        2. Due Review Items
        3. New Authorized Curriculum Target
        """
        now = datetime.now(timezone.utc)
        dec_id = f"dec:{learner_id}:{int(now.timestamp())}"

        # ── 1. Check Active Repair Needs ──────────────────────────────────────
        repair_target = self.target_selector.select_repair_target(learner_id)
        if repair_target:
            t_type, target_id = repair_target
            if t_type == "grammar":
                return LearningDecision(
                    decision_id=dec_id,
                    learner_id=learner_id,
                    decision_type=DecisionType.grammar_repair,
                    generation_mode=GenerationMode.grammar_repair,
                    target_language=target_language,
                    native_language=native_language,
                    selected_target_grammar_ids=[target_id],
                    reason_codes=["ACTIVE_GRAMMAR_ERROR_REPAIR"],
                )
            else:
                return LearningDecision(
                    decision_id=dec_id,
                    learner_id=learner_id,
                    decision_type=DecisionType.vocabulary_repair,
                    generation_mode=GenerationMode.vocabulary_repair,
                    target_language=target_language,
                    native_language=native_language,
                    selected_target_vocabulary_ids=[target_id.replace(":sense", "")],
                    selected_target_vocabulary_sense_ids=[target_id] if ":sense" in target_id else [],
                    reason_codes=["ACTIVE_VOCABULARY_SENSE_REPAIR"],
                )

        # ── 2. Check Due Review Items ─────────────────────────────────────────
        g_due, v_due = self.target_selector.select_review_targets(learner_id)
        if g_due or v_due:
            return LearningDecision(
                decision_id=dec_id,
                learner_id=learner_id,
                decision_type=DecisionType.smart_review,
                generation_mode=GenerationMode.mixed_practice,
                target_language=target_language,
                native_language=native_language,
                selected_target_grammar_ids=g_due,
                selected_target_vocabulary_ids=[v.replace(":sense", "") for v in v_due],
                selected_target_vocabulary_sense_ids=[v for v in v_due if ":sense" in v],
                reason_codes=["SMART_REVIEW_DUE_ITEMS"],
            )

        # ── 3. Select Next New Authorized Curriculum Target ───────────────────
        course_target_node = self.course_service.get_next_course_target(learner_id, level_code=requested_level)
        if course_target_node and course_target_node.grammar_target_ids:
            allowed_g, allowed_v = self.target_selector.select_known_supporting_content(learner_id)
            g_target = course_target_node.grammar_target_ids[0]
            v_targets = course_target_node.vocabulary_target_ids
            return LearningDecision(
                decision_id=dec_id,
                learner_id=learner_id,
                decision_type=DecisionType.new_learning,
                generation_mode=GenerationMode.grammar_micro_lesson,
                target_language=target_language,
                native_language=native_language,
                selected_target_grammar_ids=[g_target],
                selected_target_vocabulary_ids=[v.replace(":sense", "") for v in v_targets],
                selected_target_vocabulary_sense_ids=[v for v in v_targets if ":sense" in v],
                selected_allowed_grammar_ids=allowed_g,
                selected_allowed_vocabulary_ids=allowed_v,
                reason_codes=["COURSE_PROGRESSION_NEXT_TARGET"],
            )

        new_g_target = self.target_selector.select_next_new_grammar_target(learner_id, level=requested_level)
        if new_g_target:
            allowed_g, allowed_v = self.target_selector.select_known_supporting_content(learner_id)
            return LearningDecision(
                decision_id=dec_id,
                learner_id=learner_id,
                decision_type=DecisionType.new_learning,
                generation_mode=GenerationMode.grammar_micro_lesson,
                target_language=target_language,
                native_language=native_language,
                selected_target_grammar_ids=[new_g_target],
                selected_allowed_grammar_ids=allowed_g,
                selected_allowed_vocabulary_ids=allowed_v,
                reason_codes=["NEW_AUTHORITATIVE_GRAMMAR_CURRICULUM"],
            )

        # Fallback to Vocabulary New Learning
        new_v_target = self.target_selector.select_next_new_vocabulary_target(learner_id, level=requested_level)
        if new_v_target:
            return LearningDecision(
                decision_id=dec_id,
                learner_id=learner_id,
                decision_type=DecisionType.new_learning,
                generation_mode=GenerationMode.vocabulary_lesson,
                target_language=target_language,
                native_language=native_language,
                selected_target_vocabulary_ids=[new_v_target.replace(":sense", "")],
                selected_target_vocabulary_sense_ids=[new_v_target] if ":sense" in new_v_target else [],
                reason_codes=["NEW_AUTHORITATIVE_VOCABULARY_CURRICULUM"],
            )


        # Default fallback if everything is mastered
        return LearningDecision(
            decision_id=dec_id,
            learner_id=learner_id,
            decision_type=DecisionType.continue_course,
            generation_mode=GenerationMode.mixed_practice,
            target_language=target_language,
            native_language=native_language,
            reason_codes=["COURSE_MASTERY_REINFORCEMENT"],
        )

    def to_assignment_request(self, decision: LearningDecision) -> CurriculumAssignmentRequest:
        """
        Converts a LearningDecision into a CurriculumAssignmentRequest for CurriculumAssignmentService.
        """
        return CurriculumAssignmentRequest(
            request_id=f"req:{decision.decision_id}",
            target_language=decision.target_language,
            native_language=decision.native_language,
            generation_mode=decision.generation_mode,
            task_difficulty=TaskDifficulty.controlled_recall,
            target_grammar_ids=decision.selected_target_grammar_ids,
            target_vocabulary_ids=decision.selected_target_vocabulary_ids,
            target_vocabulary_sense_ids=decision.selected_target_vocabulary_sense_ids,
            allowed_grammar_ids=decision.selected_allowed_grammar_ids,
            allowed_vocabulary_ids=decision.selected_allowed_vocabulary_ids,
            allowed_vocabulary_sense_ids=decision.selected_allowed_vocabulary_sense_ids,
        )
