# backend/audio/audio_cache_manager.py
"""
ROLE: DETERMINISTIC AUDIO CACHE MANAGER

Manages audio caching based on SHA-256 cache identity keys.
Prevents regenerating identical valid audio unnecessarily.
Supports cache invalidation when content version changes.
"""

import hashlib
import logging
from typing import Any, Dict, Optional, Tuple
from backend.audio.audio_models import AudioAsset, TTSRequest

logger = logging.getLogger(__name__)


class AudioCacheManager:
    """
    Manages deterministic audio caching and content version linkage.
    """

    def __init__(self):
        self._cache: Dict[str, Tuple[AudioAsset, bytes]] = {}

    @staticmethod
    def compute_cache_key(request: TTSRequest, provider_name: str) -> str:
        """
        Computes SHA-256 deterministic cache identity:
        sha256(text + voice + speed + language + source_content_version + provider)
        """
        text = (request.text or "").strip().lower()
        voice = (request.voice or "alloy").strip().lower()
        speed = str(round(request.speed, 2))
        lang = (request.language or "en").strip().lower()
        version = (request.source_content_version or "v1").strip()
        provider = provider_name.strip().lower()

        raw_str = f"{text}|{voice}|{speed}|{lang}|{version}|{provider}"
        return hashlib.sha256(raw_str.encode("utf-8")).hexdigest()

    def get_cached_audio(self, cache_key: str) -> Optional[Tuple[AudioAsset, bytes]]:
        """
        Retrieves cached AudioAsset and audio bytes if present.
        """
        if cache_key in self._cache:
            asset, audio_bytes = self._cache[cache_key]
            logger.info(f"Audio cache HIT for key: {cache_key[:12]}...")
            return asset, audio_bytes
        return None

    def store_cached_audio(self, asset: AudioAsset, audio_bytes: bytes) -> None:
        """
        Stores AudioAsset and audio bytes in cache.
        """
        self._cache[asset.cache_key] = (asset, audio_bytes)
        logger.info(f"Stored audio in cache for key: {asset.cache_key[:12]}...")

    def invalidate_by_version(self, source_content_version: str) -> int:
        """
        Invalidates cached items matching a specific source_content_version.
        """
        keys_to_delete = [
            k for k, (asset, _) in self._cache.items()
            if asset.source_content_version == source_content_version
        ]
        for k in keys_to_delete:
            del self._cache[k]
        return len(keys_to_delete)

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Returns cache statistics.
        """
        total_cached = len(self._cache)
        total_size_bytes = sum(len(audio) for _, audio in self._cache.values())
        return {
            "total_items": total_cached,
            "total_size_bytes": total_size_bytes,
        }
