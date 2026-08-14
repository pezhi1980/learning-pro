# backend/lifecycle/pre_generation_service.py
"""
ROLE: PRE-GENERATION SERVICE

Pre-generates common curriculum lessons and exercises before learner requests.
MANDATORY RULE: Every pre-generated item STILL goes through the normal 5-stage validation pipeline
(OutputValidator, SourceValidator, CoverageValidator, CurriculumValidator, ExerciseValidator).
Only validated items enter 'validated' / 'published' status. Rejected items remain 'rejected'.
"""

import logging
from typing import Dict, List, Optional
from backend.lifecycle.content_versioning_engine import ContentVersioningEngine
from backend.lifecycle.lifecycle_models import ContentVersionRecord, PublishingStatus
from backend.lifecycle.publishing_workflow_service import PublishingWorkflowService
from backend.schemas import CurriculumAssignmentRequest, Lesson, LessonStatus
from backend.services.lesson_generation_service import LessonGenerationService

logger = logging.getLogger(__name__)


class PreGenerationService:
    """
    Pre-generation orchestrator ensuring pre-generated content runs through normal validation pipelines.
    """

    def __init__(
        self,
        lesson_gen_service: Optional[LessonGenerationService] = None,
        versioning_engine: Optional[ContentVersioningEngine] = None,
        publishing_service: Optional[PublishingWorkflowService] = None,
    ):
        self.lesson_gen_service = lesson_gen_service or LessonGenerationService()
        self.versioning_engine = versioning_engine or ContentVersioningEngine()
        self.publishing_service = publishing_service or PublishingWorkflowService(
            versioning_engine=self.versioning_engine
        )

    async def pre_generate_micro_lesson(self, assignment_request: CurriculumAssignmentRequest) -> Lesson:
        """
        Pre-generates a micro lesson through LessonGenerationService.
        Enforces normal validation pipeline execution.
        """
        # STEP 1: Invoke official LessonGenerationService pipeline (runs all 5 validators)
        lesson: Lesson = await self.lesson_gen_service.generate_lesson(assignment_request)

        content_id = lesson.lesson_id
        target_ids = (assignment_request.target_grammar_ids or []) + (assignment_request.target_vocabulary_ids or [])


        # STEP 2: Determine initial publishing status based on validation result
        initial_status = PublishingStatus.validated if lesson.status == LessonStatus.validated else PublishingStatus.rejected

        # STEP 3: Register version
        payload = lesson.model_dump()
        record: ContentVersionRecord = self.versioning_engine.register_content_version(
            content_id=content_id,
            payload=payload,
            target_ids=target_ids,
            initial_status=initial_status,
        )

        # STEP 4: Publish if validated, preserve rejected if invalid
        if record.publishing_status == PublishingStatus.validated:
            self.publishing_service.publish_content(record.content_version_hash)
            logger.info(f"Pre-generated lesson '{content_id}' validated and published.")
        else:
            logger.warning(f"Pre-generated lesson '{content_id}' rejected by validation pipeline.")

        return lesson
