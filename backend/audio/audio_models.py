# backend/audio/audio_models.py
"""
ROLE: AUDIO & TTS DATA MODELS

Defines structured data models for:
- TTS Request & Response payloads
- Audio Asset metadata and version linkage
- Listening Playback Sessions, Playback States, and Transcript Reveal logic
- Listening Exercise Evaluation Results
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AudioType(str, Enum):
    vocabulary = "vocabulary"
    chunk = "chunk"
    sentence = "sentence"
    example = "example"
    listening_exercise = "listening_exercise"


class PlaybackState(str, Enum):
    idle = "idle"
    loading = "loading"
    playing = "playing"
    paused = "paused"
    completed = "completed"
    error = "error"


class AudioStatus(str, Enum):
    cached = "cached"
    generating = "generating"
    failed = "failed"


class TTSRequest(BaseModel):
    text: str
    voice: str = "alloy"
    language: str = "en"
    speed: float = 1.0
    output_format: str = "mp3"
    audio_type: AudioType = AudioType.sentence
    linked_target_id: Optional[str] = None
    source_content_version: Optional[str] = None


class TTSResponse(BaseModel):
    audio_bytes: bytes
    duration_seconds: float
    provider_name: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AudioAsset(BaseModel):
    asset_id: str
    source_content: str
    source_content_version: str
    voice: str
    provider: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    duration_seconds: float
    storage_reference: str
    cache_key: str
    status: AudioStatus = AudioStatus.cached
    linked_target_id: Optional[str] = None
    audio_type: AudioType = AudioType.sentence


class ListeningPlaybackSession(BaseModel):
    session_id: str
    learner_id: str
    asset_id: str
    playback_state: PlaybackState = PlaybackState.idle
    current_position_seconds: float = 0.0
    replay_count: int = 0
    is_transcript_revealed: bool = False
    transcript_text: str = ""
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ListeningEvaluationResult(BaseModel):
    learner_id: str
    listening_target_id: str
    learner_answer: str
    target_transcript: str
    is_correct: bool
    similarity_score: float
