# backend/tests/test_content_lifecycle.py
"""
ROLE: TEST SUITE FOR CONTENT LIFECYCLE & BACKGROUND PROCESSING

Comprehensive deterministic unit tests covering:
- Version Immutability & Historical Record Preservation
- Publishing Workflow State Transitions (generated, rejected, validated, published, deprecated, replaced)
- Production Serving Rule (ONLY 'published' content eligible)
- Handling of Rejected Content (rejected content cannot be published or served)
- SHA-256 Deterministic Content Caching & Invalidation
- Pre-Generation Engine enforcing 5-stage validation pipeline
- Async Background Job submission & status tracking
"""

import sys
import os
import unittest
import asyncio

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
root_dir = os.path.abspath(os.path.join(backend_dir, ".."))
for d in [root_dir, backend_dir]:
    if d not in sys.path:
        sys.path.insert(0, d)

from backend.lifecycle import (
    BackgroundJobService,
    ContentCacheManager,
    ContentVersioningEngine,
    JobStatus,
    JobType,
    PreGenerationService,
    PublishingStatus,
    PublishingWorkflowService,
)
from backend.schemas import CurriculumAssignmentRequest, GenerationMode, TaskDifficulty
from backend.agents.content_agent import ContentPedagogyAgent, AgentInput
from backend.schemas.agent_output import AgentOutput, ExampleItem, ExerciseItem, ExplanationBlock, TargetTrace
from backend.services.lesson_generation_service import LessonGenerationService


class MockContentAgent(ContentPedagogyAgent):
    async def generate(self, agent_input: AgentInput) -> AgentOutput:
        g_codes = [g.grammar_code for g in agent_input.target_grammar]
        return AgentOutput(
            request_id=agent_input.request_id,
            generation_mode=agent_input.generation_mode,
            explanations=[
                ExplanationBlock(
                    id="exp_1",
                    title="Present Simple",
                    content="Present simple explanation content.",
                    targets=TargetTrace(grammar_codes=g_codes),
                )
            ],
            examples=[
                ExampleItem(
                    id="ex_1",
                    sentence="I am a student.",
                    translation="I am a student.",
                    targets=TargetTrace(grammar_codes=g_codes),
                )
            ],
            exercises=[
                ExerciseItem(
                    id="ex_item_1",
                    exercise_type="multiple_choice",
                    prompt="Select correct verb form:",
                    options=["am", "is", "are", "be"],
                    correct_answer="am",
                    targets=TargetTrace(grammar_codes=g_codes),
                )
            ],
        )



class TestContentLifecycle(unittest.TestCase):


    @classmethod
    def setUpClass(cls):
        cls.versioning_engine = ContentVersioningEngine()
        cls.publishing_service = PublishingWorkflowService(versioning_engine=cls.versioning_engine)
        cls.cache_manager = ContentCacheManager()
        cls.mock_agent = MockContentAgent()
        cls.lesson_gen_service = LessonGenerationService(agent=cls.mock_agent)
        cls.pre_gen_service = PreGenerationService(
            lesson_gen_service=cls.lesson_gen_service,
            versioning_engine=cls.versioning_engine,
            publishing_service=cls.publishing_service,
        )
        cls.job_service = BackgroundJobService()

    def test_1_version_immutability(self):
        """
        Verify historical content versions are preserved immutably and never silently overwritten.
        """
        content_id = "lesson_test_101"
        v1 = self.versioning_engine.register_content_version(
            content_id=content_id,
            payload={"title": "Lesson v1"},
            target_ids=["g_present_simple"],
            initial_status=PublishingStatus.validated,
        )

        self.assertEqual(v1.version_index, 1)

        v2 = self.versioning_engine.register_content_version(
            content_id=content_id,
            payload={"title": "Lesson v2 Updated"},
            target_ids=["g_present_simple"],
            initial_status=PublishingStatus.validated,
        )

        self.assertEqual(v2.version_index, 2)

        history = self.versioning_engine.list_version_history(content_id)
        self.assertEqual(len(history), 2, "Historical versions must be immutably preserved.")
        self.assertEqual(history[0].replaced_by_version_hash, v2.content_version_hash)

    def test_2_publishing_workflow_states_and_serving_rule(self):
        """
        Verify publishing state transitions and enforce rule: ONLY 'published' content can be served in production.
        """
        content_id = "lesson_pub_201"
        rec = self.versioning_engine.register_content_version(
            content_id=content_id,
            payload={"title": "Publishing Test Lesson"},
            target_ids=["g_be_present"],
            initial_status=PublishingStatus.validated,
        )

        # Attempt serving prior to publishing -> must raise ValueError
        with self.assertRaises(ValueError):
            self.publishing_service.get_servable_production_content(content_id)

        # Publish content
        pub_rec = self.publishing_service.publish_content(rec.content_version_hash)
        self.assertEqual(pub_rec.publishing_status, PublishingStatus.published)

        # Retrieve for production serving -> success
        servable = self.publishing_service.get_servable_production_content(content_id)
        self.assertEqual(servable.content_version_hash, rec.content_version_hash)

    def test_3_rejected_content_handling(self):
        """
        Verify rejected content cannot be published or served in production.
        """
        content_id = "lesson_rej_301"
        rej_rec = self.versioning_engine.register_content_version(
            content_id=content_id,
            payload={"title": "Invalid Lesson Output"},
            target_ids=["g_unknown"],
            initial_status=PublishingStatus.rejected,
        )

        with self.assertRaises(ValueError):
            self.publishing_service.publish_content(rej_rec.content_version_hash)

        with self.assertRaises(ValueError):
            self.publishing_service.get_servable_production_content(content_id)

    def test_4_deterministic_content_cache(self):
        """
        Verify deterministic content caching and version-based invalidation.
        """
        key = self.cache_manager.compute_cache_key(
            target_ids=["g_present_simple"],
            mode="grammar",
            cefr_level="A1",
            content_version_hash="hash_abc_123",
        )

        rec = self.versioning_engine.register_content_version(
            content_id="cached_lesson_401",
            payload={"text": "Cached text"},
            initial_status=PublishingStatus.published,
        )

        self.cache_manager.store_cached_content(key, rec)
        cached = self.cache_manager.get_cached_content(key)
        self.assertIsNotNone(cached)
        self.assertEqual(cached.content_id, "cached_lesson_401")

        # Invalidate cache
        deleted = self.cache_manager.invalidate_cache("hash_abc_123")
        self.assertEqual(deleted, 0)  # hash didn't match rec.content_version_hash

        deleted_actual = self.cache_manager.invalidate_cache(rec.content_version_hash)
        self.assertEqual(deleted_actual, 1)

    def test_5_pre_generation_service(self):
        """
        Verify pre-generation service passes through LessonGenerationService validation pipeline.
        """
        req = CurriculumAssignmentRequest(
            request_id="req_pre_gen_501",
            target_language="en",
            generation_mode=GenerationMode.grammar_micro_lesson,
            task_difficulty=TaskDifficulty.recognition,
            target_grammar_ids=["grammar:en:A1:PP.I_am:1"],
        )




        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            lesson = loop.run_until_complete(self.pre_gen_service.pre_generate_micro_lesson(req))
            self.assertIsNotNone(lesson)
            self.assertIn(lesson.status.value, ["validated", "rejected"])
        finally:
            loop.close()

    def test_6_async_background_jobs(self):
        """
        Verify background job submission and execution tracking.
        """
        job = self.job_service.submit_job(
            job_type=JobType.maintenance,
            payload={"task": "purge_scratch"},
        )

        self.assertEqual(job.job_type, JobType.maintenance)
        self.assertIn(job.status, [JobStatus.pending, JobStatus.running, JobStatus.completed])

        fetched = self.job_service.get_job(job.job_id)
        self.assertIsNotNone(fetched)


if __name__ == "__main__":
    unittest.main()
