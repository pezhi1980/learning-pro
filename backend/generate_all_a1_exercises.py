"""
generate_all_a1_exercises.py — Comprehensive AI Content Generation Pipeline
Generates ALL 5 real exercise types for all 20 CEFR A1 grammar topics:
  1. multiple_choice   (5 per topic)
  2. fill_blank        (5 per topic)
  3. sentence_order    (5 per topic)
  4. error_correction  (5 per topic)
  5. translation       (5 per topic)

Total target: 25 distinct exercises per topic = 500 exercises across all 20 A1 topics.
Enforces type-aware quality checks (Filter 1) and cross-type deduplication (Filter 2).
"""

import os
import sys
import asyncio
import logging

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

os.environ["SUPABASE_URL"] = SUPABASE_URL
os.environ["SUPABASE_SERVICE_ROLE_KEY"] = SUPABASE_SERVICE_ROLE_KEY
os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

import importlib.util
from supabase import create_client

script_dir = os.path.dirname(os.path.abspath(__file__))
openai_service_path = os.path.join(script_dir, "services", "openai_service.py")
spec = importlib.util.spec_from_file_location("openai_service", openai_service_path)
openai_service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(openai_service)

A1_GRAMMAR_TOPICS = openai_service.A1_GRAMMAR_TOPICS
EXERCISE_TYPES = openai_service.EXERCISE_TYPES
generate_multiple_choice_exercises = openai_service.generate_multiple_choice_exercises
generate_fill_blank_exercises = openai_service.generate_fill_blank_exercises
generate_sentence_order_exercises = openai_service.generate_sentence_order_exercises
generate_error_correction_exercises = openai_service.generate_error_correction_exercises
generate_translation_exercises = openai_service.generate_translation_exercises
filter1_quality_check = openai_service.filter1_quality_check
filter2_duplicate_check = openai_service.filter2_duplicate_check
extract_comparable_text = openai_service.extract_comparable_text

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# TODO: Increase pool sizes for fill_blank, sentence_order, error_correction, and translation if a similar practice/quiz split is built for them later.
QUESTIONS_PER_TYPE = {
    "multiple_choice": 15,
    "fill_blank": 5,
    "sentence_order": 5,
    "error_correction": 5,
    "translation": 5,
}

GENERATOR_FOR_TYPE = {
    "multiple_choice": generate_multiple_choice_exercises,
    "fill_blank": generate_fill_blank_exercises,
    "sentence_order": generate_sentence_order_exercises,
    "error_correction": generate_error_correction_exercises,
    "translation": generate_translation_exercises,
}


def load_all_existing_texts_for_topic(topic_id: str) -> set[str]:
    """Load core text of all existing exercises for a topic across ALL types for cross-type deduplication."""
    res = sb.table("exercises").select("type", "content_json").eq("topic_id", topic_id).execute()
    texts = set()
    for row in res.data:
        c_json = row.get("content_json") or {}
        ex_type = row.get("type", "multiple_choice")
        text = extract_comparable_text(ex_type, c_json)
        if text:
            texts.add(text)
    return texts


async def main():
    print("=" * 70)
    print("🚀 Starting Comprehensive A1 Exercise Generation (5 Types × 20 Topics)")
    print("=" * 70)

    # 1. Get Language and Level UUIDs
    lang_res = sb.table("languages").select("id").eq("code", "en").single().execute()
    level_res = sb.table("levels").select("id").eq("code", "A1").single().execute()

    lang_uuid = lang_res.data["id"]
    level_uuid = level_res.data["id"]

    total_created = 0

    for index, topic in enumerate(A1_GRAMMAR_TOPICS, 1):
        topic_code = topic["topic_code"]
        order_index = topic["order_index"]

        # Ensure topic row exists in DB
        topic_res = sb.table("grammar_topics").select("id").eq("language_id", lang_uuid).eq("level_id", level_uuid).eq("topic_code", topic_code).maybe_single().execute()
        if not topic_res.data:
            ins = sb.table("grammar_topics").insert({
                "language_id": lang_uuid,
                "level_id": level_uuid,
                "topic_code": topic_code,
                "order_index": order_index,
                "is_published": True
            }).execute()
            topic_id = ins.data[0]["id"]
        else:
            topic_id = topic_res.data["id"]

        # Load all existing exercise texts for this topic across ALL 5 types
        existing_texts = load_all_existing_texts_for_topic(topic_id)
        print(f"\n[{index}/20] Topic '{topic_code}' — Loaded {len(existing_texts)} existing exercise texts across all types.")

        for exercise_type in EXERCISE_TYPES:
            target_count = QUESTIONS_PER_TYPE.get(exercise_type, 5) if isinstance(QUESTIONS_PER_TYPE, dict) else QUESTIONS_PER_TYPE
            # Check existing count for this specific type
            ex_res = sb.table("exercises").select("id").eq("topic_id", topic_id).eq("type", exercise_type).execute()
            existing_count = len(ex_res.data)

            if existing_count >= target_count:
                print(f"  • Type '{exercise_type}' already has {existing_count}/{target_count} questions. Skipping.")
                continue

            needed = target_count - existing_count
            print(f"  • Generating {needed} '{exercise_type}' exercises (currently has {existing_count})...")

            generator = GENERATOR_FOR_TYPE[exercise_type]
            approved_count = 0
            max_attempts = 5
            attempts = 0

            while approved_count < needed and attempts < max_attempts:
                attempts += 1
                batch_count = max(needed - approved_count + 3, 8)
                raw_exercises = await generator(topic_code, "fa", count=batch_count)

                for ex in raw_exercises:
                    if approved_count >= needed:
                        break

                    text = extract_comparable_text(exercise_type, ex)
                    if not text:
                        continue

                    # Filter 1: Quality Validation (type-aware)
                    passed_f1, score, reason = await filter1_quality_check(ex, topic_code, exercise_type)
                    if not passed_f1:
                        print(f"    ❌ Filter 1 ({exercise_type}) Rejected ({score:.2f}): {text[:40]}... Reason: {reason}")
                        continue

                    # Filter 2: Cross-type & within-type Deduplication
                    is_dup, dup_reason = filter2_duplicate_check(text, existing_texts)
                    if is_dup:
                        print(f"    ❌ Filter 2 ({exercise_type}) Rejected (Duplicate): {text[:40]}... Reason: {dup_reason}")
                        continue

                    # Build type-specific content_json matching contract
                    if exercise_type == "multiple_choice":
                        content_json = {
                            "question": ex.get("question", text),
                            "options": ex.get("options", []),
                            "correct_answer": ex.get("correct_answer", ""),
                            "explanation": ex.get("explanation", ""),
                        }
                    elif exercise_type == "fill_blank":
                        content_json = {
                            "sentence": ex.get("sentence", text),
                            "correct_answer": ex.get("correct_answer", ""),
                            "acceptable_answers": ex.get("acceptable_answers", []),
                            "explanation": ex.get("explanation", ""),
                        }
                    elif exercise_type == "sentence_order":
                        content_json = {
                            "target_sentence": ex.get("target_sentence", text),
                            "explanation": ex.get("explanation", ""),
                        }
                    elif exercise_type == "error_correction":
                        content_json = {
                            "incorrect_sentence": ex.get("incorrect_sentence", ""),
                            "correct_sentence": ex.get("correct_sentence", text),
                            "explanation": ex.get("explanation", ""),
                        }
                    elif exercise_type == "translation":
                        content_json = {
                            "source_sentence": ex.get("source_sentence", ""),
                            "target_sentence": ex.get("target_sentence", text),
                            "explanation": ex.get("explanation", ""),
                        }
                    else:
                        content_json = ex

                    sb.table("exercises").insert({
                        "language_id": lang_uuid,
                        "level_id": level_uuid,
                        "topic_id": topic_id,
                        "type": exercise_type,
                        "native_language": "fa",
                        "content_json": content_json,
                        "quality_score": score,
                        "generation_model": "gpt-4o",
                        "is_approved": True,
                    }).execute()

                    existing_texts.add(text)
                    approved_count += 1
                    total_created += 1
                    print(f"    ✅ Saved '{exercise_type}' [{approved_count}/{needed}] (Score: {score:.2f}): {text[:50]}")

                    await asyncio.sleep(0.3)

    print("\n" + "=" * 70)
    print(f"🎉 Pipeline Completed! Created {total_created} new verified exercises across 5 types.")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())
