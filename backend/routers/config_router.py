# backend/routers/config_router.py

from fastapi import APIRouter, HTTPException, Header
from typing import Optional, Dict, Any
from ..config import get_app_config, FeatureFlagService, MigrationEngine, ContentMigrationTool

router = APIRouter(prefix="/api/config", tags=["config"])

_config = get_app_config()
_feature_flags = FeatureFlagService()
_migration_engine = MigrationEngine()
_content_migration_tool = ContentMigrationTool()


@router.get("/info")
def get_system_config_info():
    return {
        "environment": _config.environment,
        "app_version": _config.app_version,
        "api_version": _config.api_version,
        "schema_version": _config.schema_version,
        "content_version": _config.content_version,
        "is_production": _config.is_production,
    }


@router.get("/feature-flags")
def get_feature_flags():
    return _feature_flags.get_all_flags()


@router.post("/migrations/apply")
def apply_database_migrations(x_admin_key: Optional[str] = Header(None)):
    if x_admin_key != "secret_admin_key_123":
        raise HTTPException(status_code=403, detail="Admin authorization required for migrations.")

    res = _migration_engine.apply_pending_migrations()
    return res
