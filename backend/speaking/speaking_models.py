# backend/speaking/speaking_models.py
"""
ROLE: SPEAKING & PRONUNCIATION DATA MODELS

Defines structured data models for:
- Speech Recognition input & transcription results
- Pronunciation attempts and word-level feedback
- 5 Speaking Practice modes (read_aloud, controlled_answer, sentence_production, guided_response, controlled_dialogue)
- 3-Way Evaluation separation (Transcription Confidence, Linguistic Correctness, Pronunciation Quality)
- Voice Attempt records and Learner Privacy metadata
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SpeakingMode(str, Enum):
    read_aloud = "read_aloud"
    controlled_answer = "controlled_answer"
    sentence_production = "sentence_production"
    guided_response = "guided_response"
    controlled_dialogue = "controlled_dialogue"


class TargetLevel(str, Enum):
    word = "word"
    chunk = "chunk"
    sentence = "sentence"


class SpeechAudioInput(BaseModel):
    audio_base64: str
    audio_format: str = "wav"
    sample_rate: int = 16000
    language: str = "en"


class SpeechTranscriptionResult(BaseModel):
    transcript: str
    transcription_confidence: float
    provider_name: str
    status: str = "success"
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VoiceAttemptRecord(BaseModel):
    attempt_id: str
    learner_id: str
    target_text: str
    target_type: TargetLevel = TargetLevel.sentence
    linked_target_id: Optional[str] = None
    audio_storage_reference: str
    transcription: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_deleted: bool = False


class PronunciationResult(BaseModel):
    attempt_id: str
    learner_id: str
    target_text: str
    transcription: str
    transcription_confidence: float
    linguistic_correctness_score: float
    pronunciation_quality_score: float
    overall_score: float
    word_level_feedback: List[Dict[str, Any]] = Field(default_factory=list)
    feedback_text: str


class SpeakingEvaluationResult(BaseModel):
    evaluation_id: str
    learner_id: str
    mode: SpeakingMode
    prompt: str
    expected_text_or_patterns: List[str] = Field(default_factory=list)
    transcription: str
    transcription_confidence: float
    linguistic_correctness_score: float
    pronunciation_quality_score: float
    is_passed: bool
    feedback: str
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
