# backend/main.py

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ Learning Lang Pro Backend started")
    yield
    print("Backend shutting down")

app = FastAPI(
    title="Learning Lang Pro API",
    description="Backend API for Learning Lang Pro — AI-powered language learning",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten in production with your Flutter web domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
