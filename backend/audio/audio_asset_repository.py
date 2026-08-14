# backend/audio/audio_asset_repository.py
"""
ROLE: AUDIO ASSET REPOSITORY

Tracks audio asset metadata records and content linkages:
- asset_id
- source_content
- source_content_version
- voice
- provider
- duration
- storage_reference
- cache_key
- status
- linked_target_id
"""

from typing import Dict, List, Optional
from backend.audio.audio_models import AudioAsset


class AudioAssetRepository:
    """
    Repository maintaining audio asset records and target linkages.
    """

    def __init__(self):
        self._assets: Dict[str, AudioAsset] = {}
        self._assets_by_target: Dict[str, List[AudioAsset]] = {}

    def save_asset(self, asset: AudioAsset) -> None:
        """
        Saves or updates an AudioAsset record.
        """
        self._assets[asset.asset_id] = asset

        if asset.linked_target_id:
            if asset.linked_target_id not in self._assets_by_target:
                self._assets_by_target[asset.linked_target_id] = []
            if asset not in self._assets_by_target[asset.linked_target_id]:
                self._assets_by_target[asset.linked_target_id].append(asset)

    def get_asset(self, asset_id: str) -> Optional[AudioAsset]:
        return self._assets.get(asset_id)

    def get_assets_by_target(self, target_id: str) -> List[AudioAsset]:
        return self._assets_by_target.get(target_id, [])

    def list_assets(self, limit: int = 50, offset: int = 0) -> List[AudioAsset]:
        all_items = list(self._assets.values())
        return all_items[offset : offset + limit]
