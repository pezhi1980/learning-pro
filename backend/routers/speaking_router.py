# backend/routers/speaking_router.py
"""
ROLE: SPEAKING & PRONUNCIATION REST API ROUTER

Exposes FastAPI REST endpoints for:
- Pronunciation evaluation (word/chunk/sentence)
- Speaking practice evaluation across 5 modes
- STT audio transcription
- Learner voice privacy data purge and policy summary
"""

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.speaking import (
    PronunciationResult,
    SpeakingEvaluationResult,
    SpeakingMode,
    SpeakingService,
    SpeechAudioInput,
    SpeechTranscriptionResult,
    TargetLevel,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/speaking", tags=["Speaking & Pronunciation"])

speaking_service = SpeakingService()


class PronunciationRequest(BaseModel):
    learner_id: str
    target_text: str
    audio_input: SpeechAudioInput
    target_level: TargetLevel = TargetLevel.sentence
    linked_target_id: Optional[str] = None


class SpeakingPracticeRequest(BaseModel):
    learner_id: str
    mode: SpeakingMode
    prompt: str
    audio_input: SpeechAudioInput
    expected_text_or_patterns: List[str]
    linked_target_id: Optional[str] = None


class TranscribeRequest(BaseModel):
    audio_input: SpeechAudioInput
    target_hint: Optional[str] = None


@router.post("/pronunciation/evaluate", response_model=PronunciationResult)
async def evaluate_pronunciation(req: PronunciationRequest):
    try:
        return speaking_service.record_and_evaluate_pronunciation(
            learner_id=req.learner_id,
            target_text=req.target_text,
            audio_input=req.audio_input,
            target_level=req.target_level,
            linked_target_id=req.linked_target_id,
        )
    except Exception as e:
        logger.error(f"Pronunciation evaluation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/practice/evaluate", response_model=SpeakingEvaluationResult)
async def evaluate_speaking_practice(req: SpeakingPracticeRequest):
    try:
        return speaking_service.evaluate_speaking_practice(
            learner_id=req.learner_id,
            mode=req.mode,
            prompt=req.prompt,
            audio_input=req.audio_input,
            expected_text_or_patterns=req.expected_text_or_patterns,
            linked_target_id=req.linked_target_id,
        )
    except Exception as e:
        logger.error(f"Speaking practice evaluation failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/transcribe", response_model=SpeechTranscriptionResult)
async def transcribe_audio(req: TranscribeRequest):
    return speaking_service.transcribe_audio(req.audio_input, target_hint=req.target_hint)


@router.delete("/privacy/learner/{learner_id}", response_model=Dict[str, Any])
async def purge_learner_voice_data(learner_id: str):
    return speaking_service.purge_learner_voice_privacy_data(learner_id)


@router.get("/privacy/policy", response_model=Dict[str, Any])
async def get_privacy_policy():
    return speaking_service.privacy_manager.get_privacy_policy_summary()
