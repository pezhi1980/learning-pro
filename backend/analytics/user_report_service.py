# backend/analytics/user_report_service.py
"""
ROLE: USER CONTENT REPORTING SERVICE

Receives learner issue reports for curriculum content across 6 categories:
wrong_answer, unclear_explanation, unnatural_example, audio_problem, typo, technical_problem.
Attaches lesson_id, exercise_id, content_version, and source_trace for complete traceability.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from backend.analytics.analytics_models import ReportType, UserReportRecord

logger = logging.getLogger(__name__)


class UserReportService:
    """
    Service logging and querying user content reports with complete source traceability.
    """

    def __init__(self):
        self._reports: List[UserReportRecord] = []

    def submit_report(
        self,
        learner_id: str,
        report_type: ReportType,
        description: str,
        lesson_id: Optional[str] = None,
        exercise_id: Optional[str] = None,
        content_version: Optional[str] = None,
        source_trace: Optional[List[str]] = None,
    ) -> UserReportRecord:

        now = datetime.now(timezone.utc)
        report_id = f"rpt:{report_type.value}:{int(now.timestamp())}:{len(self._reports) + 1}"

        record = UserReportRecord(
            report_id=report_id,
            learner_id=learner_id,
            report_type=report_type,
            description=description,
            lesson_id=lesson_id,
            exercise_id=exercise_id,
            content_version=content_version,
            source_trace=source_trace or [],
            created_at=now,
        )

        self._reports.append(record)
        logger.info(f"User content report submitted [{report_type.value}] by learner '{learner_id}' (id={report_id}).")
        return record

    def list_reports(
        self,
        lesson_id: Optional[str] = None,
        report_type: Optional[ReportType] = None,
        limit: int = 100,
    ) -> List[UserReportRecord]:

        results = self._reports
        if lesson_id:
            results = [r for r in results if r.lesson_id == lesson_id]
        if report_type:
            results = [r for r in results if r.report_type == report_type]

        return results[-limit:]
