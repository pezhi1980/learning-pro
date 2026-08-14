# backend/audio/__init__.py
"""
ROLE: AUDIO, LISTENING & TTS PACKAGE

Provides complete Listening & Audio infrastructure:
- Provider-independent TTS Abstraction (Mock & OpenAI)
- SHA-256 Deterministic Audio Cache Manager
- Audio Asset Repository with Content Version Linkage
- Listening Playback Sessions (transcript reveal, state management)
- Listening Exercise Evaluation Service
"""

from .audio_models import (
    AudioType,
    PlaybackState,
    AudioStatus,
    TTSRequest,
    TTSResponse,
    AudioAsset,
    ListeningPlaybackSession,
    ListeningEvaluationResult,
)
from .tts_interface import TTSProviderInterface
from .tts_providers import MockTTSProvider, OpenAITTSProvider, TTSProviderFactory
from .audio_cache_manager import AudioCacheManager
from .audio_asset_repository import AudioAssetRepository
from .listening_service import ListeningService

__all__ = [
    "AudioType",
    "PlaybackState",
    "AudioStatus",
    "TTSRequest",
    "TTSResponse",
    "AudioAsset",
    "ListeningPlaybackSession",
    "ListeningEvaluationResult",
    "TTSProviderInterface",
    "MockTTSProvider",
    "OpenAITTSProvider",
    "TTSProviderFactory",
    "AudioCacheManager",
    "AudioAssetRepository",
    "ListeningService",
]
