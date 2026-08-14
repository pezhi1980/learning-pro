# backend/speaking/speech_interface.py
"""
ROLE: SPEECH RECOGNITION INTERFACE

Defines abstract provider-independent Speech-to-Text interface.
Decouples application speaking logic from specific STT vendors (Whisper, Mock STT, etc.).
"""

from abc import ABC, abstractmethod
from typing import Optional
from backend.speaking.speaking_models import SpeechAudioInput, SpeechTranscriptionResult


class SpeechRecognizerInterface(ABC):
    """
    Abstract interface for Speech-to-Text (STT) transcription providers.
    """

    @abstractmethod
    def transcribe(
        self, audio_input: SpeechAudioInput, target_text_hint: Optional[str] = None
    ) -> SpeechTranscriptionResult:
        """
        Transcribes audio input into text and confidence metrics.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Returns provider identifier name.
        """
        pass
