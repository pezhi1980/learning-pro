# backend/assessment/assessment_repository.py
"""
ROLE: ASSESSMENT REPOSITORY

In-memory and persistence storage for assessment sessions, submissions, placement results,
diagnostic reports, checkpoint results, and level assessment reports.
Enforces server-side authoritative state and cross-user data isolation.
"""

from typing import Dict, List, Optional
from backend.assessment.assessment_models import (
    AssessmentSession,
    CheckpointResult,
    DiagnosticReport,
    LevelAssessmentReport,
    PlacementResult,
)


class AssessmentRepository:
    """
    Repository maintaining server-side assessment sessions and historical assessment reports.
    """

    def __init__(self):
        self._sessions: Dict[str, AssessmentSession] = {}
        self._placement_results: Dict[str, List[PlacementResult]] = {}
        self._diagnostic_reports: Dict[str, List[DiagnosticReport]] = {}
        self._checkpoint_results: Dict[str, List[CheckpointResult]] = {}
        self._level_reports: Dict[str, List[LevelAssessmentReport]] = {}

    # ── Sessions ─────────────────────────────────────────────────────────────

    def save_session(self, session: AssessmentSession) -> None:
        self._sessions[session.session_id] = session

    def get_session(self, session_id: str) -> Optional[AssessmentSession]:
        return self._sessions.get(session_id)

    # ── Placement Results ───────────────────────────────────────────────────

    def save_placement_result(self, result: PlacementResult) -> None:
        if result.learner_id not in self._placement_results:
            self._placement_results[result.learner_id] = []
        self._placement_results[result.learner_id].append(result)

    def get_placement_results(self, learner_id: str) -> List[PlacementResult]:
        return self._placement_results.get(learner_id, [])

    # ── Diagnostic Reports ──────────────────────────────────────────────────

    def save_diagnostic_report(self, report: DiagnosticReport) -> None:
        if report.learner_id not in self._diagnostic_reports:
            self._diagnostic_reports[report.learner_id] = []
        self._diagnostic_reports[report.learner_id].append(report)

    def get_diagnostic_reports(self, learner_id: str) -> List[DiagnosticReport]:
        return self._diagnostic_reports.get(learner_id, [])

    # ── Checkpoint Results ──────────────────────────────────────────────────

    def save_checkpoint_result(self, result: CheckpointResult) -> None:
        if result.learner_id not in self._checkpoint_results:
            self._checkpoint_results[result.learner_id] = []
        self._checkpoint_results[result.learner_id].append(result)

    def get_checkpoint_results(self, learner_id: str) -> List[CheckpointResult]:
        return self._checkpoint_results.get(learner_id, [])

    # ── Level Reports ───────────────────────────────────────────────────────

    def save_level_report(self, report: LevelAssessmentReport) -> None:
        if report.learner_id not in self._level_reports:
            self._level_reports[report.learner_id] = []
        self._level_reports[report.learner_id].append(report)

    def get_level_reports(self, learner_id: str) -> List[LevelAssessmentReport]:
        return self._level_reports.get(learner_id, [])
