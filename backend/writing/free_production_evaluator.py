# backend/writing/free_production_evaluator.py
"""
ROLE: FREE PRODUCTION EVALUATOR

Evaluates semantically open writing responses.
CORE RULE: Open responses may have multiple valid answers. Never use exact-string mismatch
as automatic proof of incorrectness when the task is semantically open.
"""

from typing import Any, Dict, List, Tuple
from backend.writing.writing_models import WritingSubmission, WritingTaskType


class FreeProductionEvaluator:
    """
    Evaluator for semantically open writing production.
    """

    def evaluate_free_production(self, submission: WritingSubmission) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluates free production text against targets and semantic adequacy without exact string matching.
        """
        text = submission.learner_text.strip()
        clean_words = [w.lower().strip(".,!?;:\"'") for w in text.split()]
        total_words = len(clean_words)

        if total_words == 0:
            return 0.0, {"reason": "Empty submission", "target_matches": []}

        # 1. Check target vocabulary presence
        vocab_matches: List[str] = []
        for v in submission.target_vocabulary_items:
            clean_v = v.lower().strip()
            if clean_v in clean_words or any(clean_v in w for w in clean_words):
                vocab_matches.append(v)

        vocab_score = (
            len(vocab_matches) / max(1, len(submission.target_vocabulary_items))
            if submission.target_vocabulary_items
            else 1.0
        )

        # 2. Check length adequacy per task type
        min_words = 3
        if submission.task_type == WritingTaskType.short_answer:
            min_words = 2
        elif submission.task_type == WritingTaskType.paragraph:
            min_words = 15
        elif submission.task_type == WritingTaskType.extended_writing:
            min_words = 30

        length_ratio = min(1.0, total_words / min_words)

        # 3. Overall score calculation (non-exact)
        score = round(vocab_score * 0.60 + length_ratio * 0.40, 2)

        details = {
            "total_words": total_words,
            "min_words_required": min_words,
            "vocab_matches": vocab_matches,
            "vocab_score": vocab_score,
            "length_ratio": length_ratio,
        }

        return score, details
