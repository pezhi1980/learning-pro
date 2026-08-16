# backend/tests/test_audio_system.py
"""
ROLE: TEST SUITE FOR LISTENING, TTS & AUDIO INFRASTRUCTURE

Comprehensive deterministic unit tests covering:
- Provider-Independent TTS Abstraction & Mock Execution
- SHA-256 Deterministic Audio Caching & Zero Duplicate Generation
- Content Version Linkage & Cache Invalidation
- Audio Asset Repository & Target Linkage Tracking
- Listening Playback Sessions & State Transitions (idle -> loading -> playing -> paused -> completed)
- Transcript Reveal & Replay Controls
- Listening Exercise Evaluation
- Fallback Handling for Provider Failures
"""

import sys
import os
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.audio import (
    AudioCacheManager,
    AudioAssetRepository,
    AudioStatus,
    AudioType,
    ListeningPlaybackSession,
    ListeningService,
    MockTTSProvider,
    OpenAITTSProvider,
    PlaybackState,
    TTSProviderFactory,
    TTSRequest,
)


class TestAudioSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_provider = MockTTSProvider()
        cls.cache_manager = AudioCacheManager()
        cls.repository = AudioAssetRepository()
        cls.listening_service = ListeningService(
            provider=cls.mock_provider,
            cache_manager=cls.cache_manager,
            repository=cls.repository,
        )

    def test_1_tts_provider_abstraction_and_mock(self):
        """
        Verify MockTTSProvider generates synthetic audio response conforming to TTSProviderInterface without network calls.
        """
        req = TTSRequest(text="Hello world, this is a test.", voice="alloy", speed=1.0)
        res = self.mock_provider.generate_speech(req)

        self.assertEqual(res.provider_name, "mock_tts")
        self.assertGreater(len(res.audio_bytes), 0)
        self.assertGreater(res.duration_seconds, 0.0)

    def test_2_deterministic_audio_caching(self):
        """
        Verify identical TTS requests produce identical SHA-256 cache keys and hit cache with 0 duplicate generation.
        """
        req = TTSRequest(
            text="Deterministic caching test string.",
            voice="echo",
            speed=1.0,
            language="en",
            source_content_version="v1.0",
        )

        key1 = self.cache_manager.compute_cache_key(req, "mock_tts")
        key2 = self.cache_manager.compute_cache_key(req, "mock_tts")
        self.assertEqual(key1, key2, "Identical requests must produce identical cache keys.")

        # First call: Cache miss & generation
        asset1, audio1 = self.listening_service.get_or_generate_audio(req)
        self.assertEqual(asset1.cache_key, key1)

        # Second call: Cache hit
        asset2, audio2 = self.listening_service.get_or_generate_audio(req)
        self.assertEqual(asset1.asset_id, asset2.asset_id)
        self.assertEqual(audio1, audio2)

    def test_3_content_version_linkage_and_invalidation(self):
        """
        Verify changing content version produces a distinct cache key, and invalidate_by_version purges stale cache items.
        """
        req_v1 = TTSRequest(text="I am learning English.", source_content_version="v1")
        req_v2 = TTSRequest(text="I am learning English.", source_content_version="v2")

        key_v1 = self.cache_manager.compute_cache_key(req_v1, "mock_tts")
        key_v2 = self.cache_manager.compute_cache_key(req_v2, "mock_tts")
        self.assertNotEqual(key_v1, key_v2, "Version change must produce a distinct cache key.")

        # Store v1
        self.listening_service.get_or_generate_audio(req_v1)
        self.assertIsNotNone(self.cache_manager.get_cached_audio(key_v1))

        # Invalidate v1
        deleted_count = self.cache_manager.invalidate_by_version("v1")
        self.assertEqual(deleted_count, 1)
        self.assertIsNone(self.cache_manager.get_cached_audio(key_v1))

    def test_4_audio_asset_repository_and_target_linkage(self):
        """
        Verify AudioAssetRepository tracks asset metadata, duration, storage references, and target linkages.
        """
        req = TTSRequest(
            text="Word target audio.",
            audio_type=AudioType.vocabulary,
            linked_target_id="v_item_12345",
        )

        asset, _ = self.listening_service.get_or_generate_audio(req)
        self.assertEqual(asset.linked_target_id, "v_item_12345")

        fetched = self.repository.get_asset(asset.asset_id)
        self.assertIsNotNone(fetched)
        self.assertEqual(fetched.linked_target_id, "v_item_12345")

        target_assets = self.repository.get_assets_by_target("v_item_12345")
        self.assertGreater(len(target_assets), 0)

    def test_5_listening_playback_session_lifecycle(self):
        """
        Test playback state transitions: idle -> loading -> playing -> paused -> completed, and replay counter.
        """
        learner_id = "learner_audio_01"
        session = self.listening_service.create_playback_session(
            learner_id=learner_id,
            asset_id="asset_test_101",
            transcript_text="She is reading a book.",
        )

        self.assertEqual(session.playback_state, PlaybackState.idle)
        self.assertFalse(session.is_transcript_revealed)

        # Transition to playing
        sess1 = self.listening_service.update_playback_state(session.session_id, PlaybackState.playing)
        self.assertEqual(sess1.playback_state, PlaybackState.playing)

        # Transition to paused
        sess2 = self.listening_service.update_playback_state(session.session_id, PlaybackState.paused, current_position_seconds=2.5)
        self.assertEqual(sess2.playback_state, PlaybackState.paused)
        self.assertEqual(sess2.current_position_seconds, 2.5)

        # Complete playback
        sess3 = self.listening_service.update_playback_state(session.session_id, PlaybackState.completed, current_position_seconds=5.0)
        self.assertEqual(sess3.playback_state, PlaybackState.completed)

        # Replay
        sess4 = self.listening_service.update_playback_state(session.session_id, PlaybackState.playing, current_position_seconds=0.0)
        self.assertEqual(sess4.replay_count, 1)

    def test_6_transcript_reveal(self):
        """
        Verify transcript text remains hidden by default and is revealed on request.
        """
        learner_id = "learner_transcript_01"
        session = self.listening_service.create_playback_session(
            learner_id=learner_id,
            asset_id="asset_test_102",
            transcript_text="They go to school by bus.",
        )

        self.assertFalse(session.is_transcript_revealed)

        revealed = self.listening_service.reveal_transcript(session.session_id)
        self.assertTrue(revealed.is_transcript_revealed)
        self.assertEqual(revealed.transcript_text, "They go to school by bus.")

    def test_7_listening_exercise_evaluation(self):
        """
        Test answer evaluation and similarity score calculation for listening exercises.
        """
        eval_res_exact = self.listening_service.evaluate_listening_exercise(
            learner_id="user_listen_eval",
            listening_target_id="target_01",
            learner_answer="She lives in Stockholm.",
            target_transcript="She lives in Stockholm.",
        )
        self.assertTrue(eval_res_exact.is_correct)
        self.assertEqual(eval_res_exact.similarity_score, 1.0)

        eval_res_close = self.listening_service.evaluate_listening_exercise(
            learner_id="user_listen_eval",
            listening_target_id="target_01",
            learner_answer="She lives in Stockholm",  # missing period
            target_transcript="She lives in Stockholm.",
        )
        self.assertTrue(eval_res_close.is_correct)

    def test_8_openai_tts_provider_fallback(self):
        """
        Verify OpenAITTSProvider gracefully falls back to MockTTSProvider when API key is unconfigured/invalid.
        """
        provider = OpenAITTSProvider(api_key="sk-proj-invalid-key-for-test")
        req = TTSRequest(text="Fallback test string.")
        res = provider.generate_speech(req)

        self.assertIsNotNone(res)
        self.assertGreater(len(res.audio_bytes), 0)


if __name__ == "__main__":
    unittest.main()
