# backend/speaking/speaking_service.py
"""
ROLE: SPEAKING SERVICE

Orchestrates:
- Pronunciation Practice & retries for words, chunks, and sentences.
- 5 Speaking Practice modes (Read Aloud, Controlled Answer, Sentence Production, Guided Response, Dialogue).
- Speech Recognition (STT) provider transcription.
- 3-Way Evaluation separation (STT Confidence, Linguistic Correctness, Pronunciation Quality).
- Learner Voice Privacy management and retention deletion.
"""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.speaking.speaking_evaluator import SpeakingEvaluator
from backend.speaking.speaking_models import (
    PronunciationResult,
    SpeakingEvaluationResult,
    SpeakingMode,
    SpeechAudioInput,
    SpeechTranscriptionResult,
    TargetLevel,
    VoiceAttemptRecord,
)
from backend.speaking.speech_interface import SpeechRecognizerInterface
from backend.speaking.speech_providers import SpeechRecognizerFactory
from backend.speaking.voice_attempt_repository import VoiceAttemptRepository
from backend.speaking.voice_privacy_manager import VoicePrivacyManager

logger = logging.getLogger(__name__)


class SpeakingService:
    """
    Core Speaking & Pronunciation service managing STT transcription, evaluation, and voice privacy.
    """

    def __init__(
        self,
        recognizer: Optional[SpeechRecognizerInterface] = None,
        repository: Optional[VoiceAttemptRepository] = None,
        evaluator: Optional[SpeakingEvaluator] = None,
        privacy_manager: Optional[VoicePrivacyManager] = None,
    ):
        self.recognizer = recognizer or SpeechRecognizerFactory.get_recognizer()
        self.repository = repository or VoiceAttemptRepository()
        self.evaluator = evaluator or SpeakingEvaluator()
        self.privacy_manager = privacy_manager or VoicePrivacyManager(repository=self.repository)

    def record_and_evaluate_pronunciation(
        self,
        learner_id: str,
        target_text: str,
        audio_input: SpeechAudioInput,
        target_level: TargetLevel = TargetLevel.sentence,
        linked_target_id: Optional[str] = None,
    ) -> PronunciationResult:
        """
        Transcribes audio, records attempt, and evaluates pronunciation quality for word/chunk/sentence.
        """
        # 1. Transcribe Audio
        transcription_res = self.recognizer.transcribe(audio_input, target_text_hint=target_text)

        # 2. Record Voice Attempt
        now = datetime.now(timezone.utc)
        attempt_id = f"voice_att:{learner_id}:{int(now.timestamp())}"
        attempt_record = VoiceAttemptRecord(
            attempt_id=attempt_id,
            learner_id=learner_id,
            target_text=target_text,
            target_type=target_level,
            linked_target_id=linked_target_id,
            audio_storage_reference=f"memory://voice/{attempt_id}.{audio_input.audio_format}",
            transcription=transcription_res.transcript,
            created_at=now,
            is_deleted=False,
        )
        self.repository.save_attempt(attempt_record)

        # 3. Evaluate 3-way Pronunciation Quality
        return self.evaluator.evaluate_pronunciation(
            attempt_id=attempt_id,
            learner_id=learner_id,
            target_text=target_text,
            transcription_result=transcription_res,
        )

    def evaluate_speaking_practice(
        self,
        learner_id: str,
        mode: SpeakingMode,
        prompt: str,
        audio_input: SpeechAudioInput,
        expected_text_or_patterns: List[str],
        linked_target_id: Optional[str] = None,
    ) -> SpeakingEvaluationResult:
        """
        Evaluates speaking practice across 5 modes (read_aloud, controlled_answer, sentence_production, guided_response, controlled_dialogue).
        """
        hint = expected_text_or_patterns[0] if expected_text_or_patterns else prompt
        transcription_res = self.recognizer.transcribe(audio_input, target_text_hint=hint)

        now = datetime.now(timezone.utc)
        attempt_id = f"speaking_eval:{learner_id}:{int(now.timestamp())}"
        attempt_record = VoiceAttemptRecord(
            attempt_id=attempt_id,
            learner_id=learner_id,
            target_text=prompt,
            target_type=TargetLevel.sentence,
            linked_target_id=linked_target_id,
            audio_storage_reference=f"memory://voice/{attempt_id}.{audio_input.audio_format}",
            transcription=transcription_res.transcript,
            created_at=now,
            is_deleted=False,
        )
        self.repository.save_attempt(attempt_record)

        return self.evaluator.evaluate_speaking_mode(
            evaluation_id=attempt_id,
            learner_id=learner_id,
            mode=mode,
            prompt=prompt,
            transcription_result=transcription_res,
            expected_text_or_patterns=expected_text_or_patterns,
        )

    def transcribe_audio(
        self, audio_input: SpeechAudioInput, target_hint: Optional[str] = None
    ) -> SpeechTranscriptionResult:
        """
        Transcribes audio directly via configured STT provider.
        """
        return self.recognizer.transcribe(audio_input, target_text_hint=target_hint)

    def purge_learner_voice_privacy_data(self, learner_id: str) -> Dict[str, Any]:
        """
        Purges all learner voice recording data for privacy compliance.
        """
        return self.privacy_manager.purge_learner_voice_data(learner_id, hard_delete=True)
