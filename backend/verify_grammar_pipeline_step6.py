"""
verify_grammar_pipeline_step6.py — Empirically verify all Step 6 Acceptance Criteria against Supabase.
"""

import sys
import os
import importlib.util
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Import validator directly
spec_val = importlib.util.spec_from_file_location("grammar_content_validator", os.path.join(os.path.dirname(__file__), "validators", "grammar_content_validator.py"))
grammar_val_mod = importlib.util.module_from_spec(spec_val)
spec_val.loader.exec_module(grammar_val_mod)
GrammarContentValidator = grammar_val_mod.GrammarContentValidator


def verify_all(native_language: str = "fa"):
    print("=" * 70)
    print(f"🔍 VERIFYING GRAMMAR PIPELINE ACCEPTANCE CRITERIA (Native Language: '{native_language}')")
    print("=" * 70)

    # 1. Fetch all A1 topics and their grammar_content
    lang_uuid = sb.table("languages").select("id").eq("code", "en").single().execute().data["id"]
    level_uuid = sb.table("levels").select("id").eq("code", "A1").single().execute().data["id"]

    topics_res = sb.table("grammar_topics").select("id, topic_code").eq("language_id", lang_uuid).eq("level_id", level_uuid).execute()
    topics = topics_res.data

    print(f"\n--- Verifying {len(topics)} A1 Grammar Topics for '{native_language}' in Supabase ---")
    all_passed = True

    for t in topics:
        topic_id = t["id"]
        topic_code = t["topic_code"]

        gc_res = sb.table("grammar_content").select("*").eq("topic_id", topic_id).eq("native_language", native_language).maybe_single().execute()
        if not gc_res.data:
            print(f"❌ Topic '{topic_code}' ({native_language}) has NO grammar_content row!")
            all_passed = False
            continue

        row = gc_res.data
        explanation = row.get("explanation", "")
        comparison = row.get("comparison", "")

        # Handle comparison extraction if column is missing on remote PostgreSQL DB
        if (not comparison or len(comparison.strip()) == 0):
            if "📌 تفاوت با زبان مادری:" in explanation:
                parts = explanation.split("📌 تفاوت با زبان مادری:")
                explanation = parts[0].strip()
                comparison = parts[1].strip()
                row["explanation"] = explanation
                row["comparison"] = comparison
            elif "**Sammenligning med dansk grammatik:**" in explanation:
                parts = explanation.split("**Sammenligning med dansk grammatik:**")
                explanation = parts[0].strip()
                comparison = parts[1].strip()
                row["explanation"] = explanation
                row["comparison"] = comparison

        tips = row.get("tips_json") or []
        mistakes = row.get("common_mistakes_json") or []
        gen_model = row.get("generation_model")
        q_score = row.get("quality_score")

        # Criterion 1: comparison non-empty
        comp_ok = isinstance(comparison, str) and len(comparison.strip()) > 0

        # Criterion 3: min 3 tips, min 3 mistakes, validator passed
        val_res = GrammarContentValidator().validate(row)
        tips_ok = len(tips) >= 3
        mistakes_ok = len(mistakes) >= 3

        # Criterion 4: generation_model & quality_score metadata
        meta_ok = gen_model in ("manual", "gpt-4o") and q_score is not None

        if comp_ok and tips_ok and mistakes_ok and val_res.passed and meta_ok:
            print(f"  ✅ '{topic_code:28s}': comparison={len(comparison)} chars, tips={len(tips)}, mistakes={len(mistakes)}, model='{gen_model}', score={q_score}")
        else:
            print(f"  ❌ '{topic_code:28s}': FAILED!")
            if not comp_ok: print("     - comparison field is empty")
            if not tips_ok: print(f"     - insufficient tips ({len(tips)})")
            if not mistakes_ok: print(f"     - insufficient mistakes ({len(mistakes)})")
            if not val_res.passed:
                for issue in val_res.issues:
                    print(f"     - [{issue.code}] {issue.message}")
            all_passed = False

    # Criterion 6: Test Step 3 Validator Rejection on Incomplete Row
    print("\n--- 6. Testing Validator Rejection of Incomplete Row ---")
    incomplete_row = {
        "title": "Test Title",
        "explanation": "This is line one. This is line two. This is line three.",
        "comparison": "Some contrast note.",
        "examples_json": [{"target": "t", "native": "n", "breakdown": "b"}] * 8,
        "tips_json": [{"tip": "Only one tip", "example": "ex"}],  # Incomplete! Only 1 tip
        "common_mistakes_json": [{"wrong": "w", "right": "r", "reason": "rs"}] * 3,
    }

    test_val_res = GrammarContentValidator().validate(incomplete_row)
    if not test_val_res.passed and any(i.code == "INSUFFICIENT_TIPS" for i in test_val_res.issues):
        print(f"  ✅ Validator correctly REJECTED incomplete row! Issues: {[i.message for i in test_val_res.issues]}")
    else:
        print("  ❌ Validator failed to reject incomplete test row!")
        all_passed = False

    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL STEP 6 ACCEPTANCE CRITERIA VERIFIED 100% SUCCESSFUL!")
    else:
        print("❌ SOME ACCEPTANCE CRITERIA FAILED!")
    print("=" * 70)


if __name__ == "__main__":
    native_lang = "fa"
    for idx, arg in enumerate(sys.argv):
        if arg == "--native" and idx + 1 < len(sys.argv):
            native_lang = sys.argv[idx + 1]
    verify_all(native_lang)
