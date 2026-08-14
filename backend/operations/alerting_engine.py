# backend/operations/alerting_engine.py

import time
import uuid
import logging
from typing import Dict, List, Optional
from .operational_models import AlertNotification

logger = logging.getLogger(__name__)


class AlertingEngine:
    def __init__(self, cooldown_seconds: float = 300.0):
        self.cooldown_seconds = cooldown_seconds
        self._last_alert_time: Dict[str, float] = {}
        self.active_alerts: List[AlertNotification] = []

    def trigger_alert(
        self,
        alert_key: str,
        severity: str,
        component: str,
        message: str,
    ) -> Optional[AlertNotification]:
        now = time.time()
        last_time = self._last_alert_time.get(alert_key, 0.0)

        # De-duplication / Anti-Spam Cooldown check
        if (now - last_time) < self.cooldown_seconds:
            logger.info(f"ALERT THROTTLED (cooldown active): [{alert_key}] {message}")
            return AlertNotification(
                alert_id=str(uuid.uuid4()),
                alert_key=alert_key,
                severity=severity,
                component=component,
                message=message,
                timestamp=now,
                throttled=True,
            )

        self._last_alert_time[alert_key] = now
        notification = AlertNotification(
            alert_id=str(uuid.uuid4()),
            alert_key=alert_key,
            severity=severity,
            component=component,
            message=message,
            timestamp=now,
            throttled=False,
        )

        self.active_alerts.append(notification)
        logger.warning(f"CRITICAL ALERT TRIGGERED: [{severity}] [{component}] {message}")
        return notification

    def evaluate_metrics(self, metrics_summary: Dict) -> List[AlertNotification]:
        alerts = []
        error_rate = metrics_summary.get("error_rate_percent", 0.0)
        counters = metrics_summary.get("counters", {})

        if error_rate >= 10.0:
            alert = self.trigger_alert(
                alert_key="high_api_error_rate",
                severity="CRITICAL",
                component="api_gateway",
                message=f"API Error Rate breached threshold: {error_rate}%",
            )
            if alert and not alert.throttled:
                alerts.append(alert)

        if counters.get("database_failures_total", 0) > 0:
            alert = self.trigger_alert(
                alert_key="database_failure_detected",
                severity="CRITICAL",
                component="database",
                message="Database connectivity failure detected.",
            )
            if alert and not alert.throttled:
                alerts.append(alert)

        if counters.get("speech_tts_failures_total", 0) >= 5:
            alert = self.trigger_alert(
                alert_key="tts_provider_failure",
                severity="WARNING",
                component="tts_provider",
                message="Multiple Speech/TTS failures encountered.",
            )
            if alert and not alert.throttled:
                alerts.append(alert)

        return alerts
