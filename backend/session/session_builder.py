# backend/session/session_builder.py
"""
ROLE: SESSION BUILDER

Converts LearningDecision outputs into structured Daily Learning Sessions containing ordered activities.
Enforces Novelty Budget (max 1 primary new target per activity segment).
Controls session length, activity counts, review/repair counts, and activity ordering.
All targets in generated activities are pre-authorized by LearningDecision Engine.
"""

from typing import List, Optional
from backend.learning.decision_models import DecisionType, LearningDecision
from backend.session.session_models import ActivityType, DailyLearningSession, SessionActivity, SessionStatus


class SessionBuilder:
    """
    Constructs structured Daily Learning Sessions from LearningDecision objects.
    """

    def __init__(
        self,
        default_max_activities: int = 3,
        default_activity_duration_minutes: int = 5,
    ):
        self.default_max_activities = default_max_activities
        self.default_activity_duration_minutes = default_activity_duration_minutes

    def build_session(self, decision: LearningDecision) -> DailyLearningSession:
        """
        Converts a LearningDecision into a structured, persistent-ready DailyLearningSession.
        """
        session_id = f"sess:{decision.learner_id}:{decision.decision_id.split(':')[-1]}"
        activities: List[SessionActivity] = []
        activity_order = 1

        # ── 1. Repair Activities ──────────────────────────────────────────────
        if decision.decision_type in (DecisionType.grammar_repair, DecisionType.vocabulary_repair):
            if decision.selected_target_grammar_ids:
                activities.append(
                    SessionActivity(
                        activity_id=f"{session_id}:act:{activity_order}",
                        activity_type=ActivityType.grammar_repair,
                        title=f"Grammar Repair: {decision.selected_target_grammar_ids[0]}",
                        order=activity_order,
                        target_grammar_ids=decision.selected_target_grammar_ids,
                        allowed_grammar_ids=decision.selected_allowed_grammar_ids,
                        allowed_vocabulary_ids=decision.selected_allowed_vocabulary_ids,
                        estimated_duration_minutes=self.default_activity_duration_minutes,
                    )
                )
                activity_order += 1
            elif decision.selected_target_vocabulary_ids or decision.selected_target_vocabulary_sense_ids:
                v_ids = decision.selected_target_vocabulary_ids or decision.selected_target_vocabulary_sense_ids
                activities.append(
                    SessionActivity(
                        activity_id=f"{session_id}:act:{activity_order}",
                        activity_type=ActivityType.vocabulary_repair,
                        title=f"Vocabulary Repair: {v_ids[0]}",
                        order=activity_order,
                        target_vocabulary_ids=decision.selected_target_vocabulary_ids,
                        target_vocabulary_sense_ids=decision.selected_target_vocabulary_sense_ids,
                        allowed_grammar_ids=decision.selected_allowed_grammar_ids,
                        allowed_vocabulary_ids=decision.selected_allowed_vocabulary_ids,
                        estimated_duration_minutes=self.default_activity_duration_minutes,
                    )
                )
                activity_order += 1

        # ── 2. Smart Review Activities ─────────────────────────────────────────
        if decision.decision_type == DecisionType.smart_review or (
            decision.selected_target_grammar_ids and decision.decision_type != DecisionType.new_learning
        ):
            if decision.selected_target_grammar_ids or decision.selected_target_vocabulary_ids:
                activities.append(
                    SessionActivity(
                        activity_id=f"{session_id}:act:{activity_order}",
                        activity_type=ActivityType.smart_review,
                        title="Smart Review Session",
                        order=activity_order,
                        target_grammar_ids=decision.selected_target_grammar_ids,
                        target_vocabulary_ids=decision.selected_target_vocabulary_ids,
                        target_vocabulary_sense_ids=decision.selected_target_vocabulary_sense_ids,
                        allowed_grammar_ids=decision.selected_allowed_grammar_ids,
                        allowed_vocabulary_ids=decision.selected_allowed_vocabulary_ids,
                        estimated_duration_minutes=self.default_activity_duration_minutes,
                    )
                )
                activity_order += 1

        # ── 3. Primary New Target (Enforce Novelty Budget: 1 Primary Target) ──
        if decision.decision_type == DecisionType.new_learning or (
            decision.selected_target_grammar_ids and not activities
        ):
            if decision.selected_target_grammar_ids:
                # Primary Grammar New Target
                primary_g = decision.selected_target_grammar_ids[0]
                activities.append(
                    SessionActivity(
                        activity_id=f"{session_id}:act:{activity_order}",
                        activity_type=ActivityType.new_grammar,
                        title=f"New Grammar: {primary_g}",
                        order=activity_order,
                        target_grammar_ids=[primary_g],  # Strict novelty budget: 1 new target
                        target_vocabulary_ids=decision.selected_target_vocabulary_ids[:3],
                        target_vocabulary_sense_ids=decision.selected_target_vocabulary_sense_ids[:3],
                        allowed_grammar_ids=decision.selected_allowed_grammar_ids,
                        allowed_vocabulary_ids=decision.selected_allowed_vocabulary_ids,
                        estimated_duration_minutes=self.default_activity_duration_minutes,
                    )
                )
                activity_order += 1

            elif decision.selected_target_vocabulary_ids:
                # Primary Vocab New Target
                primary_v = decision.selected_target_vocabulary_ids[0]
                activities.append(
                    SessionActivity(
                        activity_id=f"{session_id}:act:{activity_order}",
                        activity_type=ActivityType.new_vocabulary,
                        title=f"New Vocabulary: {primary_v}",
                        order=activity_order,
                        target_vocabulary_ids=[primary_v],
                        target_vocabulary_sense_ids=decision.selected_target_vocabulary_sense_ids[:1],
                        allowed_grammar_ids=decision.selected_allowed_grammar_ids,
                        allowed_vocabulary_ids=decision.selected_allowed_vocabulary_ids,
                        estimated_duration_minutes=self.default_activity_duration_minutes,
                    )
                )
                activity_order += 1

        # ── 4. Mixed Practice / Reinforcement Fallback ────────────────────────
        if len(activities) < self.default_max_activities:
            activities.append(
                SessionActivity(
                    activity_id=f"{session_id}:act:{activity_order}",
                    activity_type=ActivityType.mixed_practice,
                    title="Mixed Practice & Mastery Reinforcement",
                    order=activity_order,
                    allowed_grammar_ids=decision.selected_allowed_grammar_ids,
                    allowed_vocabulary_ids=decision.selected_allowed_vocabulary_ids,
                    estimated_duration_minutes=self.default_activity_duration_minutes,
                )
            )
            activity_order += 1

        total_duration = sum(act.estimated_duration_minutes for act in activities)
        activity_ids = [act.activity_id for act in activities]

        return DailyLearningSession(
            session_id=session_id,
            learner_id=decision.learner_id,
            target_language=decision.target_language,
            native_language=decision.native_language or "fa",
            requested_level="A1",
            status=SessionStatus.created,
            activities=activities,
            current_activity_id=activity_ids[0] if activity_ids else None,
            completed_activity_ids=[],
            remaining_activity_ids=activity_ids,
            total_estimated_duration_minutes=total_duration,
        )
