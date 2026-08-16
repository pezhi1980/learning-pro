"""
backend/agents/content_agent.py — Polyglot Master Pedagogy Content Agent
Dedicated AI Agent for generating structured, high-quality lessons and exercises across all target languages.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple
try:
    from openai import AsyncOpenAI
except ImportError:
    AsyncOpenAI = None

try:
    from supabase import create_client, Client
except ImportError:
    create_client = None
    Client = None

from backend.schemas import (
    AgentInput,
    AgentOutput,
    BackendError,
    ErrorDetail,
    ErrorType,
)

logger = logging.getLogger(__name__)

# ==============================================================================
# Master System Instruction
# Constrains AI behavior to source-bound, non-inventive content generation.
# ==============================================================================
DEFAULT_SYSTEM_INSTRUCTION = """ROLE: CONTENT GENERATION AGENT

This module is responsible only for generating educational language-learning content.

It must receive explicit curriculum targets from the Backend and generate content only for those targets.

It must never decide what curriculum should be taught.

CORE RULES:

1. Backend determines WHAT to teach.
2. Agent determines HOW to present the assigned content.
3. Every assigned target is mandatory.
4. Never omit an assigned target.
5. Never replace an assigned target.
6. Never postpone an assigned target.
7. Never decide that an assigned target is unnecessary.
8. Never change the curriculum level of an assigned target.
9. Never invent Grammar Codes.
10. Never invent Vocabulary targets.
11. Never invent Vocabulary Senses.
12. Never expand a lexeme into unassigned meanings.
13. Never add related curriculum merely because it is pedagogically useful.
14. Never expand a broad Grammar label into unrelated advanced usages unless explicitly assigned.
15. Use source-provided curriculum information as authoritative.
16. General model knowledge may be used only to:
    - explain assigned content
    - produce natural examples
    - produce original exercises
    - produce translations
    - produce breakdowns
    - ensure linguistic naturalness
    - clarify the assigned concept
17. General model knowledge must never redefine the curriculum.
18. Supporting language may appear in examples.
19. Supporting language must not be presented as a new educational target unless assigned.
20. Exercises must intentionally test assigned targets only.
21. Output must match AgentOutput exactly.
22. Every ExplanationBlock must include TargetTrace.
23. Every ExampleItem must include TargetTrace.
24. Every ExerciseItem must include TargetTrace.
25. Coverage declarations must refer only to assigned learning_object_id values.
26. Do not output: valid=true, approved=true, source_verified=true, curriculum_verified=true.
27. Backend validation is authoritative.
28. If required source/assignment information is insufficient, return controlled generation failure.
29. Generated examples and exercises must be original.
30. Language must be natural, clear, and appropriate for the assigned teaching task.
31. Grammar lesson examples should avoid unnecessarily difficult vocabulary.
32. Vocabulary lesson examples should avoid unnecessarily complex unassigned grammar.
33. Grammar complexity and Vocabulary complexity must remain independently controllable.
34. Never claim source facts that were not supplied by Backend.
35. Never pretend to have read a PDF unless source information was explicitly supplied in AgentInput/context.

36. Whenever an example sentence, exercise question, or translation pair references a country, city, or nationality, you MUST choose randomly from this fixed list only — never use any other country or city:
    - Countries: Denmark, Sweden, Norway, Finland, Iceland
    - Cities: Copenhagen, Aarhus, Odense, Stockholm, Gothenburg, Malmö, Oslo, Bergen, Trondheim, Helsinki, Tampere, Reykjavik
    - Nationalities: Danish, Swedish, Norwegian, Finnish, Icelandic
    Do not default to Paris, London, New York, or any other non-Scandinavian location under any circumstances.

MASTER PRINCIPLE:
SOURCE DEFINES WHAT EXISTS.
BACKEND DEFINES WHAT IS ASSIGNED.
AGENT GENERATES HOW IT IS TAUGHT.
BACKEND VALIDATES THE RESULT.
"""


class ContentPedagogyAgent:
    """
    Dedicated Content Generation Agent conforming to AgentInput -> AgentOutput contract.
    """

    def __init__(
        self,
        system_instruction: str = DEFAULT_SYSTEM_INSTRUCTION,
        openai_api_key: Optional[str] = None,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
    ):
        self.system_instruction = system_instruction
        self.api_key = openai_api_key or os.getenv("OPENAI_API_KEY")
        self.supabase_url = supabase_url or os.getenv("SUPABASE_URL")
        self.supabase_key = supabase_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY")

        self.client = AsyncOpenAI(api_key=self.api_key) if (AsyncOpenAI and self.api_key) else None
        self.sb = create_client(self.supabase_url, self.supabase_key) if (create_client and self.supabase_url and self.supabase_key) else None


    def set_system_instruction(self, custom_instruction: str):
        self.system_instruction = custom_instruction

    # ── Canonical Contract-Bound Generation ───────────────────────────────────
    async def generate(self, agent_input: AgentInput) -> AgentOutput:
        """
        Primary contract method: Accepts AgentInput and returns structured AgentOutput.
        Must NOT decide its own curriculum targets.
        """
        prompt = self._build_prompt_from_input(agent_input)

        try:
            response = await self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": self.system_instruction},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.3,
            )

            raw_content = response.choices[0].message.content
            if not raw_content:
                raise ValueError("AI returned an empty content string")

            data = json.loads(raw_content)
            # Ensure request_id matches
            data["request_id"] = agent_input.request_id
            data["generation_mode"] = agent_input.generation_mode.value

            return AgentOutput(**data)

        except Exception as e:
            logger.error(f"Agent generation failed for request {agent_input.request_id}: {e}")
            raise RuntimeError(f"Agent generation failed for request {agent_input.request_id}: {e}")


    def _build_prompt_from_input(self, agent_input: AgentInput) -> str:
        grammar_str = "\n".join([
            f"- ID: {g.learning_object_id} | Code: {g.grammar_code} | Label: {g.label} | Level: {g.source.level}"
            for g in agent_input.target_grammar
        ]) or "None"

        vocab_str = "\n".join([
            f"- ID: {v.learning_object_id} | Item: {v.item} | POS: {v.part_of_speech} | Senses: {[s.guideword for s in v.senses if s.guideword]}"
            for v in agent_input.target_vocabulary
        ]) or "None"

        return f"""
REQUEST ID: {agent_input.request_id}
GENERATION MODE: {agent_input.generation_mode.value}
TARGET LANGUAGE: {agent_input.target_language}
NATIVE LANGUAGE: {agent_input.native_language or 'English'}
TASK DIFFICULTY: {agent_input.task_difficulty.value}

ASSIGNED TARGET GRAMMAR:
{grammar_str}

ALLOWED SUPPORTING GRAMMAR CODES:
{', '.join(agent_input.allowed_grammar_codes) or 'None'}

ASSIGNED TARGET VOCABULARY:
{vocab_str}

ALLOWED SUPPORTING VOCABULARY ITEMS:
{', '.join(agent_input.allowed_vocabulary_items) or 'None'}

ALLOWED SUPPORTING VOCABULARY SENSES:
{', '.join(agent_input.allowed_vocabulary_sense_ids) or 'None'}

Generate structured JSON matching AgentOutput schema:
{{
  "request_id": "{agent_input.request_id}",
  "generation_mode": "{agent_input.generation_mode.value}",
  "title": "<Lesson Title>",
  "explanations": [
    {{
      "id": "exp_1",
      "title": "<Explanation Title>",
      "content": "<Explanation content in native language>",
      "targets": {{
        "learning_object_id": "<target_id>",
        "grammar_codes": ["<code1>"],
        "vocabulary_items": ["<item1>"],
        "vocabulary_sense_ids": []
      }}
    }}
  ],
  "examples": [
    {{
      "id": "ex_1",
      "sentence": "<Example sentence in target language>",
      "translation": "<Translation in native language>",
      "breakdown": "<Grammar breakdown>",
      "targets": {{
        "learning_object_id": "<target_id>",
        "grammar_codes": ["<code1>"],
        "vocabulary_items": ["<item1>"],
        "vocabulary_sense_ids": []
      }}
    }}
  ],
  "exercises": [
    {{
      "id": "ex_item_1",
      "exercise_type": "multiple_choice",
      "prompt": "<Question prompt>",
      "options": ["<Opt A>", "<Opt B>", "<Opt C>", "<Opt D>"],
      "correct_answer": "<Exact matching correct option>",
      "explanation": "<Pedagogical explanation>",
      "targets": {{
        "learning_object_id": "<target_id>",
        "grammar_codes": ["<code1>"],
        "vocabulary_items": ["<item1>"],
        "vocabulary_sense_ids": []
      }}
    }}
  ],
  "coverage": [
    {{
      "learning_object_id": "<target_id>",
      "explained": true,
      "example_covered": true,
      "exercise_covered": true
    }}
  ]
}}
"""

    # ── Legacy/Backward Compatibility Methods ─────────────────────────────────
    async def generate_curriculum_topics(self, target_language: str, native_language: str, level: str) -> List[Dict[str, Any]]:
        prompt = f"Target Language: {target_language}\nLearner Native: {native_language}\nLevel: {level}\nReturn JSON with 'topics'."
        res = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": self.system_instruction}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.3,
        )
        return json.loads(res.choices[0].message.content).get("topics", [])

    async def generate_lesson(self, target_language: str, native_language: str, level: str, topic_code: str) -> Dict[str, Any]:
        prompt = f"Generate lesson JSON for {topic_code} level {level}."
        res = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": self.system_instruction}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        return json.loads(res.choices[0].message.content)

    async def generate_exercises(self, target_language: str, native_language: str, level: str, topic_code: str, count: int = 5) -> List[Dict[str, Any]]:
        prompt = f"Generate {count} exercises JSON for {topic_code}."
        res = await self.client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "system", "content": self.system_instruction}, {"role": "user", "content": prompt}],
            response_format={"type": "json_object"},
            temperature=0.7,
        )
        return json.loads(res.choices[0].message.content).get("exercises", [])
