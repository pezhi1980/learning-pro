# backend/routers/operations_router.py

from fastapi import APIRouter, HTTPException, Depends, Header
from typing import Optional, Dict, Any
from ..operations import (
    HealthChecker,
    MetricsMonitor,
    AlertingEngine,
    BackupManager,
    RestoreService,
    StructuredLogger,
)
from ..curriculum.curriculum_service import CurriculumService

router = APIRouter(prefix="/api/operations", tags=["operations"])

_curriculum_service = CurriculumService()

_health_checker = HealthChecker(curriculum_service=_curriculum_service)
_metrics_monitor = MetricsMonitor()
_alerting_engine = AlertingEngine()
_backup_manager = BackupManager()
_restore_service = RestoreService(_backup_manager)
_logger = StructuredLogger()


@router.get("/health")
def get_health_status():
    report = _health_checker.check_health()
    _logger.log_operation(
        request_id="req_health_check",
        operation="health_check",
        status="SUCCESS",
        message=f"Health status: {report.status}",
    )
    return report.model_dump()


@router.get("/metrics")
def get_metrics_summary():
    summary = _metrics_monitor.get_metrics_summary()
    return summary


@router.get("/alerts")
def get_active_alerts():
    metrics = _metrics_monitor.get_metrics_summary()
    triggered = _alerting_engine.evaluate_metrics(metrics)
    return [a.model_dump() for a in _alerting_engine.active_alerts]


@router.post("/backup")
def create_system_backup(payload: Dict[str, Any], x_admin_key: Optional[str] = Header(None)):
    if x_admin_key != "secret_admin_key_123":
        raise HTTPException(status_code=403, detail="Admin authorization required for backup.")

    archive = _backup_manager.create_backup(payload)
    _logger.log_operation(
        request_id=f"req_backup_{archive.archive_id}",
        operation="create_backup",
        status="SUCCESS",
        message=f"Backup archive created: {archive.archive_id}",
    )
    return archive.model_dump()


@router.post("/restore")
def restore_system_backup(archive_data: Dict[str, Any], x_admin_key: Optional[str] = Header(None)):
    if x_admin_key != "secret_admin_key_123":
        raise HTTPException(status_code=403, detail="Admin authorization required for restore.")

    try:
        from ..operations import BackupArchive
        archive = BackupArchive(**archive_data)
        result = _restore_service.verify_and_restore(archive)
        if not result.success:
            raise HTTPException(status_code=400, detail=f"Restore failed: {', '.join(result.errors)}")
        return result.model_dump()

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid backup payload: {str(e)}")
