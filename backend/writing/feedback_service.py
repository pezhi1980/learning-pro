# backend/writing/feedback_service.py
"""
ROLE: WRITING FEEDBACK SERVICE

Generates structured feedback across 5 dimensions:
- target_grammar
- target_vocabulary
- task_completion
- clarity
- organization
Supports Repair connections and Vocabulary Sense clarifications.
CORE RULE: Do not turn every writing correction into newly authorized Curriculum.
"""

from typing import Any, Dict, List, Optional
from backend.writing.writing_models import StructuredFeedback, WritingSubmission, WritingTaskType


class WritingFeedbackService:
    """
    Service generating 5-dimension structured writing feedback.
    """

    def generate_feedback(
        self,
        submission: WritingSubmission,
        evaluation_score: float,
        eval_details: Dict[str, Any],
    ) -> StructuredFeedback:
        """
        Builds structured feedback for a writing submission.
        """
        is_correct = evaluation_score >= 0.70

        # 1. Target Grammar Feedback
        g_feedback: Optional[str] = None
        repair_targets: List[str] = []
        if submission.target_grammar_codes:
            g_codes_str = ", ".join(submission.target_grammar_codes)
            if is_correct:
                g_feedback = f"Good application of target grammar: {g_codes_str}."
            else:
                g_feedback = f"Review target grammar structure: {g_codes_str}."
                repair_targets.extend(submission.target_grammar_codes)

        # 2. Target Vocabulary Feedback & Sense Clarification
        v_feedback: Optional[str] = None
        sense_clarification: Optional[str] = None
        vocab_matches = eval_details.get("vocab_matches", [])

        if submission.target_vocabulary_items:
            v_items_str = ", ".join(submission.target_vocabulary_items)
            if len(vocab_matches) == len(submission.target_vocabulary_items):
                v_feedback = f"Excellent use of target vocabulary: {v_items_str}."
            else:
                missing = [v for v in submission.target_vocabulary_items if v not in vocab_matches]
                v_feedback = f"Try incorporating target vocabulary: {', '.join(missing)}."
                repair_targets.extend(missing)

        if submission.target_vocabulary_sense_ids:
            senses_str = ", ".join(submission.target_vocabulary_sense_ids)
            sense_clarification = (
                f"Vocabulary Sense Context: Note the specific sense for target IDs: '{senses_str}'."
            )

        # 3. Task Completion Feedback
        if is_correct:
            tc_feedback = f"Task completed successfully for '{submission.task_type.value}'."
        else:
            tc_feedback = (
                f"Task incomplete or under required word count ({eval_details.get('total_words', 0)} words provided, "
                f"minimum required: {eval_details.get('min_words_required', 3)})."
            )

        # 4. Clarity Feedback
        clarity = (
            "Clear and readable sentence structure."
            if is_correct
            else "Ensure clear word order and sentence punctuation."
        )

        # 5. Organization Feedback (for Paragraph and Extended Writing)
        org_feedback: Optional[str] = None
        if submission.task_type in (WritingTaskType.paragraph, WritingTaskType.extended_writing):
            org_feedback = (
                "Well-organized paragraph structure with smooth topic flow."
                if is_correct
                else "Use transition words and separate thoughts clearly across sentences."
            )

        return StructuredFeedback(
            target_grammar_feedback=g_feedback,
            target_vocabulary_feedback=v_feedback,
            task_completion_feedback=tc_feedback,
            clarity_feedback=clarity,
            organization_feedback=org_feedback,
            repair_target_ids=list(set(repair_targets)),
            vocabulary_sense_clarification=sense_clarification,
        )
