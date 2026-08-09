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

# ── Routers ─────────────────────────────────────────────────
app.include_router(admin_router)

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
