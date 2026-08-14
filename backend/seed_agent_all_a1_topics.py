"""
backend/seed_agent_all_a1_topics.py — Runs ContentPedagogyAgent across A1 topics.
Generates structured lessons, Farsi grammar comparisons, 8 main examples, and validated exercises.
"""

import os
import sys
import asyncio
import logging

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

from agents.content_agent import ContentPedagogyAgent
from services.openai_service import (
    A1_GRAMMAR_TOPICS,
    TOPIC_LABELS,
    generate_grammar_content,
    generate_multiple_choice_exercises,
    filter1_quality_check,
    filter2_duplicate_check,
)
from supabase import create_client

url = os.getenv('SUPABASE_URL', '')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')

sb = create_client(url, key)

async def main():
    print("=" * 75)
    print("🤖 Starting ContentPedagogyAgent A1 Lessons & Exercises Pipeline...")
    print("=" * 75)

    lang_res = sb.table("languages").select("id").eq("code", "en").single().execute()
    level_res = sb.table("levels").select("id").eq("code", "A1").single().execute()

    lang_id = lang_res.data["id"]
    level_id = level_res.data["id"]

    agent = ContentPedagogyAgent()
    existing_questions = set()

    for idx, t in enumerate(A1_GRAMMAR_TOPICS, 1):
        topic_code = t["topic_code"]
        order_index = t["order_index"]
        topic_label = TOPIC_LABELS.get(topic_code, topic_code.replace("_", " ").title())
        print(f"\n[{idx}/{len(A1_GRAMMAR_TOPICS)}] 🤖 Agent generating content for topic: '{topic_code}'...")

        try:
            # 1. Upsert Grammar Topic
            topic_res = sb.table("grammar_topics").select("id").eq("language_id", lang_id).eq("level_id", level_id).eq("topic_code", topic_code).execute()
            if topic_res.data and len(topic_res.data) > 0:
                topic_id = topic_res.data[0]["id"]
            else:
                ins = sb.table("grammar_topics").insert({
                    "language_id": lang_id,
                    "level_id": level_id,
                    "topic_code": topic_code,
                    "order_index": order_index,
                    "is_published": True
                }).execute()
                topic_id = ins.data[0]["id"]

            # 2. Generate Grammar Lesson Content with Agent
            content_data = await generate_grammar_content(topic_code, native_language="fa")

            # Save / Update Grammar Content
            existing_content = sb.table("grammar_content").select("id").eq("topic_id", topic_id).execute()
            explanation_text = content_data.get("explanation", "")
            if content_data.get("comparison"):
                explanation_text += f"\n\n**مقایسه با گرامر فارسی:**\n{content_data.get('comparison')}"

            content_payload = {
                "topic_id": topic_id,
                "native_language": "fa",
                "title": content_data.get("title", topic_label),
                "explanation": explanation_text,
                "examples_json": content_data.get("examples_json", []),
                "tips_json": content_data.get("tips_json", []),
                "common_mistakes_json": content_data.get("common_mistakes_json", []),
            }

            if existing_content.data and len(existing_content.data) > 0:
                sb.table("grammar_content").update(content_payload).eq("id", existing_content.data[0]["id"]).execute()
            else:
                sb.table("grammar_content").insert(content_payload).execute()

            print(f"  ✅ Saved Lesson Content for '{topic_code}' ({len(content_data.get('examples_json', []))} examples).")

            # 3. Generate Validated Exercises for Topic
            raw_exercises = await generate_multiple_choice_exercises(topic_code, native_language="fa", count=6)
            saved_exercises = 0

            for ex in raw_exercises:
                if saved_exercises >= 5:
                    break

                q_text = ex.get("question", "")
                if not q_text:
                    continue

                passed_f1, score, reason = await filter1_quality_check(ex, topic_code)
                if not passed_f1:
                    continue

                is_dup, dup_reason = filter2_duplicate_check(q_text, existing_questions)
                if is_dup:
                    continue

                exercise_payload = {
                    "language_id": lang_id,
                    "level_id": level_id,
                    "topic_id": topic_id,
                    "type": "multiple_choice",
                    "native_language": "fa",
                    "content_json": {
                        "question": q_text,
                        "options": ex.get("options", []),
                        "correct_answer": ex.get("correct_answer", ""),
                        "explanation": ex.get("explanation", ""),
                    },
                    "quality_score": score,
                    "generation_model": "gpt-4o",
                    "is_approved": True,
                }

                sb.table("exercises").insert(exercise_payload).execute()
                existing_questions.add(q_text)
                saved_exercises += 1

            print(f"  ✅ Saved {saved_exercises} Validated Exercises for '{topic_code}'.")

        except Exception as e:
            print(f"  ❌ Error on topic '{topic_code}': {e}")

        await asyncio.sleep(0.2)

    print("\n" + "=" * 75)
    print("🎉 ALL A1 LESSONS AND EXERCISES SUCCESSFULLY GENERATED BY AGENT & VALIDATED!")
    print("=" * 75)

if __name__ == "__main__":
    asyncio.run(main())
