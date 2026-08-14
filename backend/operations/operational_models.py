# backend/operations/operational_models.py

import time
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ComponentHealth(BaseModel):
    name: str
    status: str  # HEALTHY, DEGRADED, UNHEALTHY
    message: str
    latency_ms: float = 0.0
    details: Dict[str, Any] = Field(default_factory=dict)


class HealthReport(BaseModel):
    status: str  # HEALTHY, DEGRADED, UNHEALTHY
    timestamp: float = Field(default_factory=time.time)
    checks: Dict[str, ComponentHealth] = Field(default_factory=dict)


class StructuredLogEntry(BaseModel):
    request_id: str
    service: str
    operation: str
    status: str  # SUCCESS, WARNING, ERROR
    error_code: Optional[str] = None
    message: str
    timestamp: float = Field(default_factory=time.time)
    safe_identifiers: Dict[str, str] = Field(default_factory=dict)


class SystemMetric(BaseModel):
    metric_name: str
    count: int = 0
    total_value: float = 0.0
    p95_latency_ms: float = 0.0
    labels: Dict[str, str] = Field(default_factory=dict)


class AlertNotification(BaseModel):
    alert_id: str
    alert_key: str
    severity: str  # INFO, WARNING, CRITICAL
    component: str
    message: str
    timestamp: float = Field(default_factory=time.time)
    throttled: bool = False


class BackupArchive(BaseModel):
    archive_id: str
    version: str = "1.0.0"
    created_at: float = Field(default_factory=time.time)
    record_counts: Dict[str, int] = Field(default_factory=dict)
    data: Dict[str, Any] = Field(default_factory=dict)
    checksum: str


class RestoreResult(BaseModel):
    success: bool
    archive_id: str
    restored_records: int = 0
    errors: List[str] = Field(default_factory=list)
    timestamp: float = Field(default_factory=time.time)
