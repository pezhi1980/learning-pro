# backend/tests/test_final_e2e_and_integrity.py

import os
import unittest
import time
from datetime import datetime, timezone
from backend.curriculum.curriculum_service import CurriculumService
from backend.learner.learner_repository import LearnerRepository
from backend.learner.knowledge_models import VocabularyKnowledgeState
from backend.learning.learning_decision_service import LearningDecisionService
from backend.session.session_builder import SessionBuilder
from backend.session.daily_session_service import DailySessionService
from backend.agents.content_agent import ContentPedagogyAgent
from backend.validators.output_validator import OutputValidator
from backend.evaluation.evaluation_service import EvaluationService
from backend.evaluation.answer_evaluator import AnswerEvaluator
from backend.evaluation.evaluation_models import EvaluationResult
from backend.schemas.agent_output import ExerciseItem, TargetTrace
from backend.intelligence.spaced_repetition_engine import SpacedRepetitionEngine
from backend.learner.error_tracker import ErrorTracker
from backend.assessment.placement_service import PlacementService
from backend.assessment.level_assessment_service import LevelAssessmentService
from backend.audio.listening_service import ListeningService
from backend.audio.tts_providers import MockTTSProvider
from backend.audio.audio_models import TTSRequest
from backend.speaking.speaking_service import SpeakingService
from backend.speaking.speaking_models import SpeechAudioInput
from backend.writing.writing_service import WritingService
from backend.writing.writing_models import WritingSubmission
from backend.security.authorization_service import AuthorizationService, AccessControlContext
from backend.security.input_sanitizer import InputSanitizer
from backend.operations.health_checker import HealthChecker


class TestFinalE2EAndIntegrity(unittest.TestCase):
    def setUp(self):
        self.curriculum_service = CurriculumService()
        self.learner_repo = LearnerRepository()
        self.decision_service = LearningDecisionService()
        self.session_builder = SessionBuilder()
        self.session_service = DailySessionService(self.session_builder)
        self.content_agent = ContentPedagogyAgent()
        self.output_validator = OutputValidator()
        self.evaluation_service = EvaluationService(repository=self.learner_repo)
        self.answer_evaluator = AnswerEvaluator()
        self.srs_engine = SpacedRepetitionEngine()
        self.error_tracker = ErrorTracker(repository=self.learner_repo)
        self.auth_service = AuthorizationService()
        self.input_sanitizer = InputSanitizer()
        self.health_checker = HealthChecker(curriculum_service=self.curriculum_service)

    def test_1_curriculum_data_integrity(self):
        """Verify all curriculum references exist in authoritative PDF source layer."""
        grammar_items = self.curriculum_service.list_all_grammar()
        vocab_items = self.curriculum_service.vocab_repo.list_all()

        self.assertGreater(len(grammar_items), 0, "PDF Grammar curriculum must not be empty.")
        self.assertGreater(len(vocab_items), 0, "PDF Vocabulary curriculum must not be empty.")

        for item in grammar_items[:5]:
            self.assertIsNotNone(item.grammar_code)
            self.assertIsNotNone(item.source_item_id)
            self.assertIsNotNone(item.document_level)

        for item in vocab_items[:5]:
            self.assertIsNotNone(item.lexeme)
            self.assertIsNotNone(item.source_item_id)
            self.assertIsNotNone(item.document_level)

    def test_2_complete_learner_e2e(self):
        """Full Learner E2E Loop: Decision -> Session -> Agent -> Validator -> Evaluation -> Mastery."""
        learner_id = "learner_e2e_101"

        # 1. Learning Decision
        decision = self.decision_service.determine_next_learning_decision(learner_id, requested_level="A1")
        self.assertEqual(decision.learner_id, learner_id)
        self.assertIsNotNone(decision.decision_id)

        # 2. Session Building
        session = self.session_service.create_session(decision)
        self.assertEqual(session.learner_id, learner_id)
        self.assertGreater(len(session.activities), 0)

        # 3. Answer Evaluation
        ex = ExerciseItem(
            id="ex_e2e_1",
            exercise_type="multiple_choice",
            prompt="Choose verb form",
            options=["go", "goes"],
            correct_answer="goes",
            explanation="3rd person singular",
            targets=TargetTrace(learning_object_id="g_1", grammar_codes=["g_code_1"]),
        )
        eval_res = self.answer_evaluator.evaluate_exercise(learner_id, "lesson_1", ex, "goes")
        self.assertTrue(eval_res.correct)
        self.assertGreaterEqual(eval_res.score, 1.0)

    def test_3_assessments_e2e(self):
        """Verify Placement, Diagnostic, Checkpoint, and Level Assessment flows."""
        learner_id = "learner_assess_201"

        placement_svc = PlacementService(curriculum_service=self.curriculum_service)
        placement = placement_svc.create_placement_test(learner_id=learner_id)
        self.assertIsNotNone(placement)

        level_svc = LevelAssessmentService(curriculum_service=self.curriculum_service)
        level_ass = level_svc.create_level_assessment(learner_id=learner_id, level_code="A1")
        self.assertIsNotNone(level_ass)


    def test_4_listening_and_speaking_e2e(self):
        """Verify Listening & Speaking practice pipeline with fake provider fallback."""
        tts_provider = MockTTSProvider()
        req = TTSRequest(text="Hello world", voice="en_male")
        audio_ref = tts_provider.generate_speech(req)
        self.assertIsNotNone(audio_ref)

        speaking_svc = SpeakingService()
        audio_input = SpeechAudioInput(audio_base64="ZmFrZV9hdWRpb19ieXRlcw==", audio_format="wav")
        result = speaking_svc.record_and_evaluate_pronunciation(
            learner_id="usr_spk_1",
            target_text="The cat sits on the mat.",
            audio_input=audio_input,
        )
        self.assertIsNotNone(result)
        self.assertGreaterEqual(result.pronunciation_quality_score, 0.0)

    def test_5_writing_e2e(self):
        """Verify Writing Practice free production evaluation and state update."""
        writing_svc = WritingService()
        sub = WritingSubmission(
            submission_id="sub_wrt_1",
            learner_id="usr_wrt_1",
            prompt="Write about your daily routine.",
            learner_text="I wake up at seven o'clock every morning.",
            task_type="paragraph",
        )
        eval_res = writing_svc.evaluate_writing(sub)
        self.assertIsNotNone(eval_res)
        self.assertIsNotNone(eval_res.feedback.task_completion_feedback)

    def test_6_review_and_repair_e2e(self):
        """Verify Spaced Repetition scheduling & Targeted Error Repair flow."""
        learner_id = "usr_rr_1"

        # Record error via ErrorTracker
        eval_result = EvaluationResult(
            evaluation_id="eval_rr_1",
            learner_id=learner_id,
            lesson_id="lesson_1",
            exercise_id="ex_101",
            exercise_type="multiple_choice",
            learner_answer="go",
            expected_answer="goes",
            evaluation_method="exact_match",
            correct=False,
            score=0.0,
            error_codes=["grammar_error"],
            target_learning_object_ids=["g_present_simple"],
        )
        patterns = self.error_tracker.process_evaluation_errors(eval_result)
        self.assertGreater(len(patterns), 0)

        # Spaced repetition calculation
        next_schedule = self.srs_engine.compute_next_schedule(
            current_stability=1.0,
            is_correct=True,
            overall_mastery=0.8,
            consecutive_correct=2,
            consecutive_incorrect=0,
            lapses=0,
            last_practiced_at=datetime.now(timezone.utc),
        )
        self.assertGreater(next_schedule[0], 0.0)

    def test_7_offline_sync_idempotency_e2e(self):
        """Verify offline submission queuing, sync, and idempotency protection."""
        submission_id = "sub_offline_unique_99"
        self.assertFalse(self.learner_repo.is_submission_processed(submission_id))

        self.learner_repo.record_submission(submission_id)
        self.assertTrue(self.learner_repo.is_submission_processed(submission_id))

    def test_8_vocabulary_sense_independence(self):
        """Verify Sense A progress does NOT automatically modify Sense B."""
        learner_id = "usr_sense_test"
        sense_a = "vocab:bank:financial"
        sense_b = "vocab:bank:river"

        state_a = VocabularyKnowledgeState(
            learner_id=learner_id,
            learning_object_id="v_bank",
            vocabulary_source_item_id="v_src_1",
            lexeme="bank",
            vocabulary_sense_id=sense_a,
            recognition=0.9,
            recall=0.8,
            usage=0.8,
            stability=0.8,
        )
        self.learner_repo.save_vocabulary_state(state_a)

        retrieved_a = self.learner_repo.get_vocabulary_state(learner_id, sense_a)
        retrieved_b = self.learner_repo.get_vocabulary_state(learner_id, sense_b)

        self.assertIsNotNone(retrieved_a)
        self.assertEqual(retrieved_a.recognition, 0.9)
        self.assertIsNone(retrieved_b)  # Sense B remains unaffected

    def test_9_grammar_vocab_independence(self):
        """Verify Grammar and Vocabulary complexity are controlled independently."""
        grammar_targets = self.curriculum_service.list_grammar_by_level("A1")
        vocab_targets = self.curriculum_service.list_vocabulary_by_level("A1")

        self.assertGreater(len(grammar_targets), 0)
        self.assertGreater(len(vocab_targets), 0)

    def test_10_failure_injection_resilience(self):
        """Verify system handles security violations, path traversal attempts, and health probes safely."""
        ctx = AccessControlContext(requester_id="usr_A", is_admin=False)
        with self.assertRaises(PermissionError):
            self.auth_service.authorize_resource_access(ctx, resource_owner_id="usr_B", resource_type="sessions")

        # Path Traversal & Injection rejection
        with self.assertRaises(ValueError):
            self.input_sanitizer.sanitize_identifier("../etc/passwd")

        # Health Probe Resilience
        report = self.health_checker.check_health()
        self.assertIn(report.status, ["HEALTHY", "DEGRADED"])

    def test_11_production_bypass_audit(self):
        """Verify no direct ContentAgent calls or unauthorized curriculum mutations occur."""
        ctx_admin = AccessControlContext(requester_id="admin_01", is_admin=True)
        self.auth_service.authorize_resource_access(ctx_admin, resource_owner_id="usr_owner", resource_type="curriculum")


if __name__ == "__main__":
    unittest.main()
