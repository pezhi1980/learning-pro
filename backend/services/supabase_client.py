# backend/services/supabase_client.py

import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

_client: Client | None = None


def get_supabase() -> Client:
    global _client
    if _client is None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if not url or not key:
            raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")
        _client = create_client(url, key)
    return _client


async def get_language_uuid(code: str) -> str:
    """Get UUID of a language by its code (e.g., 'en')"""
    sb = get_supabase()
    result = sb.table("languages").select("id").eq("code", code).single().execute()
    return result.data["id"]


async def get_level_uuid(code: str) -> str:
    """Get UUID of a level by its code (e.g., 'A1')"""
    sb = get_supabase()
    result = sb.table("levels").select("id").eq("code", code).single().execute()
    return result.data["id"]


async def topic_exists(language_id: str, level_id: str, topic_code: str) -> bool:
    """Check if a grammar topic already exists"""
    sb = get_supabase()
    result = (
        sb.table("grammar_topics")
        .select("id")
        .eq("language_id", language_id)
        .eq("level_id", level_id)
        .eq("topic_code", topic_code)
        .execute()
    )
    return len(result.data) > 0


async def get_topic_id(language_id: str, level_id: str, topic_code: str) -> str | None:
    """Get UUID of a grammar topic"""
    sb = get_supabase()
    result = (
        sb.table("grammar_topics")
        .select("id")
        .eq("language_id", language_id)
        .eq("level_id", level_id)
        .eq("topic_code", topic_code)
        .execute()
    )
    if result.data:
        return result.data[0]["id"]
    return None


async def insert_grammar_topic(language_id: str, level_id: str, topic_code: str, order_index: int) -> str:
    """Insert a grammar topic and return its UUID"""
    sb = get_supabase()
    result = (
        sb.table("grammar_topics")
        .insert({
            "language_id": language_id,
            "level_id": level_id,
            "topic_code": topic_code,
            "order_index": order_index,
            "is_published": True,
        })
        .execute()
    )
    return result.data[0]["id"]


async def grammar_content_exists(topic_id: str, native_language: str) -> bool:
    """Check if grammar content exists for a topic + native language"""
    sb = get_supabase()
    result = (
        sb.table("grammar_content")
        .select("id")
        .eq("topic_id", topic_id)
        .eq("native_language", native_language)
        .execute()
    )
    return len(result.data) > 0


async def insert_grammar_content(
    topic_id: str,
    native_language: str,
    title: str,
    explanation: str,
    comparison: str = "",
    examples_json: list = None,
    tips_json: list = None,
    common_mistakes_json: list = None,
    generation_model: str = "gpt-4o",
    quality_score: float = 1.0,
) -> str:
    """Insert grammar content and return its UUID"""
    sb = get_supabase()
    result = (
        sb.table("grammar_content")
        .insert({
            "topic_id": topic_id,
            "native_language": native_language,
            "title": title,
            "explanation": explanation,
            "comparison": comparison,
            "examples_json": examples_json or [],
            "tips_json": tips_json or [],
            "common_mistakes_json": common_mistakes_json or [],
            "generation_model": generation_model,
            "quality_score": quality_score,
        })
        .execute()
    )
    return result.data[0]["id"]


async def exercise_question_exists(language_id: str, question: str) -> bool:
    """Check if an exercise with the same question already exists (Filter 2)"""
    sb = get_supabase()
    result = (
        sb.table("exercises")
        .select("id")
        .eq("language_id", language_id)
        .ilike("content_json->>question", question)
        .execute()
    )
    return len(result.data) > 0


async def insert_exercise(
    language_id: str,
    level_id: str,
    topic_id: str,
    native_language: str,
    content_json: dict,
    quality_score: float,
    generation_model: str,
) -> str:
    """Insert an approved exercise and return its UUID"""
    sb = get_supabase()
    result = (
        sb.table("exercises")
        .insert({
            "language_id": language_id,
            "level_id": level_id,
            "topic_id": topic_id,
            "type": "multiple_choice",
            "difficulty": 1,
            "content_json": content_json,
            "native_language": native_language,
            "quality_score": quality_score,
            "is_approved": True,
            "generation_model": generation_model,
        })
        .execute()
    )
    return result.data[0]["id"]


async def log_generation(
    batch_id: str,
    entity_type: str,
    entity_id: str | None,
    language_id: str,
    level_id: str,
    status: str,
    filter1_result: dict | None = None,
    filter2_result: dict | None = None,
    error_message: str | None = None,
):
    """Log content generation activity"""
    sb = get_supabase()
    sb.table("content_generation_log").insert({
        "batch_id": batch_id,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "language_id": language_id,
        "level_id": level_id,
        "status": status,
        "filter1_result_json": filter1_result,
        "filter2_result_json": filter2_result,
        "error_message": error_message,
    }).execute()
