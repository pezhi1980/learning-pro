# backend/routers/admin_audit_router.py
"""
ROLE: ADMIN, AUDIT & TRACEABILITY REST API ROUTER

Exposes FastAPI REST endpoints for:
- Admin content and curriculum inspection
- Generation trace querying
- Admin control actions (publish, unpublish, deprecate, disable)
- Audit log querying
- System versioning manifest inspection
"""

import logging
import os
from typing import Any, Dict, List, Optional
try:
    from fastapi import APIRouter, Header, HTTPException
except ImportError:
    class APIRouter:
        def __init__(self, *args, **kwargs): pass
        def get(self, *args, **kwargs): return lambda f: f
        def post(self, *args, **kwargs): return lambda f: f
    class Header:
        def __init__(self, default=...): self.default = default
    class HTTPException(Exception):
        def __init__(self, status_code: int, detail: str):
            self.status_code = status_code
            self.detail = detail
from pydantic import BaseModel


from backend.audit import (
    AdminControlAction,
    AdminControlService,
    AdminInspectionService,
    AuditEventType,
    AuditLogger,
    GenerationTraceEngine,
    SystemVersioningManager,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/admin-audit", tags=["Admin, Audit & Complete Traceability"])

versioning_manager = SystemVersioningManager()
trace_engine = GenerationTraceEngine(versioning_manager=versioning_manager)
audit_logger = AuditLogger()
inspection_service = AdminInspectionService(trace_engine=trace_engine)
control_service = AdminControlService(audit_logger=audit_logger)


def verify_admin_key(x_admin_key: str = Header(...)):
    expected = os.getenv("ADMIN_SECRET_KEY", "secret_admin_key_123")
    if not expected or x_admin_key != expected:
        raise HTTPException(status_code=401, detail="Unauthorized admin key.")


class AdminActionRequest(BaseModel):
    action: AdminControlAction
    content_id: str
    version_hash: Optional[str] = None


@router.get("/inspect/content/{content_id}")
async def inspect_content(content_id: str, x_admin_key: str = Header(...)):
    verify_admin_key(x_admin_key)
    try:
        return inspection_service.inspect_content_details(content_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/inspect/trace/{request_id}")
async def inspect_trace(request_id: str, x_admin_key: str = Header(...)):
    verify_admin_key(x_admin_key)
    try:
        return inspection_service.inspect_generation_trace(request_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/control/action")
async def execute_admin_control_action(
    req: AdminActionRequest,
    x_admin_key: str = Header(...),
    x_admin_id: str = Header("admin_user_01"),
):
    verify_admin_key(x_admin_key)
    try:
        return control_service.execute_admin_action(
            admin_id=x_admin_id,
            action=req.action,
            content_id=req.content_id,
            version_hash=req.version_hash,
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/logs")
async def get_audit_logs(
    event_type: Optional[AuditEventType] = None,
    limit: int = 50,
    x_admin_key: str = Header(...),
):
    verify_admin_key(x_admin_key)
    return audit_logger.get_logs(event_type=event_type, limit=limit)


@router.get("/versioning/manifest")
async def get_system_versioning_manifest(x_admin_key: str = Header(...)):
    verify_admin_key(x_admin_key)
    return versioning_manager.get_active_manifest()
