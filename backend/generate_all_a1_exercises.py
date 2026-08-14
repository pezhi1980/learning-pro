"""
generate_all_a1_exercises.py — Run AI content generation pipeline for all 20 A1 grammar topics.
Follows all 4 project rules:
  1. CEFR A1 standards
  2. 2-Filter System (Filter 1: GPT-4o-mini quality check >= 0.75, Filter 2: deduplication)
  3. 100% Original exercises
  4. Direct storage in Supabase DB (DB caching)
"""

import os
import sys
import asyncio
import uuid
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

from supabase import create_client
from services.openai_service import (
    A1_GRAMMAR_TOPICS,
    generate_grammar_content,
    generate_multiple_choice_exercises,
    filter1_quality_check,
    filter2_duplicate_check,
)

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
QUESTIONS_PER_TOPIC = 5

async def main():
    print("=" * 60)
    print("🚀 Starting A1 Quick Quiz & Practice Generation Pipeline")
    print("=" * 60)

    # 1. Get Language and Level UUIDs
    lang_res = sb.table("languages").select("id").eq("code", "en").single().execute()
    level_res = sb.table("levels").select("id").eq("code", "A1").single().execute()

    lang_uuid = lang_res.data["id"]
    level_uuid = level_res.data["id"]

    # Load existing questions for Filter 2 deduplication
    existing_res = sb.table("exercises").select("content_json").eq("language_id", lang_uuid).eq("level_id", level_uuid).execute()
    existing_questions = {
        row["content_json"].get("question", "")
        for row in existing_res.data
        if row.get("content_json")
    }
    print(f"Loaded {len(existing_questions)} existing questions for deduplication.")

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

        # Check existing exercises count for this topic
        ex_res = sb.table("exercises").select("id").eq("topic_id", topic_id).execute()
        existing_count = len(ex_res.data)

        if existing_count >= QUESTIONS_PER_TOPIC:
            print(f"[{index}/20] Topic '{topic_code}' already has {existing_count} questions. Skipping.")
            continue

        needed = QUESTIONS_PER_TOPIC - existing_count
        print(f"\n[{index}/20] Generating {needed} exercises for topic '{topic_code}' (currently has {existing_count})...")

        # Generate 8 raw candidate questions (with buffer for filters)
        raw_exercises = await generate_multiple_choice_exercises(topic_code, "fa", count=8)
        approved_count = 0

        for ex in raw_exercises:
            if approved_count >= needed:
                break

            q_text = ex.get("question", "")
            if not q_text:
                continue

            # Filter 1: Quality Validation with GPT-4o-mini
            passed_f1, score, reason = await filter1_quality_check(ex, topic_code)
            if not passed_f1:
                print(f"  ❌ Filter 1 Rejected ({score:.2f}): {q_text[:40]}... Reason: {reason}")
                continue

            # Filter 2: Deduplication
            is_dup, dup_reason = filter2_duplicate_check(q_text, existing_questions)
            if is_dup:
                print(f"  ❌ Filter 2 Rejected (Duplicate): {q_text[:40]}... Reason: {dup_reason}")
                continue

            # Passed both filters -> Save to DB
            content_json = {
                "question": q_text,
                "options": ex.get("options", []),
                "correct_answer": ex.get("correct_answer", ""),
                "explanation": ex.get("explanation", ""),
            }

            sb.table("exercises").insert({
                "language_id": lang_uuid,
                "level_id": level_uuid,
                "topic_id": topic_id,
                "type": "multiple_choice",
                "native_language": "fa",
                "content_json": content_json,
                "quality_score": score,
                "generation_model": "gpt-4o",
                "is_approved": True,
            }).execute()

            existing_questions.add(q_text)
            approved_count += 1
            total_created += 1
            print(f"  ✅ Saved [{approved_count}/{needed}] (Score: {score:.2f}): {q_text}")

            await asyncio.sleep(0.3)

    print("\n" + "=" * 60)
    print(f"🎉 Pipeline Completed! Created {total_created} new verified exercises.")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
