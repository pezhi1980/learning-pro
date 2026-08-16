"""
fix_grammar_topic_titles.py — Update grammar_topics table in Supabase so titles are real human-readable topic titles.
"""

import sys
import os
from dotenv import load_dotenv

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

TOPIC_TITLES = {
    "verb_to_be_present": "Verb to Be (Present Tense)",
    "personal_pronouns": "Personal Pronouns",
    "indefinite_articles": "Indefinite Articles (a / an)",
    "definite_article": "Definite Article (the)",
    "plural_nouns": "Plural Nouns (Regular & Irregular)",
    "possessive_adjectives": "Possessive Adjectives",
    "demonstratives": "Demonstratives (this, that, these, those)",
    "present_simple_affirmative": "Present Simple (Affirmative)",
    "present_simple_negative": "Present Simple (Negative)",
    "present_simple_questions": "Present Simple (Questions)",
    "have_got": "Have got / Has got",
    "can_ability": "Modal Verb: Can (Ability)",
    "imperative": "Imperative Sentences",
    "there_is_there_are": "There is / There are",
    "basic_prepositions_place": "Prepositions of Place (in, on, at)",
    "adjectives_basic": "Basic Adjectives & Position",
    "numbers_and_quantity": "Numbers & Quantity (some / any)",
    "wh_questions": "Question Words (Who, What, Where, When, Why)",
    "object_pronouns": "Object Pronouns (me, him, her, us, them)",
    "like_and_want": "Expressing Likes & Desires (like / want)",
}

def update_titles():
    print("Updating topic titles in grammar_topics table...")
    lang_res = sb.table("languages").select("id").eq("code", "en").single().execute()
    level_res = sb.table("levels").select("id").eq("code", "A1").single().execute()

    lang_uuid = lang_res.data["id"]
    level_uuid = level_res.data["id"]

    topics = sb.table("grammar_topics").select("id, topic_code").eq("language_id", lang_uuid).eq("level_id", level_uuid).execute().data

    for idx, t in enumerate(sorted(topics, key=lambda x: x["topic_code"]), 1):
        t_id = t["id"]
        code = t["topic_code"]
        title = TOPIC_TITLES.get(code, code.replace("_", " ").title())

        sb.table("grammar_topics").update({
            "title": title,
            "order_index": idx
        }).eq("id", t_id).execute()
        print(f"  ✅ [{idx:02d}] {code:30s} -> '{title}'")

    print("\n🎉 Topic titles updated successfully in Supabase!")

if __name__ == "__main__":
    update_titles()
