"""
backend/seed_danish_grammar_content.py
Generates Danish (native_language="da") grammar content for A1 topics using backend generation pipeline.
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

import importlib.util
spec = importlib.util.spec_from_file_location("openai_service", os.path.join(os.path.dirname(__file__), "services", "openai_service.py"))
openai_service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(openai_service)

spec_val = importlib.util.spec_from_file_location(
    "grammar_content_validator",
    os.path.join(os.path.dirname(__file__), "validators", "grammar_content_validator.py"),
)
grammar_val_mod = importlib.util.module_from_spec(spec_val)
spec_val.loader.exec_module(grammar_val_mod)
GrammarContentValidator = grammar_val_mod.GrammarContentValidator

A1_GRAMMAR_TOPICS = openai_service.A1_GRAMMAR_TOPICS
TOPIC_LABELS = openai_service.TOPIC_LABELS
generate_grammar_content = openai_service.generate_grammar_content
from supabase import create_client

url = os.getenv('SUPABASE_URL', '')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY', '')
sb = create_client(url, key)

async def generate_danish_content_for_topic(topic_code: str, topic_id: str, topic_label: str):
    logging.info(f"Generating Danish grammar content for topic '{topic_code}'...")
    try:
        content_data = await generate_grammar_content(topic_code, native_language="da")
    except Exception as e:
        logging.error(f"❌ Error generating Danish content for '{topic_code}': {e}")
        return

    content_payload = {
        "topic_id": topic_id,
        "native_language": "da",
        "title": content_data.get("title", topic_label),
        "explanation": content_data.get("explanation", ""),
        "comparison": content_data.get("comparison", ""),
        "examples_json": content_data.get("examples_json", []),
        "tips_json": content_data.get("tips_json", []),
        "common_mistakes_json": content_data.get("common_mistakes_json", []),
        "quality_score": content_data.get("quality_score", 0.9),
        "generation_model": "gpt-4o",
    }

    # Validate before write
    validator = GrammarContentValidator()
    val_result = validator.validate(content_payload)
    if not val_result.passed:
        reasons = "; ".join(issue.message for issue in val_result.issues)
        logging.warning(f"⚠️ Skipped '{topic_code}' (da) — validation failed: {reasons}")
        return

    # Upsert into grammar_content with schema fallback handling
    existing = sb.table("grammar_content").select("id").eq("topic_id", topic_id).eq("native_language", "da").execute()
    try:
        if existing.data and len(existing.data) > 0:
            sb.table("grammar_content").update(content_payload).eq("id", existing.data[0]["id"]).execute()
        else:
            sb.table("grammar_content").insert(content_payload).execute()
    except Exception as db_err:
        if "comparison" in str(db_err):
            payload_fb = dict(content_payload)
            del payload_fb["comparison"]
            if content_data.get("comparison"):
                payload_fb["explanation"] = payload_fb["explanation"] + f"\n\n**Sammenligning med dansk grammatik:**\n{content_data.get('comparison')}"
            if existing.data and len(existing.data) > 0:
                sb.table("grammar_content").update(payload_fb).eq("id", existing.data[0]["id"]).execute()
            else:
                sb.table("grammar_content").insert(payload_fb).execute()
        else:
            raise db_err

    logging.info(f"✅ Saved Danish Grammar Content for '{topic_code}'.")

async def main():
    print("🇩🇰 Starting Danish Content Generation Pipeline...")
    lang_res = sb.table("languages").select("id").eq("code", "en").single().execute()
    level_res = sb.table("levels").select("id").eq("code", "A1").single().execute()

    lang_id = lang_res.data["id"]
    level_id = level_res.data["id"]

    for idx, t in enumerate(A1_GRAMMAR_TOPICS, 1):
        topic_code = t["topic_code"]
        topic_label = TOPIC_LABELS.get(topic_code, topic_code.replace("_", " ").title())
        
        topic_res = sb.table("grammar_topics").select("id").eq("language_id", lang_id).eq("level_id", level_id).eq("topic_code", topic_code).execute()
        if not topic_res.data:
            ins = sb.table("grammar_topics").insert({
                "language_id": lang_id,
                "level_id": level_id,
                "topic_code": topic_code,
                "order_index": t["order_index"],
                "is_published": True
            }).execute()
            topic_id = ins.data[0]["id"]
        else:
            topic_id = topic_res.data[0]["id"]

        await generate_danish_content_for_topic(topic_code, topic_id, topic_label)

if __name__ == "__main__":
    asyncio.run(main())
