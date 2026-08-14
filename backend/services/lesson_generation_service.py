# backend/services/lesson_generation_service.py
"""
ROLE: LESSON GENERATION ORCHESTRATOR

This service controls the complete lesson-generation workflow.
It is the central coordinator between curriculum assignment, Agent generation, and deterministic validators.

MANDATORY FLOW:
1. Receive CurriculumAssignmentRequest.
2. Obtain authorized AgentInput targets from CurriculumAssignmentService.
3. Call Content Generation Agent with AgentInput.
4. Receive AgentOutput.
5. Run OutputValidator.
6. Run SourceValidator.
7. Run CoverageValidator.
8. Run CurriculumValidator.
9. Run ExerciseValidator.
10. Accept lesson (LessonStatus.validated) ONLY if all required validators pass.
11. Reject lesson (LessonStatus.rejected) if any validator fails.
"""

from typing import Dict, Optional
from backend.agents.content_agent import ContentPedagogyAgent
from backend.curriculum import CurriculumService
from backend.schemas import (
    AgentInput,
    AgentOutput,
    CurriculumAssignmentRequest,
    Lesson,
    LessonStatus,
    ValidationResult,
)
from backend.services.curriculum_assignment_service import CurriculumAssignmentService
from backend.validators import validate_all


class LessonGenerationService:
    """
    Central orchestration service for content generation, validation, and lifecycle control.
    """

    def __init__(
        self,
        assignment_service: Optional[CurriculumAssignmentService] = None,
        agent: Optional[ContentPedagogyAgent] = None,
        curriculum_service: Optional[CurriculumService] = None,
    ):
        self.curriculum_service = curriculum_service or CurriculumService()
        self.assignment_service = assignment_service or CurriculumAssignmentService(curriculum_service=self.curriculum_service)
        self.agent = agent or ContentPedagogyAgent()

    async def generate_lesson(self, request: CurriculumAssignmentRequest) -> Lesson:
        """
        Main pipeline entrypoint: ASSIGN -> GENERATE -> VALIDATE -> ACCEPT/REJECT
        """
        # STEP 1 & 2 & 3: Assign & Validate AgentInput targets
        agent_input: AgentInput = self.assignment_service.build_agent_input(request)

        # STEP 4 & 5: Invoke Agent with AgentInput
        agent_output: AgentOutput = await self.agent.generate(agent_input)

        # STEP 6-11: Run 5-stage validation pipeline
        validated_output, validation_results = validate_all(
            input_data=agent_input,
            raw_or_parsed_output=agent_output,
            curriculum_service=self.curriculum_service,
        )

        # STEP 12 & 13 & 14: Determine final LessonStatus
        all_passed = (
            validated_output is not None and
            all(res.passed for res in validation_results.values())
        )

        final_status = LessonStatus.validated if all_passed else LessonStatus.rejected

        # Construct canonical Lesson object
        return Lesson(
            lesson_id=f"lesson:{request.request_id}",
            request_id=request.request_id,
            target_language=request.target_language,
            native_language=request.native_language,
            generation_mode=request.generation_mode,
            assigned_grammar=agent_input.target_grammar,
            assigned_vocabulary=agent_input.target_vocabulary,
            content=validated_output or agent_output,
            status=final_status,
            validation_results=validation_results,
        )
