# backend/audio/tts_providers.py
"""
ROLE: TTS PROVIDER IMPLEMENTATIONS & FACTORY

Implements:
- MockTTSProvider for deterministic, zero-cost unit testing and local development.
- OpenAITTSProvider for optional live OpenAI Speech API calls.
- TTSProviderFactory for dynamic provider instantiation.
"""

import os
import logging
from typing import Optional
from backend.audio.audio_models import TTSRequest, TTSResponse
from backend.audio.tts_interface import TTSProviderInterface

logger = logging.getLogger(__name__)


class MockTTSProvider(TTSProviderInterface):
    """
    Deterministic Mock TTS Provider for unit testing and offline development.
    Generates synthetic audio bytes and estimated durations without network calls.
    """

    @property
    def provider_name(self) -> str:
        return "mock_tts"

    def generate_speech(self, request: TTSRequest) -> TTSResponse:
        text = request.text or ""
        word_count = len(text.split())
        estimated_duration = max(0.5, round(word_count * 0.4 / max(0.1, request.speed), 2))

        fake_audio_bytes = f"RIFF_MOCK_AUDIO_DATA:[text='{text}',voice='{request.voice}',speed={request.speed}]".encode("utf-8")

        return TTSResponse(
            audio_bytes=fake_audio_bytes,
            duration_seconds=estimated_duration,
            provider_name=self.provider_name,
            metadata={
                "voice": request.voice,
                "speed": request.speed,
                "word_count": word_count,
                "synthetic": True,
            },
        )


class OpenAITTSProvider(TTSProviderInterface):
    """
    Live OpenAI Text-to-Speech provider.
    Falls back to MockTTSProvider if OPENAI_API_KEY is not configured.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.mock_fallback = MockTTSProvider()

    @property
    def provider_name(self) -> str:
        return "openai_tts"

    def generate_speech(self, request: TTSRequest) -> TTSResponse:
        if not self.api_key or "sk-proj-mock" in self.api_key or not self.api_key.startswith("sk-"):
            logger.info("OpenAI API key missing or invalid; falling back to MockTTSProvider.")
            return self.mock_fallback.generate_speech(request)

        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            voice_map = {"alloy": "alloy", "echo": "echo", "fable": "fable", "onyx": "onyx", "nova": "nova", "shimmer": "shimmer"}
            voice = voice_map.get(request.voice.lower(), "alloy")

            response = client.audio.speech.create(
                model="tts-1",
                voice=voice,
                input=request.text,
                speed=request.speed,
            )
            audio_bytes = response.content
            estimated_duration = max(0.5, round(len(request.text.split()) * 0.4 / request.speed, 2))

            return TTSResponse(
                audio_bytes=audio_bytes,
                duration_seconds=estimated_duration,
                provider_name=self.provider_name,
                metadata={"voice": voice, "model": "tts-1"},
            )
        except Exception as e:
            logger.warning(f"OpenAI TTS API call failed: {e}. Falling back to MockTTSProvider.")
            return self.mock_fallback.generate_speech(request)


class TTSProviderFactory:
    """
    Factory for selecting and instantiating TTS providers.
    """

    @staticmethod
    def get_provider(provider_name: Optional[str] = None) -> TTSProviderInterface:
        name = (provider_name or os.getenv("TTS_PROVIDER", "mock")).lower()
        if name in ("openai", "openai_tts"):
            return OpenAITTSProvider()
        return MockTTSProvider()
