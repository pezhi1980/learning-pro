import json
import os
from dotenv import load_dotenv
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

load_dotenv()

def get_openai_client() -> AsyncOpenAI:
    return AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

client = get_openai_client()

GENERATION_MODEL = "gpt-4o"
FILTER_MODEL = "gpt-4o-mini"

# ── Complete Grammar Content Requirements (Step 1 Contract) ───────────────────
from schemas.grammar_content_schema import (
    GrammarContentSchema,
    GrammarContentRequirements,
    MIN_EXPLANATION_SENTENCES,
    MIN_EXAMPLES_COUNT,
    MIN_TIPS_COUNT,
    MIN_COMMON_MISTAKES_COUNT,
)

GRAMMAR_CONTENT_REQUIREMENTS = GrammarContentRequirements()

# ── 5 Real Exercise Types & Content Contracts ─────────────────────────────────
EXERCISE_TYPES = [
    "multiple_choice",
    "fill_blank",
    "sentence_order",
    "error_correction",
    "translation",
]

EXERCISE_CONTENT_CONTRACTS = {
    "multiple_choice": {
        "question": "str (sentence with blank OR direct question)",
        "options": "list[str] (exactly 4 options)",
        "correct_answer": "str (must match one option exactly)",
        "explanation": "str (why, in learner's native language)",
    },
    "fill_blank": {
        "sentence": "str (sentence with a single ___ blank, no options given)",
        "correct_answer": "str (exact word/phrase that fills the blank)",
        "acceptable_answers": "list[str] (minor valid variants, e.g. contractions)",
        "explanation": "str (why, in learner's native language)",
    },
    "sentence_order": {
        "target_sentence": "str (correct, complete sentence to be reassembled)",
        "explanation": "str (why this word order is correct, in native language)",
    },
    "error_correction": {
        "incorrect_sentence": "str (sentence containing exactly one grammar error)",
        "correct_sentence": "str (the corrected version)",
        "explanation": "str (why it was wrong, in native language)",
    },
    "translation": {
        "source_sentence": "str (sentence in learner's native language)",
        "target_sentence": "str (correct English translation)",
        "explanation": "str (key translation/grammar note, in native language)",
    },
}


# ── A1 Grammar Topics (CEFR standard) ─────────────────────────────────────────
A1_GRAMMAR_TOPICS = [
    {"topic_code": "verb_to_be_present", "order_index": 1},
    {"topic_code": "personal_pronouns", "order_index": 2},
    {"topic_code": "indefinite_articles", "order_index": 3},
    {"topic_code": "definite_article", "order_index": 4},
    {"topic_code": "plural_nouns", "order_index": 5},
    {"topic_code": "possessive_adjectives", "order_index": 6},
    {"topic_code": "demonstratives", "order_index": 7},
    {"topic_code": "present_simple_affirmative", "order_index": 8},
    {"topic_code": "present_simple_negative", "order_index": 9},
    {"topic_code": "present_simple_questions", "order_index": 10},
    {"topic_code": "have_got", "order_index": 11},
    {"topic_code": "can_ability", "order_index": 12},
    {"topic_code": "imperative", "order_index": 13},
    {"topic_code": "there_is_there_are", "order_index": 14},
    {"topic_code": "basic_prepositions_place", "order_index": 15},
    {"topic_code": "adjectives_basic", "order_index": 16},
    {"topic_code": "numbers_and_quantity", "order_index": 17},
    {"topic_code": "wh_questions", "order_index": 18},
    {"topic_code": "object_pronouns", "order_index": 19},
    {"topic_code": "like_and_want", "order_index": 20},
]

# ── A2 Grammar Topics (CEFR standard) ─────────────────────────────────────────
A2_GRAMMAR_TOPICS = [
    {"topic_code": "past_simple_regular", "order_index": 1},
    {"topic_code": "past_simple_irregular", "order_index": 2},
    {"topic_code": "past_continuous", "order_index": 3},
    {"topic_code": "present_continuous_future", "order_index": 4},
    {"topic_code": "comparatives_superlatives", "order_index": 5},
    {"topic_code": "going_to_future", "order_index": 6},
    {"topic_code": "will_future_predictions", "order_index": 7},
    {"topic_code": "present_perfect_simple", "order_index": 8},
    {"topic_code": "modal_verbs_must_should", "order_index": 9},
    {"topic_code": "relative_clauses_basic", "order_index": 10},
    {"topic_code": "adverbs_of_frequency", "order_index": 11},
    {"topic_code": "first_conditional", "order_index": 12},
    {"topic_code": "count_uncount_quantifiers", "order_index": 13},
    {"topic_code": "prepositions_time_movement", "order_index": 14},
    {"topic_code": "question_tags_basic", "order_index": 15},
    {"topic_code": "verb_patterns_infinitive_gerund", "order_index": 16},
    {"topic_code": "possessive_pronouns_mine_yours", "order_index": 17},
    {"topic_code": "reflexive_pronouns", "order_index": 18},
    {"topic_code": "too_and_enough", "order_index": 19},
    {"topic_code": "used_to_past", "order_index": 20},
]

TOPIC_LABELS = {
    "verb_to_be_present": "Verb 'to be' – Present",
    "personal_pronouns": "Personal Pronouns",
    "indefinite_articles": "Indefinite Articles (a / an)",
    "definite_article": "Definite Article (the)",
    "plural_nouns": "Plural Nouns",
    "possessive_adjectives": "Possessive Adjectives",
    "demonstratives": "Demonstratives (this / that / these / those)",
    "present_simple_affirmative": "Present Simple – Affirmative",
    "present_simple_negative": "Present Simple – Negative",
    "present_simple_questions": "Present Simple – Questions",
    "have_got": "Have Got",
    "can_ability": "Can – Ability & Permission",
    "imperative": "Imperative",
    "there_is_there_are": "There is / There are",
    "basic_prepositions_place": "Prepositions of Place",
    "adjectives_basic": "Basic Adjectives",
    "numbers_and_quantity": "Numbers and Quantity",
    "wh_questions": "Wh- Questions",
    "object_pronouns": "Object Pronouns",
    "like_and_want": "Like and Want",

    # A2 Topics
    "past_simple_regular": "Past Simple – Regular Verbs",
    "past_simple_irregular": "Past Simple – Irregular Verbs",
    "past_continuous": "Past Continuous",
    "present_continuous_future": "Present Continuous for Future",
    "comparatives_superlatives": "Comparatives & Superlatives",
    "going_to_future": "Future with 'going to'",
    "will_future_predictions": "Future with 'will'",
    "present_perfect_simple": "Present Perfect Simple",
    "modal_verbs_must_should": "Modals (must, should, have to)",
    "relative_clauses_basic": "Relative Clauses (who, which, where)",
    "adverbs_of_frequency": "Adverbs of Frequency & Manner",
    "first_conditional": "First Conditional",
    "count_uncount_quantifiers": "Countable & Uncountable Nouns",
    "prepositions_time_movement": "Prepositions of Time & Movement",
    "question_tags_basic": "Question Tags",
    "verb_patterns_infinitive_gerund": "Verb Patterns (Gerund / Infinitive)",
    "possessive_pronouns_mine_yours": "Possessive Pronouns (mine, yours)",
    "reflexive_pronouns": "Reflexive Pronouns (myself, yourself)",
    "too_and_enough": "Too and Enough",
    "used_to_past": "Used to (Past Habits)",
}


LEVEL_DEPTH_INSTRUCTIONS = {
    "A1": "Write explanations in simple native-language sentences, avoid grammar-teaching jargon (no 'subjunctive', no 'perfect aspect' terminology) — explain the pattern in plain terms.",
    "A2": "Write explanations in simple native-language sentences, avoid grammar-teaching jargon (no 'subjunctive', no 'perfect aspect' terminology) — explain the pattern in plain terms.",
    "B1": "Explanations may use standard grammar terminology, and must explicitly mention at least one common exception or irregular case for the topic.",
    "B2": "Explanations may use standard grammar terminology, and must explicitly mention at least one common exception or irregular case for the topic.",
    "C1": "Explanations must cover nuance, register (formal vs informal usage), and at least one edge case where the 'simple rule' taught at A1/A2 does not hold.",
    "C2": "Explanations must cover nuance, register (formal vs informal usage), and at least one edge case where the 'simple rule' taught at A1/A2 does not hold.",
}

# ── Grammar Content Generation ─────────────────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_grammar_content(topic_code: str, native_language: str, level_code: str = "A1") -> dict:
    """
    Generate complete grammar explanation, examples, tips and common mistakes
    for a given topic in the user's native language for the given CEFR level.
    """
    topic_label = TOPIC_LABELS.get(topic_code, topic_code.replace("_", " ").title())
    level_key = level_code.upper().strip()
    depth_instruction = LEVEL_DEPTH_INSTRUCTIONS.get(level_key, LEVEL_DEPTH_INSTRUCTIONS["A1"])

    lang_instruction = {
        "fa": "Write the explanation, comparison, tips and common mistakes in Persian (Farsi). Keep target example sentences in English.",
        "da": "Write the explanation, comparison, tips and common mistakes in Danish (Dansk). Keep target example sentences in English.",
        "en": "Write everything in English.",
        "ar": "Write the explanation, comparison, tips and common mistakes in Arabic. Keep target example sentences in English.",
    }.get(native_language, "Write in English.")

    prompt = f"""You are an expert English grammar teacher creating CEFR {level_code} level educational content.

Topic: {topic_label}
CEFR Level: {level_code}
Native Language for Explanations: {native_language}
Instruction: {lang_instruction}
Level Depth Requirement: {depth_instruction}

Create grammar content in the following JSON format ONLY. Return ONLY valid JSON, no other text:

{{
  "title": "<topic title in English>",
  "explanation": "<clear explanation in {native_language} language, MINIMUM 3 sentences (2-4 paragraphs), tailored to {level_code} CEFR complexity>",
  "comparison": "<clear explanation in {native_language} language explaining the exact structural contrast between English grammar and {native_language} grammar for this topic>",
  "examples_json": [
    {{"target": "<English sentence 1>", "native": "<translation in {native_language}>", "breakdown": "<grammar breakdown note in {native_language}>"}},
    {{"target": "<English sentence 2>", "native": "<translation in {native_language}>", "breakdown": "<grammar breakdown note in {native_language}>"}},
    {{"target": "<English sentence 3>", "native": "<translation in {native_language}>", "breakdown": "<grammar breakdown note in {native_language}>"}},
    {{"target": "<English sentence 4>", "native": "<translation in {native_language}>", "breakdown": "<grammar breakdown note in {native_language}>"}},
    {{"target": "<English sentence 5>", "native": "<translation in {native_language}>", "breakdown": "<grammar breakdown note in {native_language}>"}},
    {{"target": "<English sentence 6>", "native": "<translation in {native_language}>", "breakdown": "<grammar breakdown note in {native_language}>"}},
    {{"target": "<English sentence 7>", "native": "<translation in {native_language}>", "breakdown": "<grammar breakdown note in {native_language}>"}},
    {{"target": "<English sentence 8>", "native": "<translation in {native_language}>", "breakdown": "<grammar breakdown note in {native_language}>"}}
  ],
  "tips_json": [
    {{"tip": "<tip 1 in {native_language}>", "example": "<short English example 1>"}},
    {{"tip": "<tip 2 in {native_language}>", "example": "<short English example 2>"}},
    {{"tip": "<tip 3 in {native_language}>", "example": "<short English example 3>"}}
  ],
  "common_mistakes_json": [
    {{"wrong": "<incorrect English 1>", "right": "<correct English 1>", "reason": "<explanation 1 in {native_language}>"}},
    {{"wrong": "<incorrect English 2>", "right": "<correct English 2>", "reason": "<explanation 2 in {native_language}>"}},
    {{"wrong": "<incorrect English 3>", "right": "<correct English 3>", "reason": "<explanation 3 in {native_language}>"}}
  ]
}}

Requirements:
1. Explanation MUST contain at least 3 complete sentences explaining the grammar rules thoroughly for level {level_code}. Depth: {depth_instruction}
2. Comparison MUST be stored in its own field, explaining exact structural differences between English and {native_language}.
3. MUST provide EXACTLY 8 detailed example items in examples_json, each with target, native, and breakdown fields filled.
4. MUST provide MINIMUM 3 distinct items in tips_json; the 3 tips MUST NOT overlap or restate each other.
5. MUST provide MINIMUM 3 distinct items in common_mistakes_json; the 3 common mistakes MUST NOT overlap or restate each other.
6. Do NOT copy from any textbook — create original content.
7. Follow CEFR {level_code} standards exactly.
8. {SCANDINAVIAN_CONTENT_RULE}"""

    ai_client = get_openai_client()
    response = await ai_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    content = json.loads(response.choices[0].message.content)
    return content


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def filter_grammar_content_quality(
    content: dict,
    topic_code: str,
    native_language: str,
    level_code: str = "A1",
) -> tuple[bool, float, str]:
    """
    Quality evaluation for generated grammar content using FILTER_MODEL (gpt-4o-mini).
    Returns (passed, score, reason).
    """
    topic_label = TOPIC_LABELS.get(topic_code, topic_code.replace("_", " ").title())

    prompt = f"""You are a strict English language education quality reviewer.

Review this CEFR {level_code} grammar content for topic '{topic_label}' (Native Language: {native_language}):

Title: {content.get('title')}
Explanation: {content.get('explanation')}
Comparison: {content.get('comparison')}
Examples Count: {len(content.get('examples_json') or [])}
Tips Count: {len(content.get('tips_json') or [])}
Common Mistakes Count: {len(content.get('common_mistakes_json') or [])}

Evaluate on these criteria and return ONLY valid JSON:
{{
  "passed": true/false,
  "score": <float 0.0 to 1.0>,
  "checks": {{
    "explanation_clear_min_3_sentences": true/false,
    "comparison_field_non_empty": true/false,
    "at_least_8_valid_examples": true/false,
    "at_least_3_distinct_tips": true/false,
    "at_least_3_distinct_mistakes": true/false,
    "scandinavian_geography_rule_followed": true/false
  }},
  "reason": "<brief reason if failed, or 'OK' if passed>"
}}

FAIL if ANY of these:
- Explanation is unclear or fewer than 3 complete sentences
- Comparison is empty or merged into explanation
- Fewer than 8 valid examples with target/native/breakdown
- Fewer than 3 tips, or tips overlap/restate each other
- Fewer than 3 common mistakes, or mistakes overlap/restate each other
- Example sentences reference non-Scandinavian countries or cities

PASS threshold: all checks in checks object must be true AND score >= 0.75"""

    ai_client = get_openai_client()
    response = await ai_client.chat.completions.create(
        model=FILTER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    result = json.loads(response.choices[0].message.content)
    passed = result.get("passed", False)
    score = float(result.get("score", 0.0))
    reason = str(result.get("reason", ""))
    return passed, score, reason


SCANDINAVIAN_CONTENT_RULE = """CONTENT RULE: Whenever an example sentence, exercise question, or translation pair references a country, city, or nationality, you MUST choose randomly from this fixed list only — never use any other country or city:
    Countries: Denmark, Sweden, Norway, Finland, Iceland
    Cities: Copenhagen, Aarhus, Odense, Stockholm, Gothenburg, Malmö, Oslo, Bergen, Trondheim, Helsinki, Tampere, Reykjavik
    Nationalities: Danish, Swedish, Norwegian, Finnish, Icelandic
    Do not default to Paris, London, New York, or any other non-Scandinavian location under any circumstances."""


# ── Multiple Choice Exercise Generation ───────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_multiple_choice_exercises(
    topic_code: str,
    native_language: str,
    count: int = 8,
) -> list[dict]:
    """
    Generate multiple choice exercises for a given grammar topic.
    """
    topic_label = TOPIC_LABELS.get(topic_code, topic_code.replace("_", " ").title())

    explanation_lang = {
        "fa": "Persian (Farsi)",
        "da": "Danish (Dansk)",
        "en": "English",
        "ar": "Arabic",
    }.get(native_language, "English")

    prompt = f"""You are an expert English language test designer creating A1 CEFR multiple choice exercises.

Grammar Topic: {topic_label}
Explanation Language: {explanation_lang}

Generate exactly {count} unique multiple choice questions. Return ONLY valid JSON in this format:

{{
  "exercises": [
    {{
      "question": "<complete sentence with a blank OR a direct question about the grammar>",
      "options": ["<option A>", "<option B>", "<option C>", "<option D>"],
      "correct_answer": "<the correct option text, must match exactly one of the options>",
      "explanation": "<brief explanation in {explanation_lang} of why the answer is correct>"
    }}
  ]
}}

STRICT RULES:
1. All questions must test ONLY the topic: {topic_label}
2. Questions must be appropriate for CEFR A1 level (simple vocabulary, short sentences)
3. Each question must have EXACTLY 4 options
4. correct_answer must be an exact copy of one of the 4 options
5. Distractors must be plausible but clearly wrong for someone who understands the grammar
6. No question should repeat similar patterns — make them diverse
7. Do NOT use complex vocabulary — A1 level only
8. Sentences should reflect real everyday situations
9. Do NOT copy from textbooks — create original content
10. {SCANDINAVIAN_CONTENT_RULE}"""

    ai_client = get_openai_client()
    response = await ai_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    data = json.loads(response.choices[0].message.content)
    return data.get("exercises", [])


# ── Fill in the Blank Exercise Generation ──────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_fill_blank_exercises(
    topic_code: str,
    native_language: str,
    count: int = 8,
) -> list[dict]:
    """
    Generate fill-in-the-blank exercises for a given grammar topic.
    """
    topic_label = TOPIC_LABELS.get(topic_code, topic_code.replace("_", " ").title())

    explanation_lang = {
        "fa": "Persian (Farsi)",
        "da": "Danish (Dansk)",
        "en": "English",
        "ar": "Arabic",
    }.get(native_language, "English")

    prompt = f"""You are an expert English language test designer creating A1 CEFR fill-in-the-blank exercises.

Grammar Topic: {topic_label}
Explanation Language: {explanation_lang}

Generate exactly {count} unique fill-in-the-blank questions. Return ONLY valid JSON in this format:

{{
  "exercises": [
    {{
      "sentence": "<sentence containing a single ___ blank, no options provided>",
      "correct_answer": "<the exact word or phrase that correctly fills the blank>",
      "acceptable_answers": ["<minor valid variant e.g. contraction if applicable, otherwise empty list []>"],
      "explanation": "<brief explanation in {explanation_lang} of why this fills the blank>"
    }}
  ]
}}

STRICT RULES:
1. All questions must test ONLY the topic: {topic_label}
2. Questions must be appropriate for CEFR A1 level (simple vocabulary, short sentences)
3. The sentence MUST contain a single '___' blank representing the missing grammar element.
4. correct_answer MUST be the exact word/phrase filling the blank.
5. acceptable_answers MUST contain minor valid variants (e.g. ['don\\'t'] for 'do not') or be an empty list [].
6. No question should repeat similar patterns — make them diverse.
7. Do NOT use complex vocabulary — A1 level only.
8. Sentences should reflect real everyday situations.
9. Do NOT copy from textbooks — create original content.
10. {SCANDINAVIAN_CONTENT_RULE}"""

    ai_client = get_openai_client()
    response = await ai_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    data = json.loads(response.choices[0].message.content)
    return data.get("exercises", [])


# ── Sentence Order Exercise Generation ────────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_sentence_order_exercises(
    topic_code: str,
    native_language: str,
    count: int = 8,
) -> list[dict]:
    """
    Generate sentence ordering exercises for a given grammar topic.
    """
    topic_label = TOPIC_LABELS.get(topic_code, topic_code.replace("_", " ").title())

    explanation_lang = {
        "fa": "Persian (Farsi)",
        "da": "Danish (Dansk)",
        "en": "English",
        "ar": "Arabic",
    }.get(native_language, "English")

    prompt = f"""You are an expert English language test designer creating A1 CEFR sentence ordering exercises.

Grammar Topic: {topic_label}
Explanation Language: {explanation_lang}

Generate exactly {count} unique sentence ordering exercises. Return ONLY valid JSON in this format:

{{
  "exercises": [
    {{
      "target_sentence": "<a complete, grammatically correct English sentence that clearly demonstrates the target word order>",
      "explanation": "<brief explanation in {explanation_lang} of why this word order is correct>"
    }}
  ]
}}

STRICT RULES:
1. All target sentences must test ONLY the word order and structure of topic: {topic_label}
2. Sentences must be appropriate for CEFR A1 level (4 to 8 words long, simple vocabulary).
3. target_sentence MUST be grammatically flawless and natural in English.
4. No sentence should repeat similar patterns — make them diverse.
5. Do NOT copy from textbooks — create original content.
6. {SCANDINAVIAN_CONTENT_RULE}"""

    ai_client = get_openai_client()
    response = await ai_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    data = json.loads(response.choices[0].message.content)
    return data.get("exercises", [])


# ── Error Correction Exercise Generation ──────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_error_correction_exercises(
    topic_code: str,
    native_language: str,
    count: int = 8,
) -> list[dict]:
    """
    Generate error correction exercises for a given grammar topic.
    """
    topic_label = TOPIC_LABELS.get(topic_code, topic_code.replace("_", " ").title())

    explanation_lang = {
        "fa": "Persian (Farsi)",
        "da": "Danish (Dansk)",
        "en": "English",
        "ar": "Arabic",
    }.get(native_language, "English")

    prompt = f"""You are an expert English language test designer creating A1 CEFR error correction exercises.

Grammar Topic: {topic_label}
Explanation Language: {explanation_lang}

Generate exactly {count} unique error correction exercises. Return ONLY valid JSON in this format:

{{
  "exercises": [
    {{
      "incorrect_sentence": "<sentence containing EXACTLY ONE clear grammar error related to {topic_label}>",
      "correct_sentence": "<the exact corrected English sentence>",
      "explanation": "<brief explanation in {explanation_lang} pointing out the specific error and why the correction is right>"
    }}
  ]
}}

STRICT RULES:
1. The error in incorrect_sentence MUST be a GRAMMAR error directly related to: {topic_label}.
2. Do NOT use spelling or punctuation errors — the error MUST be a pedagogical grammar mistake.
3. incorrect_sentence MUST contain EXACTLY ONE error.
4. correct_sentence MUST be the exact, fully corrected English sentence.
5. Sentences must be appropriate for CEFR A1 level (simple vocabulary, short sentences).
6. No exercise should repeat similar patterns — make them diverse.
7. Do NOT copy from textbooks — create original content.
8. {SCANDINAVIAN_CONTENT_RULE}"""

    ai_client = get_openai_client()
    response = await ai_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    data = json.loads(response.choices[0].message.content)
    return data.get("exercises", [])


# ── Translation Exercise Generation ───────────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_translation_exercises(
    topic_code: str,
    native_language: str,
    count: int = 8,
) -> list[dict]:
    """
    Generate translation exercises for a given grammar topic.
    """
    topic_label = TOPIC_LABELS.get(topic_code, topic_code.replace("_", " ").title())

    explanation_lang = {
        "fa": "Persian (Farsi)",
        "da": "Danish (Dansk)",
        "en": "English",
        "ar": "Arabic",
    }.get(native_language, "English")

    prompt = f"""You are an expert English language test designer creating A1 CEFR translation exercises.

Grammar Topic: {topic_label}
Native Language: {explanation_lang}

Generate exactly {count} unique translation exercises. Return ONLY valid JSON in this format:

{{
  "exercises": [
    {{
      "source_sentence": "<sentence in {explanation_lang} to be translated>",
      "target_sentence": "<the accurate English translation demonstrating {topic_label}>",
      "explanation": "<key translation/grammar note in {explanation_lang}>"
    }}
  ]
}}

STRICT RULES:
1. source_sentence MUST be in natural {explanation_lang}.
2. target_sentence MUST be the accurate English translation testing topic: {topic_label}.
3. Sentences must be appropriate for CEFR A1 level (simple vocabulary, short sentences).
4. No exercise should repeat similar patterns — make them diverse.
5. Do NOT copy from textbooks — create original content.
6. {SCANDINAVIAN_CONTENT_RULE}"""

    ai_client = get_openai_client()
    response = await ai_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    data = json.loads(response.choices[0].message.content)
    return data.get("exercises", [])


# ── Filter 1: Quality Validation ──────────────────────────────────────────────

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
async def filter1_quality_check(
    exercise: dict,
    topic_code: str,
    exercise_type: str = "multiple_choice",
) -> tuple[bool, float, str]:
    """
    Filter 1: Validate exercise quality using GPT-4o-mini.
    Returns: (passed, quality_score 0-1, reason)
    Type-aware: evaluates specific criteria per exercise_type.
    """
    topic_label = TOPIC_LABELS.get(topic_code, topic_code)

    if exercise_type == "fill_blank":
        checks_json = """{
    "is_a1_level": true/false,
    "grammar_correct": true/false,
    "correct_answer_valid": true/false,
    "sentence_clear": true/false,
    "blank_unambiguous": true/false
  }"""
        fail_conditions = """- The sentence is too hard for A1 level
- The English grammar is wrong
- The correct_answer doesn't properly fill the blank
- The sentence or blank position is ambiguous or confusing
- The topic being tested is NOT """ + topic_label
        exercise_repr = f"Sentence: {exercise.get('sentence')}\nCorrect Answer: {exercise.get('correct_answer')}\nAcceptable Answers: {exercise.get('acceptable_answers')}\nExplanation: {exercise.get('explanation')}"

    elif exercise_type == "sentence_order":
        checks_json = """{
    "is_a1_level": true/false,
    "grammar_correct": true/false,
    "sentence_natural": true/false,
    "word_order_teaches_topic": true/false
  }"""
        fail_conditions = """- The sentence is too hard for A1 level
- The English grammar or word order is wrong
- The sentence sounds unnatural
- The sentence does NOT effectively teach or test the topic: """ + topic_label
        exercise_repr = f"Target Sentence: {exercise.get('target_sentence')}\nExplanation: {exercise.get('explanation')}"

    elif exercise_type == "error_correction":
        checks_json = """{
    "is_a1_level": true/false,
    "error_is_relevant_to_topic": true/false,
    "exactly_one_error": true/false,
    "correction_is_accurate": true/false
  }"""
        fail_conditions = """- The sentence is too hard for A1 level
- The error is NOT related to the topic: """ + topic_label + """
- There is more than one error, or no clear error at all
- The correction provided is inaccurate or still contains errors
- The error is a minor spelling/punctuation mistake rather than a grammar error"""
        exercise_repr = f"Incorrect Sentence: {exercise.get('incorrect_sentence')}\nCorrect Sentence: {exercise.get('correct_sentence')}\nExplanation: {exercise.get('explanation')}"

    elif exercise_type == "translation":
        checks_json = """{
    "is_a1_level": true/false,
    "translation_accurate": true/false,
    "natural_in_both_languages": true/false
  }"""
        fail_conditions = """- The sentence is too hard for A1 level
- The translation between source and target sentence is inaccurate
- Either the source or target sentence sounds unnatural
- The sentence does NOT test the topic: """ + topic_label
        exercise_repr = f"Source Sentence: {exercise.get('source_sentence')}\nTarget Sentence: {exercise.get('target_sentence')}\nExplanation: {exercise.get('explanation')}"

    else:  # multiple_choice (default)
        checks_json = """{
    "is_a1_level": true/false,
    "grammar_correct": true/false,
    "correct_answer_valid": true/false,
    "question_clear": true/false,
    "distractors_plausible": true/false
  }"""
        fail_conditions = """- The question is too hard for A1 level
- The English grammar in the question or options is wrong
- The correct_answer doesn't match any option exactly
- The question is ambiguous or confusing
- The distractors are obviously wrong (making it too easy)
- The topic being tested is NOT """ + topic_label
        exercise_repr = f"Question: {exercise.get('question')}\nOptions: {exercise.get('options')}\nCorrect Answer: {exercise.get('correct_answer')}\nExplanation: {exercise.get('explanation')}"

    prompt = f"""You are a strict English language education quality reviewer.

Review this A1 CEFR {exercise_type} exercise for the topic: {topic_label}

Exercise Details:
{exercise_repr}

Evaluate on these criteria and return ONLY valid JSON:
{{
  "passed": true/false,
  "score": <float 0.0 to 1.0>,
  "checks": {checks_json},
  "reason": "<brief reason if failed, or 'OK' if passed>"
}}

FAIL if ANY of these:
{fail_conditions}

PASS threshold: all checks in the checks object must be true AND score >= 0.75"""

    ai_client = get_openai_client()
    response = await ai_client.chat.completions.create(
        model=FILTER_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    result = json.loads(response.choices[0].message.content)
    passed = result.get("passed", False)
    score = result.get("score", 0.0)
    reason = result.get("reason", "")
    return passed, score, reason


# ── Helper: Extract Comparable Text for Deduplication ─────────────────────────

def extract_comparable_text(exercise_type: str, exercise: dict) -> str:
    """
    Extract the core comparable sentence from an exercise content dictionary regardless of type.
    - multiple_choice -> question
    - fill_blank -> sentence
    - sentence_order -> target_sentence
    - error_correction -> correct_sentence
    - translation -> target_sentence
    """
    if exercise_type == "multiple_choice":
        return str(exercise.get("question", "")).strip()
    elif exercise_type == "fill_blank":
        return str(exercise.get("sentence", "")).strip()
    elif exercise_type == "sentence_order":
        return str(exercise.get("target_sentence", "")).strip()
    elif exercise_type == "error_correction":
        return str(exercise.get("correct_sentence", "")).strip()
    elif exercise_type == "translation":
        return str(exercise.get("target_sentence", "")).strip()
    else:
        for key in ("question", "sentence", "target_sentence", "correct_sentence"):
            val = exercise.get(key)
            if val and isinstance(val, str) and val.strip():
                return val.strip()
        return str(exercise)


# ── Filter 2: Duplicate Check (text-based) ────────────────────────────────────

def filter2_duplicate_check(text: str, existing_texts: set[str]) -> tuple[bool, str]:
    """
    Filter 2: Check if text is too similar to existing texts in the combined cross-type pool.
    Returns (is_duplicate, reason)
    Uses simple normalized text comparison.
    """
    normalized_new = text.lower().strip().replace("  ", " ")
    if not normalized_new:
        return False, "OK"

    for existing in existing_texts:
        normalized_existing = existing.lower().strip().replace("  ", " ")

        # Exact match
        if normalized_new == normalized_existing:
            return True, f"Exact duplicate: '{existing[:60]}...'"

        # High similarity: if > 80% of words overlap for sentences with > 3 words
        new_words = set(normalized_new.split())
        existing_words = set(normalized_existing.split())
        if len(new_words) > 3 and len(existing_words) > 3:
            overlap = len(new_words & existing_words)
            similarity = overlap / max(len(new_words), len(existing_words))
            if similarity > 0.80:
                return True, f"Too similar to existing item (similarity: {similarity:.0%})"

    return False, "OK"
