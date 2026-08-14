# backend/evaluation/answer_evaluator.py
"""
ROLE: ANSWER EVALUATOR

Provides deterministic evaluation of learner exercise submissions.
Supports: Multiple Choice, Fill in the Blank, Word Order, and Matching.
Does NOT fabricate certainty for unsupported free-production tasks.
Target traceability is strictly inherited from ExerciseItem metadata.
"""

import unicodedata
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from backend.evaluation.evaluation_models import EvaluationResult
from backend.schemas.agent_output import ExerciseItem


class AnswerEvaluator:
    """
    Evaluates learner answers against exercise contracts deterministically.
    """

    def evaluate_exercise(
        self,
        learner_id: str,
        lesson_id: str,
        exercise: ExerciseItem,
        learner_answer: str,
        submission_id: Optional[str] = None,
    ) -> EvaluationResult:
        eval_id = submission_id or f"eval:{learner_id}:{exercise.id}:{datetime.now(timezone.utc).timestamp()}"
        norm_answer = self._normalize_text(learner_answer)
        norm_expected = self._normalize_text(exercise.correct_answer or "")

        # Extract target traceability from ExerciseItem
        trace = exercise.targets
        g_codes = list(trace.grammar_codes) if trace.grammar_codes else []
        v_items = list(trace.vocabulary_items) if trace.vocabulary_items else []
        s_ids = list(trace.vocabulary_sense_ids) if trace.vocabulary_sense_ids else []
        lo_ids = [trace.learning_object_id] if trace.learning_object_id else []

        ex_type = (exercise.exercise_type or "multiple_choice").lower()

        # ── 1. Multiple Choice / Selection Evaluation ─────────────────────────
        if ex_type in ("multiple_choice", "selection", "mcq"):
            is_correct = (norm_answer == norm_expected)
            error_codes = [] if is_correct else self._classify_mcq_error(g_codes, v_items, s_ids)
            return EvaluationResult(
                evaluation_id=eval_id,
                learner_id=learner_id,
                lesson_id=lesson_id,
                exercise_id=exercise.id,
                correct=is_correct,
                score=1.0 if is_correct else 0.0,
                tested_grammar_codes=g_codes,
                tested_vocabulary_items=v_items,
                tested_vocabulary_sense_ids=s_ids,
                target_learning_object_ids=lo_ids,
                evaluation_method="mcq_exact",
                learner_answer=learner_answer,
                expected_answer=exercise.correct_answer or "",
                error_codes=error_codes,
            )

        # ── 2. Fill in the Blank Evaluation ───────────────────────────────────
        elif ex_type in ("fill_in_blank", "fill_blank", "blank"):
            is_correct = (norm_answer == norm_expected)
            error_codes = [] if is_correct else ["grammar.form.incorrect" if g_codes else "vocabulary.item.incorrect"]
            return EvaluationResult(
                evaluation_id=eval_id,
                learner_id=learner_id,
                lesson_id=lesson_id,
                exercise_id=exercise.id,
                correct=is_correct,
                score=1.0 if is_correct else 0.0,
                tested_grammar_codes=g_codes,
                tested_vocabulary_items=v_items,
                tested_vocabulary_sense_ids=s_ids,
                target_learning_object_ids=lo_ids,
                evaluation_method="fill_blank_deterministic",
                learner_answer=learner_answer,
                expected_answer=exercise.correct_answer or "",
                error_codes=error_codes,
            )

        # ── 3. Word Order Evaluation ──────────────────────────────────────────
        elif ex_type in ("word_order", "sentence_order", "scramble"):
            is_correct = (norm_answer == norm_expected)
            error_codes = [] if is_correct else ["grammar.word_order.incorrect"]
            return EvaluationResult(
                evaluation_id=eval_id,
                learner_id=learner_id,
                lesson_id=lesson_id,
                exercise_id=exercise.id,
                correct=is_correct,
                score=1.0 if is_correct else 0.0,
                tested_grammar_codes=g_codes,
                tested_vocabulary_items=v_items,
                tested_vocabulary_sense_ids=s_ids,
                target_learning_object_ids=lo_ids,
                evaluation_method="word_order_exact",
                learner_answer=learner_answer,
                expected_answer=exercise.correct_answer or "",
                error_codes=error_codes,
            )

        # ── 4. Open Production (Unsupported for deterministic grading) ─────────
        else:
            return EvaluationResult(
                evaluation_id=eval_id,
                learner_id=learner_id,
                lesson_id=lesson_id,
                exercise_id=exercise.id,
                correct=False,
                score=0.0,
                tested_grammar_codes=g_codes,
                tested_vocabulary_items=v_items,
                tested_vocabulary_sense_ids=s_ids,
                target_learning_object_ids=lo_ids,
                evaluation_method="requires_advanced_evaluation",
                learner_answer=learner_answer,
                expected_answer=exercise.correct_answer or "",
                error_codes=["unsupported_deterministic_evaluation"],
                metadata={"warning": "Deterministic evaluation is not supported for free production tasks"},
            )

    def _normalize_text(self, text: str) -> str:
        if not text:
            return ""
        # Trim whitespace & NFKC normalize
        norm = unicodedata.normalize("NFKC", text.strip())
        return norm.lower()

    def _classify_mcq_error(self, g_codes: List[str], v_items: List[str], s_ids: List[str]) -> List[str]:
        errors = []
        if s_ids:
            errors.append("vocabulary.sense.confusion")
        if v_items:
            errors.append("vocabulary.choice.incorrect")
        if g_codes:
            errors.append(f"grammar.{g_codes[0]}.error")
        if not errors:
            errors.append("general.choice.incorrect")
        return errors
