"""
seed_all_a1_topics_exercises.py — Seed 5 curated CEFR A1 exercises for all 20 grammar topics in Supabase DB.
Ensures 100% complete coverage for all topics (100 exercises total).
"""

import sys
from supabase import create_client

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import os
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# 20 A1 Grammar Topics Data (5 questions per topic)
EXERCISES_DATA = {
    "verb_to_be_present": [
        {"question": "I ___ a student.", "options": ["am", "is", "are", "be"], "correct_answer": "am", "explanation": "برای ضمیر I از فعل am استفاده می‌کنیم."},
        {"question": "She ___ a doctor.", "options": ["am", "is", "are", "be"], "correct_answer": "is", "explanation": "برای ضمایر مفرد سوم شخص (she, he, it) از is استفاده می‌شود."},
        {"question": "They ___ happy today.", "options": ["am", "is", "are", "be"], "correct_answer": "are", "explanation": "برای ضمایر جمع (they, we, you) از are استفاده می‌کنیم."},
        {"question": "We ___ from Iran.", "options": ["am", "is", "are", "be"], "correct_answer": "are", "explanation": "برای ضمیر we از فعل are استفاده می‌شود."},
        {"question": "He ___ at home now.", "options": ["am", "is", "are", "be"], "correct_answer": "is", "explanation": "برای ضمیر he از فعل is استفاده می‌شود."},
    ],
    "personal_pronouns": [
        {"question": "___ is reading a book. (Sara)", "options": ["She", "He", "They", "It"], "correct_answer": "She", "explanation": "سارا مونث است و ضمیر آن She می‌باشد."},
        {"question": "___ is a fast car.", "options": ["She", "He", "It", "They"], "correct_answer": "It", "explanation": "برای اشیاء و حیوانات از ضمیر It استفاده می‌شود."},
        {"question": "Ali and I are friends. ___ study together.", "options": ["They", "We", "You", "He"], "correct_answer": "We", "explanation": "ترکیب 'Ali and I' به معنی 'ما' (We) است."},
        {"question": "___ are playing football. (The boys)", "options": ["He", "She", "It", "They"], "correct_answer": "They", "explanation": "برای اسم جمع (The boys) از ضمیر They استفاده می‌شود."},
        {"question": "___ am very tired.", "options": ["I", "You", "He", "She"], "correct_answer": "I", "explanation": "فعل am همیشه همراه ضمیر I می‌آید."},
    ],
    "indefinite_articles": [
        {"question": "This is ___ apple.", "options": ["a", "an", "the", "two"], "correct_answer": "an", "explanation": "قبل از کلماتی که با حروف صدادار (a, e, i, o, u) شروع می‌شوند از an استفاده می‌شود."},
        {"question": "I have ___ cat.", "options": ["a", "an", "the", "some"], "correct_answer": "a", "explanation": "قبل از کلمات مفرد با صدای بی‌صدا از a استفاده می‌شود."},
        {"question": "She buys ___ umbrella.", "options": ["a", "an", "the", "many"], "correct_answer": "an", "explanation": "کلمه umbrella با حرف صدادار u شروع می‌شود، پس an می‌گیرد."},
        {"question": "He is ___ teacher.", "options": ["a", "an", "the", "two"], "correct_answer": "a", "explanation": "برای مشاغل مفرد که با صدای بی‌صدا شروع می‌شوند a می‌آوریم."},
        {"question": "It is ___ hour late.", "options": ["a", "an", "the", "this"], "correct_answer": "an", "explanation": "حرف h در hour تلفظ نمی‌شود و با صدای صدادار شروع می‌شود، پس an درست است."},
    ],
    "definite_article": [
        {"question": "Look at ___ sun.", "options": ["a", "an", "the", "some"], "correct_answer": "the", "explanation": "برای پدیده‌های تک و منحصربه‌فرد مثل خورشید از حرف تعریف the استفاده می‌کنیم."},
        {"question": "___ sky is blue today.", "options": ["A", "An", "The", "Some"], "correct_answer": "The", "explanation": "برای آسمان (sky) چون یکتاست از The استفاده می‌شود."},
        {"question": "Open ___ door, please.", "options": ["a", "an", "the", "one"], "correct_answer": "the", "explanation": "وقتی درباره درِ مشخصی صحبت می‌کنیم از the استفاده می‌کنیم."},
        {"question": "___ capital of France is Paris.", "options": ["A", "An", "The", "Any"], "correct_answer": "The", "explanation": "برای واژه‌های مشخص مانند پایتخت یک کشور از The استفاده می‌شود."},
        {"question": "She plays ___ piano very well.", "options": ["a", "an", "the", "some"], "correct_answer": "the", "explanation": "قبل از نام آلات موسیقی معمولاً از the استفاده می‌شود."},
    ],
    "plural_nouns": [
        {"question": "I have two ___.", "options": ["cat", "cats", "cates", "catss"], "correct_answer": "cats", "explanation": "جمع قاعده کلمه cat با اضافه کردن s ساخته می‌شود."},
        {"question": "There are three ___ in the room.", "options": ["child", "childrens", "children", "childs"], "correct_answer": "children", "explanation": "جمع بی‌قاعده کلمه child برابر با children است."},
        {"question": "She washed all the ___.", "options": ["dish", "dishs", "dishes", "dishez"], "correct_answer": "dishes", "explanation": "کلماتی که به sh ختم می‌شوند در جمع es می‌گیرند."},
        {"question": "Look at those ___.", "options": ["man", "men", "mans", "mens"], "correct_answer": "men", "explanation": "جمع بی‌قاعده man برابر با men است."},
        {"question": "I bought three ___.", "options": ["box", "boxs", "boxes", "boxx"], "correct_answer": "boxes", "explanation": "کلماتی که به x ختم می‌شوند با es جمع بسته می‌شوند."},
    ],
    "possessive_adjectives": [
        {"question": "This is Reza. ___ bag is blue.", "options": ["His", "Her", "My", "Their"], "correct_answer": "His", "explanation": "برای صفت مالکیتی مذکر سوم شخص (رضا) از His استفاده می‌شود."},
        {"question": "Mary lost ___ keys.", "options": ["his", "her", "my", "your"], "correct_answer": "her", "explanation": "برای صفت مالکیتی مونث (مری) از her استفاده می‌شود."},
        {"question": "I love ___ family.", "options": ["my", "his", "her", "its"], "correct_answer": "my", "explanation": "صفت مالکیتی مربوط به I برابر با my است."},
        {"question": "The dog is eating ___ food.", "options": ["its", "his", "her", "their"], "correct_answer": "its", "explanation": "برای اشیاء و حیوانات مفرد از صفت مالکیتی its استفاده می‌شود."},
        {"question": "We live here. This is ___ house.", "options": ["our", "their", "your", "my"], "correct_answer": "our", "explanation": "صفت مالکیتی مربوط به We برابر با our است."},
    ],
    "demonstratives": [
        {"question": "___ is my book in my hand.", "options": ["This", "That", "These", "Those"], "correct_answer": "This", "explanation": "برای اشاره به شیء مفرد و نزدیک (در دست) از This استفاده می‌شود."},
        {"question": "___ car over there is very fast.", "options": ["This", "That", "These", "Those"], "correct_answer": "That", "explanation": "برای اشاره به شیء مفرد و دور از That استفاده می‌شود."},
        {"question": "___ shoes here are very comfortable.", "options": ["This", "That", "These", "Those"], "correct_answer": "These", "explanation": "برای اشاره به اشیاء جمع و نزدیک از These استفاده می‌کنیم."},
        {"question": "Look at ___ stars in the sky.", "options": ["this", "that", "these", "those"], "correct_answer": "those", "explanation": "برای اشاره به اشیاء جمع و دور (ستاره‌های آسمان) از those استفاده می‌شود."},
        {"question": "Is ___ your coat over there?", "options": ["this", "that", "these", "those"], "correct_answer": "that", "explanation": "برای مفرد دور (کاپشن آن طرف) از that استفاده می‌شود."},
    ],
    "present_simple_affirmative": [
        {"question": "She ___ English every day.", "options": ["study", "studies", "studys", "studying"], "correct_answer": "studies", "explanation": "در حال ساده برای she فعل s/es می‌گیرد (study -> studies)."},
        {"question": "They ___ in London.", "options": ["live", "lives", "living", "lived"], "correct_answer": "live", "explanation": "برای ضمایر جمع (They) فعل به صورت ساده می‌آید."},
        {"question": "He ___ coffee in the morning.", "options": ["drink", "drinks", "drinking", "drank"], "correct_answer": "drinks", "explanation": "برای he در حال ساده فعل s می‌گیرد."},
        {"question": "I ___ to school by bus.", "options": ["go", "goes", "going", "went"], "correct_answer": "go", "explanation": "برای ضمیر I فعل به شکل ساده می‌آید."},
        {"question": "My father ___ at a hospital.", "options": ["work", "works", "working", "worked"], "correct_answer": "works", "explanation": "پدر (مفرد سوم شخص) نیازمند فعل با پسوند s است."},
    ],
    "present_simple_negative": [
        {"question": "I ___ like cold weather.", "options": ["don't", "doesn't", "not", "am not"], "correct_answer": "don't", "explanation": "منفی حال ساده برای I با don't ساخته می‌شود."},
        {"question": "She ___ speak French.", "options": ["don't", "doesn't", "not", "isn't"], "correct_answer": "doesn't", "explanation": "منفی حال ساده برای she با doesn't ساخته می‌شود."},
        {"question": "They ___ play football on Sundays.", "options": ["don't", "doesn't", "aren't", "not"], "correct_answer": "don't", "explanation": "برای جمع (They) از don't استفاده می‌کنیم."},
        {"question": "He ___ have a car.", "options": ["don't", "doesn't", "isn't", "not"], "correct_answer": "doesn't", "explanation": "منفی حال ساده برای He با doesn't ساخته می‌شود و فعل به شکل پایه می‌آید."},
        {"question": "We ___ work on weekends.", "options": ["don't", "doesn't", "aren't", "not"], "correct_answer": "don't", "explanation": "برای We منفی با don't انجام می‌شود."},
    ],
    "present_simple_questions": [
        {"question": "___ you live in Tehran?", "options": ["Do", "Does", "Are", "Is"], "correct_answer": "Do", "explanation": "برای سوالی کردن حال ساده برای ضمیر you از Do استفاده می‌کنیم."},
        {"question": "___ she like ice cream?", "options": ["Do", "Does", "Is", "Are"], "correct_answer": "Does", "explanation": "برای سوالی کردن حال ساده برای she از Does استفاده می‌شود."},
        {"question": "___ they work here?", "options": ["Do", "Does", "Are", "Is"], "correct_answer": "Do", "explanation": "برای سوالی کردن حال ساده برای They از Do استفاده می‌شود."},
        {"question": "___ he speak English?", "options": ["Do", "Does", "Is", "Are"], "correct_answer": "Does", "explanation": "برای he از آیا (Does) استفاده می‌کنیم."},
        {"question": "Where ___ you live?", "options": ["do", "does", "are", "is"], "correct_answer": "do", "explanation": "در سوالات Wh برای you از do استفاده می‌شود."},
    ],
    "have_got": [
        {"question": "I ___ got a new car.", "options": ["have", "has", "am", "do"], "correct_answer": "have", "explanation": "برای ضمیر I از have got استفاده می‌شود."},
        {"question": "She ___ got two brothers.", "options": ["have", "has", "is", "does"], "correct_answer": "has", "explanation": "برای she از has got استفاده می‌کنیم."},
        {"question": "They ___ got a big house.", "options": ["have", "has", "are", "do"], "correct_answer": "have", "explanation": "برای They از have got استفاده می‌شود."},
        {"question": "He ___ got any money.", "options": ["hasn't", "haven't", "isn't", "doesn't"], "correct_answer": "hasn't", "explanation": "منفی has got برابر با hasn't got است."},
        {"question": "___ you got a pen?", "options": ["Have", "Has", "Do", "Are"], "correct_answer": "Have", "explanation": "سوالی داشتن برای you با Have شروع می‌شود."},
    ],
    "can_ability": [
        {"question": "She ___ speak three languages.", "options": ["can", "cans", "can to", "is can"], "correct_answer": "can", "explanation": "فعل مدال can شکل ثابت دارد و s نمی‌گیرد."},
        {"question": "I ___ swim very well.", "options": ["can", "am can", "can to", "cans"], "correct_answer": "can", "explanation": "بعد از can فعل به صورت مصدر بدون to می‌آید."},
        {"question": "They ___ come to the party tonight.", "options": ["can't", "don't can", "not can", "can't to"], "correct_answer": "can't", "explanation": "منفی توانستن برابر با can't است."},
        {"question": "___ you help me, please?", "options": ["Can", "Do", "Are", "Have"], "correct_answer": "Can", "explanation": "برای درخواست توانستن یا کمک از Can استفاده می‌شود."},
        {"question": "He ___ drive a truck.", "options": ["can't", "doesn't can", "not can", "isn't can"], "correct_answer": "can't", "explanation": "شکل منفی توانستن can't (cannot) است."},
    ],
    "imperative": [
        {"question": "___ the door, please.", "options": ["Open", "Opening", "To open", "Opens"], "correct_answer": "Open", "explanation": "جملات امری با شکل ساده فعل شروع می‌شوند."},
        {"question": "___ make noise! The baby is sleeping.", "options": ["Don't", "Not", "Doesn't", "Aren't"], "correct_answer": "Don't", "explanation": "امری منفی با Don't + فعل ساده ساخته می‌شود."},
        {"question": "___ listen carefully.", "options": ["Please", "To", "Do not to", "Are"], "correct_answer": "Please", "explanation": "برای امری محترمانه از Please در ابتدای جمله استفاده می‌شود."},
        {"question": "___ sit down.", "options": ["Please", "Don't to", "To", "Not"], "correct_answer": "Please", "explanation": "عبارت Please sit down امری محترمانه است."},
        {"question": "___ touch that hot plate!", "options": ["Don't", "Not", "Doesn't", "No"], "correct_answer": "Don't", "explanation": "برای نهی و امری منفی از Don't استفاده می‌شود."},
    ],
    "there_is_there_are": [
        {"question": "___ a book on the table.", "options": ["There is", "There are", "There be", "There have"], "correct_answer": "There is", "explanation": "برای اسم مفرد (a book) از There is استفاده می‌شود."},
        {"question": "___ five apples in the basket.", "options": ["There is", "There are", "There be", "There has"], "correct_answer": "There are", "explanation": "برای اسامی جمع (five apples) از There are استفاده می‌شود."},
        {"question": "___ any milk in the fridge?", "options": ["Is there", "Are there", "There is", "There are"], "correct_answer": "Is there", "explanation": "برای سوالی کردن وجود غیرقابل شمارش یا مفرد از Is there استفاده می‌شود."},
        {"question": "___ many students in the class.", "options": ["There are", "There is", "There be", "Is there"], "correct_answer": "There are", "explanation": "برای اسامی جمع مانند students از There are استفاده می‌شود."},
        {"question": "___ a computer on your desk?", "options": ["Is there", "Are there", "There is", "There be"], "correct_answer": "Is there", "explanation": "برای سوالی از اسم مفرد a computer از Is there استفاده می‌شود."},
    ],
    "basic_prepositions_place": [
        {"question": "The book is ___ the table.", "options": ["on", "in", "at", "underneath"], "correct_answer": "on", "explanation": "برای قرار داشتن روی سطح جسمی از حرف اضافه on استفاده می‌شود."},
        {"question": "The keys are ___ my pocket.", "options": ["in", "on", "at", "above"], "correct_answer": "in", "explanation": "برای قرار داشتن داخل فضای بسته مثل جیب از in استفاده می‌شود."},
        {"question": "She is waiting ___ the bus stop.", "options": ["at", "on", "in", "under"], "correct_answer": "at", "explanation": "برای نقطه‌ای مشخص مثل ایستگاه اتوبوس از حرف اضافه at استفاده می‌شود."},
        {"question": "The cat is sleeping ___ the bed.", "options": ["under", "at", "on top", "in between"], "correct_answer": "under", "explanation": "حرف اضافه under به معنی زیر تخت است."},
        {"question": "He lives ___ Tehran.", "options": ["in", "at", "on", "to"], "correct_answer": "in", "explanation": "قبل از نام شهرها و کشورها از حرف اضافه in استفاده می‌شود."},
    ],
    "adjectives_basic": [
        {"question": "This house is very ___.", "options": ["big", "biggest", "bigger", "bigness"], "correct_answer": "big", "explanation": "صفت ساده big برای توصیف خانه به کار می‌رود."},
        {"question": "She bought a ___ car.", "options": ["new", "newly", "news", "newer"], "correct_answer": "new", "explanation": "صفت قبل از اسم (car) قرار می‌گیرد."},
        {"question": "It is a ___ day today.", "options": ["sunny", "sun", "sunshine", "sunnily"], "correct_answer": "sunny", "explanation": "صفت sunny برای توصیف هوای روز به کار می‌رود."},
        {"question": "He is a ___ boy.", "options": ["smart", "smartly", "smartness", "smarter"], "correct_answer": "smart", "explanation": "صفت ساده smart برای توصیف پسر به کار می‌رود."},
        {"question": "The coffee is very ___.", "options": ["hot", "hotness", "hotly", "hotter"], "correct_answer": "hot", "explanation": "صفت hot برای توصیف دمای قهوه به کار می‌رود."},
    ],
    "numbers_and_quantity": [
        {"question": "I have ___ dollars in my wallet.", "options": ["twenty", "twenties", "twentieth", "twentys"], "correct_answer": "twenty", "explanation": "عدد بیست به انگلیسی به صورت twenty نوشته می‌شود."},
        {"question": "There are ___ days in a week.", "options": ["seven", "seventh", "sevens", "seventeen"], "correct_answer": "seven", "explanation": "تعداد روزهای هفته 7 (seven) است."},
        {"question": "She has ___ apples.", "options": ["many", "much", "little", "any"], "correct_answer": "many", "explanation": "برای اسامی جمع قابل شمارش (apples) از many استفاده می‌شود."},
        {"question": "How ___ water do you drink?", "options": ["much", "many", "few", "number"], "correct_answer": "much", "explanation": "برای اسامی غیرقابل شمارش مثل آب از How much استفاده می‌شود."},
        {"question": "There is ___ sugar in the cup.", "options": ["some", "many", "few", "number"], "correct_answer": "some", "explanation": "برای مقدار مثبت و غیرقابل شمارش (sugar) از some استفاده می‌شود."},
    ],
    "wh_questions": [
        {"question": "___ is your name?", "options": ["What", "Where", "Who", "When"], "correct_answer": "What", "explanation": "برای پرسش اسم شخص از کلمه پرسشی What استفاده می‌شود."},
        {"question": "___ do you live?", "options": ["Where", "What", "Who", "Why"], "correct_answer": "Where", "explanation": "برای پرسش مکان زندگی از کلمه پرسشی Where (کجا) استفاده می‌شود."},
        {"question": "___ is that girl? - She is my sister.", "options": ["Who", "What", "Where", "When"], "correct_answer": "Who", "explanation": "برای پرسش درباره هویت اشخاص از Who (چه کسی) استفاده می‌شود."},
        {"question": "___ do you go to sleep? - At 10 PM.", "options": ["When", "Where", "Who", "What"], "correct_answer": "When", "explanation": "برای پرسش درباره زمان از When (چه زمانی) استفاده می‌شود."},
        {"question": "___ are you happy? - Because it's my birthday!", "options": ["Why", "Where", "Who", "What"], "correct_answer": "Why", "explanation": "برای پرسش دلیل (چرا) از Why استفاده می‌شود."},
    ],
    "object_pronouns": [
        {"question": "Please call ___ tonight.", "options": ["me", "I", "my", "mine"], "correct_answer": "me", "explanation": "پس از فعل call از ضمیر مفعولی me استفاده می‌شود."},
        {"question": "I see ___ every day. (Sara)", "options": ["her", "she", "hers", "his"], "correct_answer": "her", "explanation": "ضمیر مفعولی سوم شخص مفرد مونث (سارا) برابر با her است."},
        {"question": "We know ___. (Reza)", "options": ["him", "he", "his", "himself"], "correct_answer": "him", "explanation": "ضمیر مفعولی برای سوم شخص مذکر (رضا) برابر با him است."},
        {"question": "Give the book to ___.", "options": ["them", "they", "their", "theirs"], "correct_answer": "them", "explanation": "پس از حرف اضافه to از ضمیر مفعولی them استفاده می‌شود."},
        {"question": "Can you hear ___?", "options": ["us", "we", "our", "ours"], "correct_answer": "us", "explanation": "ضمیر مفعولی مربوط به ما برابر با us است."},
    ],
    "like_and_want": [
        {"question": "I ___ to drink some water.", "options": ["want", "likes", "wants", "wanning"], "correct_answer": "want", "explanation": "ساختار want + to + v به معنی خواستن انجام کاری است."},
        {"question": "She ___ ice cream.", "options": ["likes", "like", "wanting", "to like"], "correct_answer": "likes", "explanation": "برای سوم شخص مفرد (she) فعل like به صورت likes می‌آید."},
        {"question": "They ___ to play video games.", "options": ["want", "wants", "likes", "wanting"], "correct_answer": "want", "explanation": "برای They از want ساده بدون s استفاده می‌شود."},
        {"question": "He ___ apples.", "options": ["likes", "like", "want to", "liking"], "correct_answer": "likes", "explanation": "برای He فعل مانند likes پسوند s می‌گیرد."},
        {"question": "Do you ___ a cup of tea?", "options": ["want", "wants", "liked", "wanting"], "correct_answer": "want", "explanation": "در جمله سوالی بعد از Do فعل به شکل ساده (want) می‌آید."},
    ],
}

def seed():
    print("=" * 60)
    print("🌱 Seeding 5 Curated CEFR A1 Exercises for ALL 20 Topics")
    print("=" * 60)

    # 1. Fetch language and level UUIDs
    lang_id = sb.table("languages").select("id").eq("code", "en").single().execute().data["id"]
    level_id = sb.table("levels").select("id").eq("code", "A1").single().execute().data["id"]

    total_inserted = 0

    for topic_code, exercises in EXERCISES_DATA.items():
        # Get topic UUID
        topic_row = sb.table("grammar_topics").select("id").eq("language_id", lang_id).eq("level_id", level_id).eq("topic_code", topic_code).maybe_single().execute()
        if not topic_row.data:
            print(f"❌ Topic {topic_code} not found in DB!")
            continue

        topic_id = topic_row.data["id"]

        # Delete old/partial exercises for clean 5 questions set
        sb.table("exercises").delete().eq("topic_id", topic_id).execute()

        # Insert 5 fresh questions
        for ex in exercises:
            content_json = {
                "question": ex["question"],
                "options": ex["options"],
                "correct_answer": ex["correct_answer"],
                "explanation": ex["explanation"],
            }

            sb.table("exercises").insert({
                "language_id": lang_id,
                "level_id": level_id,
                "topic_id": topic_id,
                "type": "multiple_choice",
                "native_language": "fa",
                "content_json": content_json,
                "quality_score": 0.95,
                "generation_model": "gpt-4o",
                "is_approved": True,
            }).execute()
            total_inserted += 1

        print(f"✅ Topic '{topic_code:28s}': inserted 5 exercises.")

    print("=" * 60)
    print(f"🎉 DONE! Successfully seeded {total_inserted} exercises across all 20 topics.")
    print("=" * 60)

if __name__ == "__main__":
    seed()
