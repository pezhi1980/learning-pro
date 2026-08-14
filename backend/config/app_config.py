# backend/config/app_config.py

import os
from typing import Optional
from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    environment: str = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development"))
    backend_url: str = Field(default_factory=lambda: os.getenv("BACKEND_URL", "http://localhost:8000"))
    db_connection_url: str = Field(default_factory=lambda: os.getenv("DATABASE_URL", "sqlite:///./app.db"))
    app_version: str = "1.0.0"
    api_version: str = "v1"
    schema_version: str = "1.0.0"
    content_version: str = "1.0.0"
    debug: bool = Field(default_factory=lambda: os.getenv("ENVIRONMENT", "development") in ["development", "test"])
    max_request_body_bytes: int = 10 * 1024 * 1024  # 10 MB

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"

    @property
    def is_staging(self) -> bool:
        return self.environment.lower() == "staging"

    @property
    def is_test(self) -> bool:
        return self.environment.lower() == "test"


_config_instance: Optional[AppConfig] = None


def get_app_config() -> AppConfig:
    global _config_instance
    if _config_instance is None:
        _config_instance = AppConfig()
    return _config_instance
