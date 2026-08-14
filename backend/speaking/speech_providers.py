# backend/speaking/speech_providers.py
"""
ROLE: SPEECH RECOGNITION PROVIDER IMPLEMENTATIONS & FACTORY

Implements:
- MockSpeechRecognizer for deterministic, zero-cost unit testing & offline dev.
- WhisperSpeechRecognizer for live OpenAI Whisper STT API integration.
- SpeechRecognizerFactory for dynamic provider selection.
"""

import os
import base64
import logging
from typing import Optional
from backend.speaking.speaking_models import SpeechAudioInput, SpeechTranscriptionResult
from backend.speaking.speech_interface import SpeechRecognizerInterface

logger = logging.getLogger(__name__)


class MockSpeechRecognizer(SpeechRecognizerInterface):
    """
    Deterministic Mock Speech Recognizer for unit testing and offline development.
    Extracts embedded mock strings from base64 audio payload or target hint.
    """

    @property
    def provider_name(self) -> str:
        return "mock_stt"

    def transcribe(
        self, audio_input: SpeechAudioInput, target_text_hint: Optional[str] = None
    ) -> SpeechTranscriptionResult:
        decoded_text = ""
        try:
            raw_bytes = base64.b64decode(audio_input.audio_base64)
            raw_str = raw_bytes.decode("utf-8", errors="ignore")
            if "MOCK_AUDIO_DATA:[text='" in raw_str:
                decoded_text = raw_str.split("MOCK_AUDIO_DATA:[text='")[1].split("'")[0]
        except Exception:
            pass

        if not decoded_text:
            decoded_text = target_text_hint or "Synthetic spoken audio text."

        return SpeechTranscriptionResult(
            transcript=decoded_text,
            transcription_confidence=0.92,
            provider_name=self.provider_name,
            status="success",
            metadata={"simulated": True, "language": audio_input.language},
        )


class WhisperSpeechRecognizer(SpeechRecognizerInterface):
    """
    Live OpenAI Whisper Speech Recognition provider.
    Falls back to MockSpeechRecognizer if OPENAI_API_KEY is absent.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.mock_fallback = MockSpeechRecognizer()

    @property
    def provider_name(self) -> str:
        return "whisper_stt"

    def transcribe(
        self, audio_input: SpeechAudioInput, target_text_hint: Optional[str] = None
    ) -> SpeechTranscriptionResult:
        if not self.api_key or "sk-proj-mock" in self.api_key or not self.api_key.startswith("sk-"):
            logger.info("OpenAI API key missing or invalid; falling back to MockSpeechRecognizer.")
            return self.mock_fallback.transcribe(audio_input, target_text_hint=target_text_hint)

        try:
            from openai import OpenAI
            import tempfile

            client = OpenAI(api_key=self.api_key)
            audio_bytes = base64.b64decode(audio_input.audio_base64)

            with tempfile.NamedTemporaryFile(suffix=f".{audio_input.audio_format}", delete=False) as tmp:
                tmp.write(audio_bytes)
                tmp_path = tmp.name

            try:
                with open(tmp_path, "rb") as audio_file:
                    res = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=audio_input.language,
                        prompt=target_text_hint,
                    )
                return SpeechTranscriptionResult(
                    transcript=res.text,
                    transcription_confidence=0.90,
                    provider_name=self.provider_name,
                    status="success",
                    metadata={"model": "whisper-1"},
                )
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        except Exception as e:
            logger.warning(f"Whisper STT API call failed: {e}. Falling back to MockSpeechRecognizer.")
            return self.mock_fallback.transcribe(audio_input, target_text_hint=target_text_hint)


class SpeechRecognizerFactory:
    """
    Factory for instantiating speech recognizer providers.
    """

    @staticmethod
    def get_recognizer(provider_name: Optional[str] = None) -> SpeechRecognizerInterface:
        name = (provider_name or os.getenv("STT_PROVIDER", "mock")).lower()
        if name in ("whisper", "whisper_stt", "openai"):
            return WhisperSpeechRecognizer()
        return MockSpeechRecognizer()
