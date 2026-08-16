import sys
import os
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
from supabase import create_client
import importlib.util

spec = importlib.util.spec_from_file_location("openai_service", "services/openai_service.py")
openai_service = importlib.util.module_from_spec(spec)
spec.loader.exec_module(openai_service)

extract_comparable_text = openai_service.extract_comparable_text
filter2_duplicate_check = openai_service.filter2_duplicate_check
EXERCISE_TYPES = openai_service.EXERCISE_TYPES

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def verify():
    print("=" * 60)
    print("🔍 VERIFYING STEP 6 ACCEPTANCE CRITERIA")
    print("=" * 60)

    # 1. Query topic 'verb_to_be_present'
    topic_res = sb.table("grammar_topics").select("id").eq("topic_code", "verb_to_be_present").maybe_single().execute()
    if not topic_res.data:
        print("❌ Topic 'verb_to_be_present' not found in DB.")
        return

    topic_id = topic_res.data["id"]
    ex_res = sb.table("exercises").select("id, type, content_json").eq("topic_id", topic_id).execute()
    rows = ex_res.data

    counts_by_type = {}
    for r in rows:
        t = r.get("type", "unknown")
        counts_by_type[t] = counts_by_type.get(t, 0) + 1

    print("\n--- 1. Exercise Row Counts by Type for 'verb_to_be_present' ---")
    for t in EXERCISE_TYPES:
        print(f"  • {t}: {counts_by_type.get(t, 0)} rows")

    # 2. Check for duplicate core sentences across all types
    print("\n--- 2. Checking Cross-Type Core Sentence Uniqueness ---")
    seen_texts = set()
    duplicates_found = 0

    for r in rows:
        ex_type = r.get("type")
        c_json = r.get("content_json") or {}
        text = extract_comparable_text(ex_type, c_json)
        is_dup, reason = filter2_duplicate_check(text, seen_texts)
        if is_dup:
            print(f"  ❌ Duplicate found! [{ex_type}] '{text}' — Reason: {reason}")
            duplicates_found += 1
        else:
            seen_texts.add(text)

    if duplicates_found == 0:
        print("  ✅ Zero duplicates found across all types! All core sentences are unique.")
    else:
        print(f"  ❌ {duplicates_found} duplicates found.")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    verify()
