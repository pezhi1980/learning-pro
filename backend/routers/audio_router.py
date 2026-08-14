# backend/routers/audio_router.py
"""
ROLE: AUDIO & LISTENING REST API ROUTER

Exposes FastAPI REST endpoints for:
- TTS Audio Generation & Cache Lookup
- Audio Asset Retrieval
- Listening Session Playback Control & Transcript Reveal
- Listening Exercise Evaluation
- Audio Cache Statistics
"""

import base64
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.audio import (
    AudioAsset,
    ListeningEvaluationResult,
    ListeningPlaybackSession,
    ListeningService,
    PlaybackState,
    TTSRequest,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/audio", tags=["Listening & Audio"])

listening_service = ListeningService()


class TTSGenerateResponse(BaseModel):
    asset: AudioAsset
    audio_base64: str


class CreatePlaybackSessionRequest(BaseModel):
    learner_id: str
    asset_id: str
    transcript_text: str = ""


class UpdatePlaybackStateRequest(BaseModel):
    playback_state: PlaybackState
    current_position_seconds: float = 0.0


class EvaluateListeningRequest(BaseModel):
    learner_id: str
    listening_target_id: str
    learner_answer: str
    target_transcript: str


@router.post("/tts/generate", response_model=TTSGenerateResponse)
async def generate_or_get_tts(req: TTSRequest, provider_override: Optional[str] = None):
    try:
        asset, audio_bytes = listening_service.get_or_generate_audio(req, provider_override=provider_override)
        audio_b64 = base64.b64encode(audio_bytes).decode("utf-8")
        return TTSGenerateResponse(asset=asset, audio_base64=audio_b64)
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=400, detail=f"TTS generation error: {str(e)}")


@router.get("/asset/{asset_id}", response_model=AudioAsset)
async def get_audio_asset(asset_id: str):
    asset = listening_service.repository.get_asset(asset_id)
    if not asset:
        raise HTTPException(status_code=404, detail=f"Audio asset '{asset_id}' not found.")
    return asset


@router.post("/listening/session/create", response_model=ListeningPlaybackSession)
async def create_playback_session(req: CreatePlaybackSessionRequest):
    return listening_service.create_playback_session(
        learner_id=req.learner_id,
        asset_id=req.asset_id,
        transcript_text=req.transcript_text,
    )


@router.post("/listening/session/{session_id}/state", response_model=ListeningPlaybackSession)
async def update_playback_state(session_id: str, req: UpdatePlaybackStateRequest):
    try:
        return listening_service.update_playback_state(
            session_id=session_id,
            state=req.playback_state,
            current_position_seconds=req.current_position_seconds,
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/listening/session/{session_id}/transcript_reveal", response_model=ListeningPlaybackSession)
async def reveal_transcript(session_id: str):
    try:
        return listening_service.reveal_transcript(session_id)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/listening/evaluate", response_model=ListeningEvaluationResult)
async def evaluate_listening_exercise(req: EvaluateListeningRequest):
    return listening_service.evaluate_listening_exercise(
        learner_id=req.learner_id,
        listening_target_id=req.listening_target_id,
        learner_answer=req.learner_answer,
        target_transcript=req.target_transcript,
    )


@router.get("/cache/stats", response_model=Dict[str, Any])
async def get_cache_stats():
    return listening_service.cache_manager.get_cache_stats()
