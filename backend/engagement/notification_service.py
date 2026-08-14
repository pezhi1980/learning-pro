# backend/engagement/notification_service.py
"""
ROLE: NOTIFICATION SERVICE

Generates and manages configurable notifications for:
- review_due
- learning_reminder
- unfinished_session
- assessment_availability
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from backend.engagement.engagement_models import NotificationRecord, NotificationTriggerType

logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service managing learner notification alerts.
    """

    def __init__(self):
        self._notifications: List[NotificationRecord] = []

    def send_notification(
        self,
        recipient_id: str,
        trigger_type: NotificationTriggerType,
        title: str,
        message: str,
    ) -> NotificationRecord:

        now = datetime.now(timezone.utc)
        nid = f"notif:{trigger_type.value}:{int(now.timestamp())}:{len(self._notifications) + 1}"

        record = NotificationRecord(
            notification_id=nid,
            recipient_id=recipient_id,
            trigger_type=trigger_type,
            title=title,
            message=message,
            created_at=now,
        )

        self._notifications.append(record)
        logger.info(f"Notification sent [{trigger_type.value}] to learner '{recipient_id}' (id={nid}).")
        return record

    def get_learner_notifications(self, recipient_id: str) -> List[NotificationRecord]:
        return [n for n in self._notifications if n.recipient_id == recipient_id]
