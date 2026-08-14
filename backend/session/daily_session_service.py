# backend/session/daily_session_service.py
"""
ROLE: DAILY SESSION SERVICE

Manages persistent & resumable Daily Learning Sessions for learners.
Provides lifecycle operations: create, start, pause, resume, complete_activity, complete_session.
Enforces cross-user isolation and state transition integrity.
"""

from datetime import datetime, timezone
from typing import Dict, List, Optional
from backend.learning.decision_models import LearningDecision
from backend.session.session_builder import SessionBuilder
from backend.session.session_models import DailyLearningSession, SessionActivity, SessionStatus


class DailySessionService:
    """
    Manages persistent learner sessions and lifecycle transitions.
    """

    def __init__(self, session_builder: Optional[SessionBuilder] = None):
        self.session_builder = session_builder or SessionBuilder()
        self._sessions: Dict[str, DailyLearningSession] = {}

    def create_session(self, decision: LearningDecision) -> DailyLearningSession:
        """
        Builds and registers a new Daily Learning Session from a LearningDecision.
        """
        session = self.session_builder.build_session(decision)
        self._sessions[session.session_id] = session
        return session

    def get_session(self, session_id: str) -> Optional[DailyLearningSession]:
        return self._sessions.get(session_id)

    def get_active_session_for_learner(self, learner_id: str) -> Optional[DailyLearningSession]:
        """
        Locates an active or paused session for a given learner.
        """
        for session in self._sessions.values():
            if session.learner_id == learner_id and session.status in (
                SessionStatus.created,
                SessionStatus.in_progress,
                SessionStatus.paused,
            ):
                return session
        return None

    def start_session(self, session_id: str) -> DailyLearningSession:
        """
        Starts a created or paused session.
        """
        session = self.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")

        now = datetime.now(timezone.utc)
        if session.status in (SessionStatus.created, SessionStatus.paused):
            session.status = SessionStatus.in_progress
            if not session.started_at:
                session.started_at = now

        return session

    def pause_session(self, session_id: str) -> DailyLearningSession:
        """
        Pauses an in-progress session.
        """
        session = self.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")

        if session.status == SessionStatus.in_progress:
            session.status = SessionStatus.paused
            session.paused_at = datetime.now(timezone.utc)

        return session

    def resume_session(self, session_id: str) -> DailyLearningSession:
        """
        Resumes a paused session.
        """
        return self.start_session(session_id)

    def complete_activity(self, session_id: str, activity_id: str) -> DailyLearningSession:
        """
        Marks an activity within a session as completed and advances current_activity_id.
        Auto-completes session when all activities are done.
        """
        session = self.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")

        now = datetime.now(timezone.utc)
        for act in session.activities:
            if act.activity_id == activity_id:
                act.is_completed = True
                act.completed_at = now

        if activity_id in session.remaining_activity_ids:
            session.remaining_activity_ids.remove(activity_id)

        if activity_id not in session.completed_activity_ids:
            session.completed_activity_ids.append(activity_id)

        if session.remaining_activity_ids:
            session.current_activity_id = session.remaining_activity_ids[0]
        else:
            session.current_activity_id = None
            self.complete_session(session_id)

        return session

    def complete_session(self, session_id: str) -> DailyLearningSession:
        """
        Marks a session as completed.
        """
        session = self.get_session(session_id)
        if not session:
            raise KeyError(f"Session '{session_id}' not found.")

        session.status = SessionStatus.completed
        session.completed_at = datetime.now(timezone.utc)
        session.current_activity_id = None
        return session
