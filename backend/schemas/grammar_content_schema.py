"""
backend/schemas/grammar_content_schema.py — Enforced Schema for Complete Grammar Explanation Content.

Single source of truth for what a complete grammar_content row must contain.
Enforced across generator, validators, and database persistence.
"""

import re
from dataclasses import dataclass
from typing import List
from pydantic import BaseModel, Field, field_validator

# ── Min Requirements Constants ────────────────────────────────────────────────
MIN_EXPLANATION_SENTENCES = 3
MIN_EXAMPLES_COUNT = 8
MIN_TIPS_COUNT = 3
MIN_COMMON_MISTAKES_COUNT = 3


class ExampleItemSchema(BaseModel):
    target: str = Field(..., description="Target English sentence")
    native: str = Field(..., description="Translation in learner's native language")
    breakdown: str = Field(..., description="Grammar note/breakdown in learner's native language")


class TipItemSchema(BaseModel):
    tip: str = Field(..., description="Educational tip in learner's native language")
    example: str = Field(..., description="Short English example sentence/phrase illustrating the tip")


class CommonMistakeItemSchema(BaseModel):
    wrong: str = Field(..., description="Incorrect English example")
    right: str = Field(..., description="Correct English sentence")
    reason: str = Field(..., description="Explanation in learner's native language why wrong")


class GrammarContentSchema(BaseModel):
    title: str = Field(..., min_length=1, description="Non-empty topic title in English")
    explanation: str = Field(..., description="Non-empty explanation in learner's native language, min 3 sentences")
    comparison: str = Field(..., description="Non-empty structural contrast with learner's native language")
    examples_json: List[ExampleItemSchema] = Field(..., description="Minimum 8 detailed example items")
    tips_json: List[TipItemSchema] = Field(..., description="Minimum 3 distinct pedagogical tips")
    common_mistakes_json: List[CommonMistakeItemSchema] = Field(..., description="Minimum 3 distinct common mistakes")

    @field_validator("explanation")
    @classmethod
    def validate_explanation_sentences(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Explanation cannot be empty.")
        sentences = [p for p in re.split(r'[.!?۔\n]+', s) if p.strip()]
        if len(sentences) < MIN_EXPLANATION_SENTENCES:
            raise ValueError(f"Explanation must contain at least {MIN_EXPLANATION_SENTENCES} sentences (got {len(sentences)}).")
        return s

    @field_validator("comparison")
    @classmethod
    def validate_comparison_nonempty(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError("Comparison cannot be empty.")
        return s

    @field_validator("examples_json")
    @classmethod
    def validate_examples_count(cls, v: List[ExampleItemSchema]) -> List[ExampleItemSchema]:
        if len(v) < MIN_EXAMPLES_COUNT:
            raise ValueError(f"examples_json must contain at least {MIN_EXAMPLES_COUNT} items (got {len(v)}).")
        return v

    @field_validator("tips_json")
    @classmethod
    def validate_tips_count(cls, v: List[TipItemSchema]) -> List[TipItemSchema]:
        if len(v) < MIN_TIPS_COUNT:
            raise ValueError(f"tips_json must contain at least {MIN_TIPS_COUNT} items (got {len(v)}).")
        return v

    @field_validator("common_mistakes_json")
    @classmethod
    def validate_mistakes_count(cls, v: List[CommonMistakeItemSchema]) -> List[CommonMistakeItemSchema]:
        if len(v) < MIN_COMMON_MISTAKES_COUNT:
            raise ValueError(f"common_mistakes_json must contain at least {MIN_COMMON_MISTAKES_COUNT} items (got {len(v)}).")
        return v


@dataclass
class GrammarContentRequirements:
    min_explanation_sentences: int = MIN_EXPLANATION_SENTENCES
    min_examples: int = MIN_EXAMPLES_COUNT
    min_tips: int = MIN_TIPS_COUNT
    min_common_mistakes: int = MIN_COMMON_MISTAKES_COUNT
    require_separate_comparison: bool = True
