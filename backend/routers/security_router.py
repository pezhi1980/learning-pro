# backend/routers/security_router.py
"""
ROLE: SECURITY, PRIVACY & DATA GOVERNANCE REST API ROUTER

Exposes FastAPI REST endpoints for:
- Account deletion (GDPR Right to Erasure, preserving global Curriculum)
- Data retention cleanup scheduling
- Privacy settings & consent preferences management
"""

import logging
from typing import Any, Dict, Optional
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from backend.security import (
    AccessControlContext,
    AccountDeletionService,
    AuthorizationService,
    DataRetentionManager,
    PrivacyManager,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/security", tags=["Security, Privacy & Data Governance"])

authz_service = AuthorizationService()
account_deletion_service = AccountDeletionService()
retention_manager = DataRetentionManager()
privacy_manager = PrivacyManager()


class DeleteAccountRequest(BaseModel):
    learner_id: str


class PrivacyPreferencesRequest(BaseModel):
    learner_id: str
    allow_voice_retention: bool = True
    allow_writing_retention: bool = True
    allow_analytics: bool = True


@router.post("/account/delete")
async def delete_learner_account(
    req: DeleteAccountRequest,
    x_requester_id: str = Header("user_default_01"),
    x_is_admin: bool = Header(False),
):
    ctx = AccessControlContext(requester_id=x_requester_id, is_admin=x_is_admin)
    try:
        authz_service.authorize_resource_access(ctx, resource_owner_id=req.learner_id, resource_type="account")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return account_deletion_service.delete_learner_account(req.learner_id)


@router.post("/retention/cleanup")
async def trigger_retention_cleanup(x_is_admin: bool = Header(False)):
    if not x_is_admin:
        raise HTTPException(status_code=403, detail="Only admins may trigger retention policy cleanup.")
    return retention_manager.execute_retention_cleanup()


@router.get("/privacy/settings/{learner_id}")
async def get_privacy_settings(
    learner_id: str,
    x_requester_id: str = Header("user_default_01"),
    x_is_admin: bool = Header(False),
):
    ctx = AccessControlContext(requester_id=x_requester_id, is_admin=x_is_admin)
    try:
        authz_service.authorize_resource_access(ctx, resource_owner_id=learner_id, resource_type="privacy_settings")
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))

    return privacy_manager.get_learner_privacy_settings(learner_id)
