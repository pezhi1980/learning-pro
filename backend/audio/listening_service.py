# backend/audio/listening_service.py
"""
ROLE: LISTENING SERVICE

Orchestrates:
- TTS Audio Generation & Cache Lookup (Zero duplicate generation)
- Audio Asset Management & Version Traceability
- Listening Session Playback State Transitions (idle -> loading -> playing -> paused -> completed)
- Transcript Reveal & Replay Controls
- Listening Exercise Evaluation
"""

import hashlib
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from backend.audio.audio_asset_repository import AudioAssetRepository
from backend.audio.audio_cache_manager import AudioCacheManager
from backend.audio.audio_models import (
    AudioAsset,
    AudioStatus,
    AudioType,
    ListeningEvaluationResult,
    ListeningPlaybackSession,
    PlaybackState,
    TTSRequest,
    TTSResponse,
)
from backend.audio.tts_interface import TTSProviderInterface
from backend.audio.tts_providers import TTSProviderFactory

logger = logging.getLogger(__name__)


class ListeningService:
    """
    Core Listening & Audio Service orchestrating TTS providers, audio cache, asset repository,
    playback session state, and listening exercise evaluations.
    """

    def __init__(
        self,
        provider: Optional[TTSProviderInterface] = None,
        cache_manager: Optional[AudioCacheManager] = None,
        repository: Optional[AudioAssetRepository] = None,
    ):
        self.provider = provider or TTSProviderFactory.get_provider()
        self.cache_manager = cache_manager or AudioCacheManager()
        self.repository = repository or AudioAssetRepository()
        self._playback_sessions: Dict[str, ListeningPlaybackSession] = {}

    def get_or_generate_audio(
        self, request: TTSRequest, provider_override: Optional[str] = None
    ) -> Tuple[AudioAsset, bytes]:
        """
        Retrieves cached audio or generates new speech via TTS provider.
        Prevents regenerating identical valid audio unnecessarily using deterministic cache key.
        """
        active_provider = (
            TTSProviderFactory.get_provider(provider_override)
            if provider_override
            else self.provider
        )
        provider_name = active_provider.provider_name

        version = request.source_content_version or hashlib.sha256(request.text.encode("utf-8")).hexdigest()[:12]
        request.source_content_version = version

        cache_key = self.cache_manager.compute_cache_key(request, provider_name)

        # 1. Check Audio Cache
        cached_result = self.cache_manager.get_cached_audio(cache_key)
        if cached_result:
            return cached_result

        # 2. Generate new audio via TTS Provider
        logger.info(f"Cache miss for '{request.text[:20]}...'. Generating audio via {provider_name}.")
        tts_response = active_provider.generate_speech(request)

        now = datetime.now(timezone.utc)
        asset_id = f"asset:{int(now.timestamp())}:{cache_key[:10]}"
        storage_ref = f"memory://audio/{cache_key}.{request.output_format}"

        asset = AudioAsset(
            asset_id=asset_id,
            source_content=request.text,
            source_content_version=version,
            voice=request.voice,
            provider=provider_name,
            created_at=now,
            duration_seconds=tts_response.duration_seconds,
            storage_reference=storage_ref,
            cache_key=cache_key,
            status=AudioStatus.cached,
            linked_target_id=request.linked_target_id,
            audio_type=request.audio_type,
        )

        # 3. Store in Cache and Repository
        self.cache_manager.store_cached_audio(asset, tts_response.audio_bytes)
        self.repository.save_asset(asset)

        return asset, tts_response.audio_bytes

    # ── Listening Session & Playback Control ───────────────────────────────

    def create_playback_session(
        self, learner_id: str, asset_id: str, transcript_text: str = ""
    ) -> ListeningPlaybackSession:
        """
        Creates a new listening playback session.
        Transcript is hidden by default (is_transcript_revealed = False).
        """
        now = datetime.now(timezone.utc)
        session_id = f"sess_listen:{learner_id}:{int(now.timestamp())}"
        session = ListeningPlaybackSession(
            session_id=session_id,
            learner_id=learner_id,
            asset_id=asset_id,
            playback_state=PlaybackState.idle,
            current_position_seconds=0.0,
            replay_count=0,
            is_transcript_revealed=False,
            transcript_text=transcript_text,
            last_updated=now,
        )
        self._playback_sessions[session_id] = session
        return session

    def get_playback_session(self, session_id: str) -> Optional[ListeningPlaybackSession]:
        return self._playback_sessions.get(session_id)

    def update_playback_state(
        self, session_id: str, state: PlaybackState, current_position_seconds: float = 0.0
    ) -> ListeningPlaybackSession:
        """
        Updates playback state (idle -> loading -> playing -> paused -> completed).
        Increments replay_count when replaying from start.
        """
        session = self.get_playback_session(session_id)
        if not session:
            raise KeyError(f"Playback session '{session_id}' not found.")

        now = datetime.now(timezone.utc)
        if state == PlaybackState.playing and current_position_seconds == 0.0 and session.playback_state in (PlaybackState.completed, PlaybackState.paused):
            session.replay_count += 1

        session.playback_state = state
        session.current_position_seconds = current_position_seconds
        session.last_updated = now
        return session

    def reveal_transcript(self, session_id: str) -> ListeningPlaybackSession:
        """
        Reveals transcript text for the listening session.
        """
        session = self.get_playback_session(session_id)
        if not session:
            raise KeyError(f"Playback session '{session_id}' not found.")

        session.is_transcript_revealed = True
        session.last_updated = datetime.now(timezone.utc)
        return session

    # ── Listening Exercise Evaluation ──────────────────────────────────────

    def evaluate_listening_exercise(
        self,
        learner_id: str,
        listening_target_id: str,
        learner_answer: str,
        target_transcript: str,
    ) -> ListeningEvaluationResult:
        """
        Evaluates a learner's listening exercise response against the target transcript.
        Calculates similarity score deterministically.
        """
        clean_given = self._normalize_text(learner_answer)
        clean_target = self._normalize_text(target_transcript)

        if not clean_target:
            similarity = 1.0 if not clean_given else 0.0
        elif clean_given == clean_target:
            similarity = 1.0
        else:
            # Word-level overlap similarity ratio
            given_words = clean_given.split()
            target_words = clean_target.split()
            matches = sum(1 for w in given_words if w in target_words)
            similarity = round(matches / max(len(target_words), len(given_words)), 2)

        is_correct = similarity >= 0.85

        return ListeningEvaluationResult(
            learner_id=learner_id,
            listening_target_id=listening_target_id,
            learner_answer=learner_answer,
            target_transcript=target_transcript,
            is_correct=is_correct,
            similarity_score=similarity,
        )

    def _normalize_text(self, text: str) -> str:
        text = text.lower().strip()
        for char in [".", ",", "!", "?", ";", ":", '"', "'"]:
            text = text.replace(char, "")
        return text
