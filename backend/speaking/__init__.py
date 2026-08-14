# backend/speaking/__init__.py
"""
ROLE: SPEAKING, STT & PRONUNCIATION PACKAGE

Provides complete Speaking System infrastructure:
- Provider-independent Speech Recognition Abstraction (Mock & Whisper)
- Pronunciation Practice & Feedback for words, chunks, and sentences
- 5 Speaking Practice Modes (Read Aloud, Controlled Answer, Sentence Production, Guided Response, Dialogue)
- 3-Way Evaluation Separation (STT Confidence, Linguistic Correctness, Pronunciation Quality)
- Voice Attempt Storage & Learner Privacy Data Deletion Engine
"""

from .speaking_models import (
    SpeakingMode,
    TargetLevel,
    SpeechAudioInput,
    SpeechTranscriptionResult,
    VoiceAttemptRecord,
    PronunciationResult,
    SpeakingEvaluationResult,
)
from .speech_interface import SpeechRecognizerInterface
from .speech_providers import MockSpeechRecognizer, WhisperSpeechRecognizer, SpeechRecognizerFactory
from .voice_attempt_repository import VoiceAttemptRepository
from .voice_privacy_manager import VoicePrivacyManager
from .speaking_evaluator import SpeakingEvaluator
from .speaking_service import SpeakingService

__all__ = [
    "SpeakingMode",
    "TargetLevel",
    "SpeechAudioInput",
    "SpeechTranscriptionResult",
    "VoiceAttemptRecord",
    "PronunciationResult",
    "SpeakingEvaluationResult",
    "SpeechRecognizerInterface",
    "MockSpeechRecognizer",
    "WhisperSpeechRecognizer",
    "SpeechRecognizerFactory",
    "VoiceAttemptRepository",
    "VoicePrivacyManager",
    "SpeakingEvaluator",
    "SpeakingService",
]
