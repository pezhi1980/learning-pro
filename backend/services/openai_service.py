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
}


# ── Grammar Content Generation ─────────────────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_grammar_content(topic_code: str, native_language: str) -> dict:
    """
    Generate grammar explanation, examples, tips and common mistakes
    for a given topic in the user's native language.
    """
    topic_label = TOPIC_LABELS.get(topic_code, topic_code.replace("_", " ").title())

    lang_instruction = {
        "fa": "Write the explanation, comparison, tips and common mistakes in Persian (Farsi). Keep target example sentences in English.",
        "da": "Write the explanation, comparison, tips and common mistakes in Danish (Dansk). Keep target example sentences in English.",
        "en": "Write everything in English.",
        "ar": "Write the explanation, comparison, tips and common mistakes in Arabic. Keep target example sentences in English.",
    }.get(native_language, "Write in English.")

    prompt = f"""You are an expert English grammar teacher creating A1-A2 CEFR level content.

Topic: {topic_label}
Native Language for Explanations: {native_language}
Instruction: {lang_instruction}

Create grammar content in the following JSON format ONLY. Return ONLY valid JSON, no other text:

{{
  "title": "<topic title in English>",
  "explanation": "<clear explanation in {native_language} language, 2-4 paragraphs, A1-A2 level>",
  "comparison": "<clear explanation in {native_language} language explaining the structural difference between English grammar and {native_language} grammar for this topic>",
  "examples_json": [
    {{"target": "<English sentence 1>", "native": "<translation in {native_language}>", "breakdown": "<grammar breakdown note in {native_language} explaining native language difference>"}},
    {{"target": "<English sentence 2>", "native": "<translation in {native_language}>", "breakdown": "<grammar breakdown note in {native_language} explaining native language difference>"}},
    {{"target": "<English sentence 3>", "native": "<translation in {native_language}>", "breakdown": "<grammar breakdown note in {native_language}>"}}
  ],
  "tips_json": [
    {{"tip": "<important tip in {native_language}>", "example": "<short English example>"}}
  ],
  "common_mistakes_json": [
    {{"wrong": "<incorrect English>", "right": "<correct English>", "reason": "<explanation in {native_language}>"}}
  ]
}}

Requirements:
- Explanation and comparison must be clear for a beginner learner
- Comparison must highlight exact structural differences between English and {native_language} (e.g. word order, verb position, articles)
- Provide at least 2 clear examples illustrating the native language contrast in breakdown
- Do NOT copy from any textbook — create original content
- Follow CEFR standards exactly
- CONTENT RULE: Whenever an example sentence, exercise question, or translation pair references a country, city, or nationality, you MUST choose randomly from this fixed list only — never use any other country or city:
  Countries: Denmark, Sweden, Norway, Finland, Iceland
  Cities: Copenhagen, Aarhus, Odense, Stockholm, Gothenburg, Malmö, Oslo, Bergen, Trondheim, Helsinki, Tampere, Reykjavik
  Nationalities: Danish, Swedish, Norwegian, Finnish, Icelandic
  Do not default to Paris, London, New York, or any other non-Scandinavian location under any circumstances."""

    ai_client = get_openai_client()
    response = await ai_client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.7,
    )

    content = json.loads(response.choices[0].message.content)
    return content


# ── Multiple Choice Exercise Generation ───────────────────────────────────────

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def generate_multiple_choice_exercises(
    topic_code: str,
    native_language: str,
    count: int = 8,
) -> list[dict]:
    """
    Generate multiple choice exercises for a given grammar topic.
    Generates more than needed (count=8) to have buffer after filtering.
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
10. CONTENT RULE: Whenever an example sentence, exercise question, or translation pair references a country, city, or nationality, you MUST choose randomly from this fixed list only — never use any other country or city:
    Countries: Denmark, Sweden, Norway, Finland, Iceland
    Cities: Copenhagen, Aarhus, Odense, Stockholm, Gothenburg, Malmö, Oslo, Bergen, Trondheim, Helsinki, Tampere, Reykjavik
    Nationalities: Danish, Swedish, Norwegian, Finnish, Icelandic
    Do not default to Paris, London, New York, or any other non-Scandinavian location under any circumstances."""

    response = await client.chat.completions.create(
        model=GENERATION_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0.8,
    )

    data = json.loads(response.choices[0].message.content)
    return data.get("exercises", [])


# ── Filter 1: Quality Validation ──────────────────────────────────────────────

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=1, max=5))
async def filter1_quality_check(exercise: dict, topic_code: str) -> tuple[bool, float, str]:
    """
    Filter 1: Validate exercise quality using GPT-4o-mini.
    Returns: (passed, quality_score 0-1, reason)
    """
    topic_label = TOPIC_LABELS.get(topic_code, topic_code)

    prompt = f"""You are a strict English language education quality reviewer.

Review this A1 CEFR multiple choice exercise for the topic: {topic_label}

Exercise:
Question: {exercise.get('question')}
Options: {exercise.get('options')}
Correct Answer: {exercise.get('correct_answer')}
Explanation: {exercise.get('explanation')}

Evaluate on these criteria and return ONLY valid JSON:
{{
  "passed": true/false,
  "score": <float 0.0 to 1.0>,
  "checks": {{
    "is_a1_level": true/false,
    "grammar_correct": true/false,
    "correct_answer_valid": true/false,
    "question_clear": true/false,
    "distractors_plausible": true/false
  }},
  "reason": "<brief reason if failed, or 'OK' if passed>"
}}

FAIL if ANY of these:
- The question is too hard for A1 level
- The English grammar in the question or options is wrong
- The correct_answer doesn't match any option exactly
- The question is ambiguous or confusing
- The distractors are obviously wrong (making it too easy)
- The topic being tested is NOT {topic_label}

PASS threshold: all 5 checks must be true AND score >= 0.75"""

    response = await client.chat.completions.create(
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


# ── Filter 2: Duplicate Check (text-based) ────────────────────────────────────

def filter2_duplicate_check(question: str, existing_questions: set[str]) -> tuple[bool, str]:
    """
    Filter 2: Check if question is too similar to existing ones.
    Returns (is_duplicate, reason)
    Uses simple normalized text comparison.
    """
    normalized_new = question.lower().strip().replace("  ", " ")

    for existing in existing_questions:
        normalized_existing = existing.lower().strip().replace("  ", " ")

        # Exact match
        if normalized_new == normalized_existing:
            return True, f"Exact duplicate: '{existing[:60]}...'"

        # High similarity: if > 80% of words overlap
        new_words = set(normalized_new.split())
        existing_words = set(normalized_existing.split())
        if len(new_words) > 3 and len(existing_words) > 3:
            overlap = len(new_words & existing_words)
            similarity = overlap / max(len(new_words), len(existing_words))
            if similarity > 0.80:
                return True, f"Too similar to existing question (similarity: {similarity:.0%})"

    return False, "OK"
