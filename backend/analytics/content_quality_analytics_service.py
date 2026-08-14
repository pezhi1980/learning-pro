# backend/analytics/content_quality_analytics_service.py
"""
ROLE: CONTENT QUALITY ANALYTICS SERVICE

Detects suspicious or low-quality curriculum content using performance signals:
- abnormally high failure (>60%)
- high abandonment (>40%)
- frequent user reports (>=3)
- repeated regeneration (>=3)
- validator failure patterns
"""

import logging
from typing import Dict, List, Optional
from backend.analytics.analytics_models import ContentQualitySignalRecord

logger = logging.getLogger(__name__)


class ContentQualityAnalyticsService:
    """
    Service analyzing telemetry signals to flag suspicious content items.
    """

    FAILURE_RATE_THRESHOLD: float = 0.60
    ABANDONMENT_RATE_THRESHOLD: float = 0.40
    REPORT_COUNT_THRESHOLD: int = 3
    REGENERATION_COUNT_THRESHOLD: int = 3

    def __init__(self):
        self._records: Dict[str, ContentQualitySignalRecord] = {}

    def evaluate_content_quality(
        self,
        content_id: str,
        total_attempts: int = 0,
        failure_count: int = 0,
        started_count: int = 0,
        abandoned_count: int = 0,
        report_count: int = 0,
        regeneration_count: int = 0,
    ) -> ContentQualitySignalRecord:
        """
        Evaluates performance telemetry signals and flags content if threshold exceeded.
        """
        failure_rate = round((failure_count / total_attempts), 2) if total_attempts > 0 else 0.0
        abandonment_rate = round((abandoned_count / started_count), 2) if started_count > 0 else 0.0

        flags: List[str] = []

        if failure_rate >= self.FAILURE_RATE_THRESHOLD and total_attempts >= 5:
            flags.append(f"Abnormally High Failure Rate ({failure_rate*100:.0f}% >= {self.FAILURE_RATE_THRESHOLD*100:.0f}%)")

        if abandonment_rate >= self.ABANDONMENT_RATE_THRESHOLD and started_count >= 5:
            flags.append(f"High Abandonment Rate ({abandonment_rate*100:.0f}% >= {self.ABANDONMENT_RATE_THRESHOLD*100:.0f}%)")

        if report_count >= self.REPORT_COUNT_THRESHOLD:
            flags.append(f"Frequent User Reports ({report_count} >= {self.REPORT_COUNT_THRESHOLD})")

        if regeneration_count >= self.REGENERATION_COUNT_THRESHOLD:
            flags.append(f"Repeated Regenerations ({regeneration_count} >= {self.REGENERATION_COUNT_THRESHOLD})")

        is_suspicious = len(flags) > 0

        record = ContentQualitySignalRecord(
            content_id=content_id,
            failure_rate=failure_rate,
            abandonment_rate=abandonment_rate,
            report_count=report_count,
            regeneration_count=regeneration_count,
            suspicious_flags=flags,
            is_suspicious=is_suspicious,
        )

        self._records[content_id] = record

        if is_suspicious:
            logger.warning(f"SUSPICIOUS CONTENT FLAGGED: '{content_id}' flags={flags}.")

        return record

    def list_suspicious_content(self) -> List[ContentQualitySignalRecord]:
        return [r for r in self._records.values() if r.is_suspicious]
