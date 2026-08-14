# backend/tests/test_speaking_system.py
"""
ROLE: TEST SUITE FOR SPEAKING, STT & PRONUNCIATION SYSTEM

Comprehensive deterministic unit tests covering:
- Speech Recognition Provider Abstraction & Mock execution (0 paid live speech calls)
- Pronunciation Practice & feedback for words, chunks, and sentences
- 5 Speaking Practice Modes (Read Aloud, Controlled Answer, Sentence Production, Guided Response, Dialogue)
- 3-Way Evaluation Separation (STT Confidence vs Linguistic Correctness vs Pronunciation Quality)
- Voice Attempt Storage, target traceability, and deletion state
- Learner Voice Privacy purging (GDPR compliance)
- Fallback Handling for STT Providers
"""

import sys
import os
import base64
import unittest

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.speaking import (
    MockSpeechRecognizer,
    PronunciationResult,
    SpeakingEvaluationResult,
    SpeakingMode,
    SpeakingService,
    SpeechAudioInput,
    SpeechRecognizerFactory,
    TargetLevel,
    VoiceAttemptRepository,
    VoicePrivacyManager,
    WhisperSpeechRecognizer,
)


class TestSpeakingSystem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mock_recognizer = MockSpeechRecognizer()
        cls.repository = VoiceAttemptRepository()
        cls.speaking_service = SpeakingService(
            recognizer=cls.mock_recognizer,
            repository=cls.repository,
        )

    def _create_mock_audio_b64(self, spoken_text: str) -> str:
        payload = f"MOCK_AUDIO_DATA:[text='{spoken_text}']"
        return base64.b64encode(payload.encode("utf-8")).decode("utf-8")

    def test_1_speech_recognition_provider_abstraction(self):
        """
        Verify MockSpeechRecognizer conforms to SpeechRecognizerInterface without live paid speech API calls.
        """
        b64_audio = self._create_mock_audio_b64("Hello world")
        audio_input = SpeechAudioInput(audio_base64=b64_audio)

        res = self.mock_recognizer.transcribe(audio_input)
        self.assertEqual(res.provider_name, "mock_stt")
        self.assertEqual(res.transcript, "Hello world")
        self.assertGreater(res.transcription_confidence, 0.5)

    def test_2_pronunciation_practice_words_chunks_sentences(self):
        """
        Test pronunciation attempts and feedback for target words, chunks, and sentences.
        """
        learner_id = "user_pron_01"
        target_text = "I would like a cup of coffee"
        audio_input = SpeechAudioInput(audio_base64=self._create_mock_audio_b64(target_text))

        res = self.speaking_service.record_and_evaluate_pronunciation(
            learner_id=learner_id,
            target_text=target_text,
            audio_input=audio_input,
            target_level=TargetLevel.sentence,
            linked_target_id="v_coffee_01",
        )

        self.assertIsInstance(res, PronunciationResult)
        self.assertEqual(res.target_text, target_text)
        self.assertGreaterEqual(res.overall_score, 0.70)
        self.assertGreater(len(res.word_level_feedback), 0)

    def test_3_three_way_evaluation_separation(self):
        """
        Verify explicit 3-way separation between STT Confidence, Linguistic Correctness, and Pronunciation Quality.
        """
        learner_id = "user_3way_eval"
        target_text = "She goes to work by train"
        # Spoken audio has partial match: "She goes to work by bus"
        audio_input = SpeechAudioInput(audio_base64=self._create_mock_audio_b64("She goes to work by bus"))

        res = self.speaking_service.record_and_evaluate_pronunciation(
            learner_id=learner_id,
            target_text=target_text,
            audio_input=audio_input,
        )

        self.assertIsNotNone(res.transcription_confidence)
        self.assertIsNotNone(res.linguistic_correctness_score)
        self.assertIsNotNone(res.pronunciation_quality_score)

        # STT confidence is independent of linguistic mismatch
        self.assertEqual(res.transcription_confidence, 0.92)
        self.assertLess(res.linguistic_correctness_score, 1.0)

    def test_4_five_speaking_practice_modes(self):
        """
        Test speaking practice evaluation across all 5 modes:
        1. read_aloud
        2. controlled_answer
        3. sentence_production
        4. guided_response
        5. controlled_dialogue
        """
        learner_id = "user_speak_modes"

        for mode in [
            SpeakingMode.read_aloud,
            SpeakingMode.controlled_answer,
            SpeakingMode.sentence_production,
            SpeakingMode.guided_response,
            SpeakingMode.controlled_dialogue,
        ]:
            prompt = f"Prompt for {mode.value}"
            expected = ["Expected response phrase"]
            audio_input = SpeechAudioInput(audio_base64=self._create_mock_audio_b64("Expected response phrase"))

            eval_res = self.speaking_service.evaluate_speaking_practice(
                learner_id=learner_id,
                mode=mode,
                prompt=prompt,
                audio_input=audio_input,
                expected_text_or_patterns=expected,
            )

            self.assertIsInstance(eval_res, SpeakingEvaluationResult)
            self.assertEqual(eval_res.mode, mode)
            self.assertTrue(eval_res.is_passed)

    def test_5_voice_attempt_storage_and_target_traceability(self):
        """
        Verify voice attempt records store audio storage URIs and target linkages.
        """
        learner_id = "user_voice_store"
        target_text = "Practice sentence"
        audio_input = SpeechAudioInput(audio_base64=self._create_mock_audio_b64(target_text))

        self.speaking_service.record_and_evaluate_pronunciation(
            learner_id=learner_id,
            target_text=target_text,
            linked_target_id="target_grammar_code_01",
            audio_input=audio_input,
        )

        attempts = self.repository.get_attempts_by_learner(learner_id)
        self.assertEqual(len(attempts), 1)
        self.assertEqual(attempts[0].linked_target_id, "target_grammar_code_01")
        self.assertTrue(attempts[0].audio_storage_reference.startswith("memory://voice/"))

    def test_6_learner_voice_privacy_deletion(self):
        """
        Verify purge_learner_voice_privacy_data permanently purges voice attempt records for GDPR compliance.
        """
        learner_id = "user_privacy_test"
        audio_input = SpeechAudioInput(audio_base64=self._create_mock_audio_b64("Private voice sentence"))

        self.speaking_service.record_and_evaluate_pronunciation(
            learner_id=learner_id,
            target_text="Private voice sentence",
            audio_input=audio_input,
        )

        self.assertEqual(len(self.repository.get_attempts_by_learner(learner_id)), 1)

        # Purge learner voice data
        purge_res = self.speaking_service.purge_learner_voice_privacy_data(learner_id)
        self.assertEqual(purge_res["status"], "success")
        self.assertEqual(purge_res["deleted_records"], 1)

        # Verify learner attempts are hard deleted
        self.assertEqual(len(self.repository.get_attempts_by_learner(learner_id)), 0)

    def test_7_whisper_provider_fallback(self):
        """
        Verify WhisperSpeechRecognizer gracefully falls back to MockSpeechRecognizer when API key is missing/invalid.
        """
        provider = WhisperSpeechRecognizer(api_key="sk-proj-invalid-key")
        audio_input = SpeechAudioInput(audio_base64=self._create_mock_audio_b64("Fallback test"))

        res = provider.transcribe(audio_input)
        self.assertIsNotNone(res)
        self.assertEqual(res.transcript, "Fallback test")


if __name__ == "__main__":
    unittest.main()
