# backend/audio/tts_interface.py
"""
ROLE: PROVIDER-INDEPENDENT TTS INTERFACE

Defines the abstract contract for Text-to-Speech providers.
Decouples application logic from specific TTS vendor implementations (OpenAI, Mock, etc.).
"""

from abc import ABC, abstractmethod
from backend.audio.audio_models import TTSRequest, TTSResponse


class TTSProviderInterface(ABC):
    """
    Abstract interface for Text-to-Speech generation providers.
    """

    @abstractmethod
    def generate_speech(self, request: TTSRequest) -> TTSResponse:
        """
        Generates audio content bytes and metadata for a TTSRequest.
        """
        pass

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """
        Returns the unique identifier string for the provider.
        """
        pass
