"""
backend/generate_grammar_content_pipeline.py — Master AI Grammar Content Generation Pipeline.

This script is the ONE authoritative pipeline for generating complete, validated grammar explanation
content for ANY CEFR level (A1 through C2).

Usage:
  python generate_grammar_content_pipeline.py --level A2 --native fa
  python generate_grammar_content_pipeline.py --level B1 --topics topic_1,topic_2
"""

import sys
import os
import argparse
import asyncio
import logging
import importlib.util
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("GrammarContentPipeline")

# Import OpenAI service & Validator dynamically to avoid pdfplumber issues
spec_ai = importlib.util.spec_from_file_location("openai_service", os.path.join(os.path.dirname(__file__), "services", "openai_service.py"))
openai_service = importlib.util.module_from_spec(spec_ai)
spec_ai.loader.exec_module(openai_service)

spec_val = importlib.util.spec_from_file_location("grammar_content_validator", os.path.join(os.path.dirname(__file__), "validators", "grammar_content_validator.py"))
grammar_val_mod = importlib.util.module_from_spec(spec_val)
spec_val.loader.exec_module(grammar_val_mod)

GrammarContentValidator = grammar_val_mod.GrammarContentValidator
generate_grammar_content = openai_service.generate_grammar_content
filter_grammar_content_quality = openai_service.filter_grammar_content_quality

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


async def run_pipeline(level_code: str, topic_codes: list[str], native_language: str = "fa"):
    """
    Run the master grammar content generation pipeline for the specified level and topics.
    """
    logger.info("=" * 70)
    logger.info(f"🚀 Master Grammar Content Pipeline for Level '{level_code}' (Native: '{native_language}')")
    logger.info(f"   Topics to process: {len(topic_codes)}")
    logger.info("=" * 70)

    # 1. Resolve language and level UUIDs from Supabase
    lang_res = sb.table("languages").select("id").eq("code", "en").single().execute()
    level_res = sb.table("levels").select("id").eq("code", level_code).maybe_single().execute()

    if not level_res.data:
        # Create level if not exists
        ins_level = sb.table("levels").insert({"code": level_code, "name": f"Level {level_code}"}).execute()
        level_uuid = ins_level.data[0]["id"]
    else:
        level_uuid = level_res.data["id"]

    lang_uuid = lang_res.data["id"]

    validator = GrammarContentValidator()
    success_count = 0
    failure_count = 0

    for idx, topic_code in enumerate(topic_codes, 1):
        logger.info(f"\n[{idx}/{len(topic_codes)}] Processing topic '{topic_code}'...")

        # 2. Ensure topic exists in DB
        topic_row = sb.table("grammar_topics").select("id").eq("language_id", lang_uuid).eq("level_id", level_uuid).eq("topic_code", topic_code).maybe_single().execute()
        if not topic_row.data:
            ins_topic = sb.table("grammar_topics").insert({
                "language_id": lang_uuid,
                "level_id": level_uuid,
                "topic_code": topic_code,
                "title": topic_code.replace("_", " ").title(),
                "is_published": True,
            }).execute()
            topic_id = ins_topic.data[0]["id"]
        else:
            topic_id = topic_row.data["id"]

        # Retry up to 3 times
        generated_ok = False
        for attempt in range(1, 4):
            logger.info(f"  • Attempt {attempt}/3 generating grammar content for '{topic_code}'...")
            try:
                content = await generate_grammar_content(topic_code, native_language, level_code=level_code)

                # Step 3 Validation
                val_result = validator.validate(content)
                if not val_result.passed:
                    logger.warning(f"    ⚠️ Validation failed on attempt {attempt}:")
                    for issue in val_result.issues:
                        logger.warning(f"       - [{issue.code}] {issue.message}")
                    continue

                # Quality Filter (GPT-4o-mini check)
                passed_qual, score, reason = await filter_grammar_content_quality(content, topic_code, native_language, level_code=level_code)
                if not passed_qual:
                    logger.warning(f"    ⚠️ Quality check failed on attempt {attempt} (Score: {score:.2f}, Reason: {reason})")
                    continue

                # Insertion into grammar_content DB table
                payload = {
                    "topic_id": topic_id,
                    "native_language": native_language,
                    "title": content.get("title", topic_code.replace("_", " ").title()),
                    "explanation": content.get("explanation", ""),
                    "comparison": content.get("comparison", ""),
                    "examples_json": content.get("examples_json", []),
                    "tips_json": content.get("tips_json", []),
                    "common_mistakes_json": content.get("common_mistakes_json", []),
                    "generation_model": "gpt-4o",
                    "quality_score": score,
                }

                existing = sb.table("grammar_content").select("id").eq("topic_id", topic_id).eq("native_language", native_language).maybe_single().execute()
                try:
                    if existing and existing.data:
                        sb.table("grammar_content").update(payload).eq("id", existing.data["id"]).execute()
                    else:
                        sb.table("grammar_content").insert(payload).execute()
                except Exception as db_err:
                    if "comparison" in str(db_err):
                        payload_fb = dict(payload)
                        del payload_fb["comparison"]
                        if existing and existing.data:
                            sb.table("grammar_content").update(payload_fb).eq("id", existing.data["id"]).execute()
                        else:
                            sb.table("grammar_content").insert(payload_fb).execute()
                    else:
                        raise db_err

                logger.info(f"  ✅ Successfully generated, validated, and stored '{topic_code}' (Quality Score: {score:.2f})")
                generated_ok = True
                success_count += 1
                break

            except Exception as e:
                logger.error(f"    ❌ Error during attempt {attempt}: {e}")

        if not generated_ok:
            logger.error(f"❌ Failed to generate valid grammar content for '{topic_code}' after 3 retries. Skipping.")
            failure_count += 1

    logger.info("\n" + "=" * 70)
    logger.info(f"🎉 Pipeline Complete for Level '{level_code}': {success_count} succeeded, {failure_count} failed.")
    logger.info("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Master AI Grammar Content Pipeline")
    parser.add_argument("--level", type=str, required=True, help="CEFR Level code (e.g. A1, A2, B1, B2)")
    parser.add_argument("--native", type=str, default="fa", help="Learner native language code (default: fa)")
    parser.add_argument("--topics", type=str, help="Comma-separated topic codes (if not provided, default topics for level will be used)")

    args = parser.parse_args()

    if args.topics:
        topic_list = [t.strip() for t in args.topics.split(",") if t.strip()]
    else:
        # Default topic lists per level
        if args.level.upper() == "A1":
            topic_list = [t["topic_code"] for t in openai_service.A1_GRAMMAR_TOPICS]
        elif args.level.upper() == "A2" and hasattr(openai_service, "A2_GRAMMAR_TOPICS"):
            topic_list = [t["topic_code"] for t in openai_service.A2_GRAMMAR_TOPICS]
        else:
            topic_list = [f"{args.level.lower()}_grammar_topic_{i}" for i in range(1, 6)]

    asyncio.run(run_pipeline(args.level.upper(), topic_list, native_language=args.native))


if __name__ == "__main__":
    main()
