# backend/lifecycle/content_cache_manager.py
"""
ROLE: CONTENT CACHE MANAGER

Manages deterministic caching for reusable validated & published content.
Cache keys incorporate target IDs, generation mode, CEFR level, content version hash, and constraints.
Prevents duplicate AI content generation.
"""

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional
from backend.lifecycle.lifecycle_models import ContentVersionRecord, PublishingStatus

logger = logging.getLogger(__name__)


class ContentCacheManager:
    """
    Manages deterministic content caching for validated curriculum lessons and exercises.
    """

    def __init__(self):
        self._cache: Dict[str, ContentVersionRecord] = {}

    @staticmethod
    def compute_cache_key(
        target_ids: List[str],
        mode: str,
        cefr_level: str,
        content_version_hash: str,
        constraints: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Computes SHA-256 deterministic content cache key:
        sha256(target_ids + mode + level + content_version_hash + constraints)
        """
        sorted_targets = "|".join(sorted(target_ids))
        mode_str = mode.strip().lower()
        level_str = cefr_level.strip().upper()
        ver_str = content_version_hash.strip().lower()
        constraints_str = json.dumps(constraints or {}, sort_keys=True)

        raw = f"{sorted_targets}:{mode_str}:{level_str}:{ver_str}:{constraints_str}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def get_cached_content(self, cache_key: str) -> Optional[ContentVersionRecord]:
        """
        Retrieves cached content version record if present and eligible (published/validated).
        """
        record = self._cache.get(cache_key)
        if record:
            if record.publishing_status in (PublishingStatus.published, PublishingStatus.validated):
                logger.info(f"Content cache HIT for key: {cache_key[:12]}...")
                return record
            else:
                # Remove stale/rejected cached record
                del self._cache[cache_key]
        return None

    def store_cached_content(self, cache_key: str, record: ContentVersionRecord) -> None:
        """
        Caches a validated or published ContentVersionRecord.
        """
        if record.publishing_status in (PublishingStatus.published, PublishingStatus.validated):
            self._cache[cache_key] = record
            logger.info(f"Stored content in cache for key: {cache_key[:12]}...")

    def invalidate_cache(self, version_hash: Optional[str] = None) -> int:
        """
        Invalidates cache items matching a version_hash or flushes entire cache.
        """
        if version_hash:
            keys_to_del = [k for k, v in self._cache.items() if v.content_version_hash == version_hash]
            for k in keys_to_del:
                del self._cache[k]
            return len(keys_to_del)
        else:
            count = len(self._cache)
            self._cache.clear()
            return count

    def get_cache_stats(self) -> Dict[str, Any]:
        return {"total_cached_items": len(self._cache)}
