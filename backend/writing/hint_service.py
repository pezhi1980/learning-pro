# backend/writing/hint_service.py
"""
ROLE: PROGRESSIVE HINT SERVICE

Manages progressive hint states:
- hint_1: gentle clue / target list
- hint_2: structural hint
- hint_3: sentence scaffold
- answer_reveal: model answer reveal
Tracks hint usage as evaluation context without invalidating submissions.
"""

from typing import Dict, List, Optional
from backend.writing.writing_models import HintLevel, HintRequest, HintResponse


class ProgressiveHintService:
    """
    Service generating progressive hints and model answer reveals.
    """

    def get_progressive_hint(self, request: HintRequest) -> HintResponse:
        """
        Generates progressive hint text based on requested level and target context.
        """
        level = request.requested_level
        g_targets = ", ".join(request.target_grammar_codes) if request.target_grammar_codes else "general grammar"
        v_targets = ", ".join(request.target_vocabulary_items) if request.target_vocabulary_items else "assigned words"

        if level == HintLevel.hint_1:
            text = f"[Hint 1 - Clue] Remember to include the target elements: {g_targets} and {v_targets}."
            answer_revealed = False
        elif level == HintLevel.hint_2:
            text = f"[Hint 2 - Structure] Pay attention to sentence order: Subject + Verb + Object. Key target: {g_targets}."
            answer_revealed = False
        elif level == HintLevel.hint_3:
            scaffold_vocab = request.target_vocabulary_items[0] if request.target_vocabulary_items else "item"
            text = f"[Hint 3 - Scaffold] Sentence frame: 'The ... [{scaffold_vocab}] is ...'"
            answer_revealed = False
        elif level == HintLevel.answer_reveal:
            model_ans = f"Model Answer: This is an example model sentence incorporating {g_targets} and {v_targets}."
            text = f"[Answer Reveal] {model_ans}"
            answer_revealed = True
        else:
            text = f"[Hint] Review task prompt: {request.prompt}"
            answer_revealed = False

        return HintResponse(
            task_id=request.task_id,
            hint_level=level,
            hint_text=text,
            answer_revealed=answer_revealed,
        )
