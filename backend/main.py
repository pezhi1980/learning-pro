# backend/main.py

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers.admin import router as admin_router

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("✅ Learning Lang Pro Backend started")
    yield
    logger.info("Backend shutting down")


app = FastAPI(
    title="Learning Lang Pro API",
    description="Backend API for Learning Lang Pro — AI-powered language learning",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from routers.admin import router as admin_router
from backend.routers.learning_router import router as learning_router
from backend.routers.course_router import router as course_router
from backend.routers.session_router import router as session_router
from backend.routers.assessment_router import router as assessment_router
from backend.routers.audio_router import router as audio_router
from backend.routers.speaking_router import router as speaking_router
from backend.routers.writing_router import router as writing_router
from backend.routers.intelligence_router import router as intelligence_router
from backend.routers.lifecycle_router import router as lifecycle_router
from backend.routers.admin_audit_router import router as admin_audit_router
from backend.routers.ai_ops_router import router as ai_ops_router
from backend.routers.security_router import router as security_router
from backend.routers.analytics_router import router as analytics_router
from backend.routers.engagement_router import router as engagement_router
from backend.routers.utilities_router import router as utilities_router
from backend.routers.operations_router import router as operations_router
from backend.routers.config_router import router as config_router

# ── Routers ─────────────────────────────────────────────────
app.include_router(admin_router)
app.include_router(learning_router)
app.include_router(course_router)
app.include_router(session_router)
app.include_router(assessment_router)
app.include_router(audio_router)
app.include_router(speaking_router)
app.include_router(writing_router)
app.include_router(intelligence_router)
app.include_router(lifecycle_router)
app.include_router(admin_audit_router)
app.include_router(ai_ops_router)
app.include_router(security_router)
app.include_router(analytics_router)
app.include_router(engagement_router)
app.include_router(utilities_router)
app.include_router(operations_router)
app.include_router(config_router)

















# ── Health Check ────────────────────────────────────────────
@app.get("/", tags=["Health"])
async def root():
    return {
        "status": "ok",
        "service": "Learning Lang Pro API",
        "version": "1.0.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
    }

@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy"}
