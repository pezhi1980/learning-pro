# backend/routers/admin.py

import os
import uuid
import asyncio
import logging
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from services.openai_service import (
    A1_GRAMMAR_TOPICS,
    generate_grammar_content,
    generate_multiple_choice_exercises,
    filter1_quality_check,
    filter2_duplicate_check,
)
from services import supabase_client as db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])

QUESTIONS_PER_TOPIC = 5
GENERATE_EXTRA = 8  # generate more than needed to survive filters


def verify_admin_key(x_admin_key: str = Header(...)):
    expected = os.getenv("ADMIN_SECRET_KEY")
    if not expected or x_admin_key != expected:
        raise HTTPException(status_code=401, detail="Invalid admin key")


# ── Response Models ────────────────────────────────────────────────────────────

class GenerationResult(BaseModel):
    batch_id: str
    language: str
    level: str
    topics_created: int
    topics_skipped: int
    grammar_content_created: int
    exercises_created: int
    exercises_rejected_filter1: int
    exercises_rejected_filter2: int
    details: list[dict]


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.post("/generate/a1/multiple-choice", response_model=GenerationResult)
async def generate_a1_multiple_choice(
    native_language: str = "fa",
    x_admin_key: str = Header(...),
):
    """
    Generate A1 multiple choice exercises for English.
    Pipeline:
      1. Ensure grammar topics exist in DB
      2. Generate grammar content (explanation, examples)
      3. Generate 8 MC exercises per topic
      4. Filter 1: quality check (GPT-4o-mini)
      5. Filter 2: duplicate check (text similarity)
      6. Store first 5 passing exercises per topic
    """
    verify_admin_key(x_admin_key)

    batch_id = str(uuid.uuid4())
    logger.info(f"Starting A1 MC generation batch {batch_id}")

    # Get UUIDs for English and A1
    try:
        lang_uuid = await db.get_language_uuid("en")
        level_uuid = await db.get_level_uuid("A1")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not resolve language/level: {e}")

    topics_created = 0
    topics_skipped = 0
    grammar_content_created = 0
    exercises_created = 0
    rejected_f1 = 0
    rejected_f2 = 0
    details = []

    # Load all existing questions from DB for Filter 2
    try:
        sb = db.get_supabase()
        existing_result = (
            sb.table("exercises")
            .select("content_json")
            .eq("language_id", lang_uuid)
            .eq("level_id", level_uuid)
            .eq("type", "multiple_choice")
            .execute()
        )
        existing_questions: set[str] = {
            row["content_json"].get("question", "")
            for row in existing_result.data
            if row.get("content_json")
        }
        logger.info(f"Loaded {len(existing_questions)} existing questions for deduplication")
    except Exception as e:
        logger.warning(f"Could not load existing questions: {e}")
        existing_questions = set()

    for topic in A1_GRAMMAR_TOPICS:
        topic_code = topic["topic_code"]
        order_index = topic["order_index"]
        topic_detail = {"topic_code": topic_code, "exercises_added": 0, "rejected": 0}

        logger.info(f"Processing topic: {topic_code}")

        # ── Step 1: Ensure topic exists ──────────────────────────────────────
        topic_id = await db.get_topic_id(lang_uuid, level_uuid, topic_code)
        if topic_id is None:
            try:
                topic_id = await db.insert_grammar_topic(
                    lang_uuid, level_uuid, topic_code, order_index
                )
                topics_created += 1
                await db.log_generation(
                    batch_id, "grammar_topic", topic_id,
                    lang_uuid, level_uuid, "approved"
                )
            except Exception as e:
                logger.error(f"Failed to insert topic {topic_code}: {e}")
                topic_detail["error"] = str(e)
                details.append(topic_detail)
                continue
        else:
            topics_skipped += 1

        # ── Step 2: Generate grammar content (if not exists) ─────────────────
        if not await db.grammar_content_exists(topic_id, native_language):
            try:
                content = await generate_grammar_content(topic_code, native_language)
                await db.insert_grammar_content(
                    topic_id=topic_id,
                    native_language=native_language,
                    title=content.get("title", topic_code),
                    explanation=content.get("explanation", ""),
                    comparison=content.get("comparison", ""),
                    examples_json=content.get("examples_json", []),
                    tips_json=content.get("tips_json", []),
                    common_mistakes_json=content.get("common_mistakes_json", []),
                    generation_model="gpt-4o",
                    quality_score=0.9,
                )
                grammar_content_created += 1
                logger.info(f"  Grammar content created for {topic_code}")
            except Exception as e:
                logger.error(f"  Failed grammar content for {topic_code}: {e}")

        # ── Step 3: Generate exercises ────────────────────────────────────────
        try:
            raw_exercises = await generate_multiple_choice_exercises(
                topic_code, native_language, count=GENERATE_EXTRA
            )
        except Exception as e:
            logger.error(f"  Generation failed for {topic_code}: {e}")
            topic_detail["error"] = f"Generation failed: {e}"
            details.append(topic_detail)
            continue

        approved_for_topic = 0

        for exercise in raw_exercises:
            if approved_for_topic >= QUESTIONS_PER_TOPIC:
                break  # We have enough for this topic

            question_text = exercise.get("question", "")

            # ── Filter 1: Quality check ───────────────────────────────────────
            try:
                passed_f1, score, reason = await filter1_quality_check(exercise, topic_code)
            except Exception as e:
                logger.warning(f"  Filter 1 error: {e}")
                passed_f1, score, reason = False, 0.0, str(e)

            if not passed_f1:
                rejected_f1 += 1
                topic_detail["rejected"] = topic_detail.get("rejected", 0) + 1
                await db.log_generation(
                    batch_id, "exercise", None, lang_uuid, level_uuid,
                    "filter1_fail",
                    filter1_result={"passed": False, "score": score, "reason": reason},
                )
                logger.info(f"  ❌ F1 rejected: {question_text[:50]}... ({reason})")
                continue

            # ── Filter 2: Duplicate check ─────────────────────────────────────
            is_duplicate, dup_reason = filter2_duplicate_check(question_text, existing_questions)

            if is_duplicate:
                rejected_f2 += 1
                topic_detail["rejected"] = topic_detail.get("rejected", 0) + 1
                await db.log_generation(
                    batch_id, "exercise", None, lang_uuid, level_uuid,
                    "filter2_fail",
                    filter2_result={"is_duplicate": True, "reason": dup_reason},
                )
                logger.info(f"  ❌ F2 rejected (duplicate): {question_text[:50]}...")
                continue

            # ── Store exercise ────────────────────────────────────────────────
            content_json = {
                "question": question_text,
                "options": exercise.get("options", []),
                "correct_answer": exercise.get("correct_answer", ""),
                "explanation": exercise.get("explanation", ""),
            }

            try:
                exercise_id = await db.insert_exercise(
                    language_id=lang_uuid,
                    level_id=level_uuid,
                    topic_id=topic_id,
                    native_language=native_language,
                    content_json=content_json,
                    quality_score=score,
                    generation_model="gpt-4o",
                )
                existing_questions.add(question_text)  # Update in-memory set
                approved_for_topic += 1
                exercises_created += 1

                await db.log_generation(
                    batch_id, "exercise", exercise_id, lang_uuid, level_uuid,
                    "approved",
                    filter1_result={"passed": True, "score": score},
                    filter2_result={"is_duplicate": False},
                )
                logger.info(f"  ✅ Saved: {question_text[:50]}...")

            except Exception as e:
                logger.error(f"  Failed to insert exercise: {e}")

            # Small delay to avoid OpenAI rate limits
            await asyncio.sleep(0.3)

        topic_detail["exercises_added"] = approved_for_topic
        details.append(topic_detail)
        logger.info(f"  Topic {topic_code}: {approved_for_topic} exercises saved")

        # Small delay between topics
        await asyncio.sleep(1.0)

    logger.info(
        f"Batch {batch_id} complete — "
        f"topics: {topics_created}, exercises: {exercises_created}, "
        f"rejected F1: {rejected_f1}, rejected F2: {rejected_f2}"
    )

    return GenerationResult(
        batch_id=batch_id,
        language="en",
        level="A1",
        topics_created=topics_created,
        topics_skipped=topics_skipped,
        grammar_content_created=grammar_content_created,
        exercises_created=exercises_created,
        exercises_rejected_filter1=rejected_f1,
        exercises_rejected_filter2=rejected_f2,
        details=details,
    )


@router.get("/status")
async def admin_status(x_admin_key: str = Header(...)):
    """Check admin connectivity and DB counts"""
    verify_admin_key(x_admin_key)
    sb = db.get_supabase()

    try:
        lang_uuid = await db.get_language_uuid("en")
        level_uuid = await db.get_level_uuid("A1")

        topics = sb.table("grammar_topics").select("id", count="exact").eq("language_id", lang_uuid).eq("level_id", level_uuid).execute()
        exercises = sb.table("exercises").select("id", count="exact").eq("language_id", lang_uuid).eq("level_id", level_uuid).eq("is_approved", True).execute()

        return {
            "status": "ok",
            "english_language_id": lang_uuid,
            "a1_level_id": level_uuid,
            "a1_grammar_topics": topics.count,
            "a1_approved_exercises": exercises.count,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
