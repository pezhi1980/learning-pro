"""
seed_all_a1_grammar_content_8_examples.py — Seed complete grammar content with 8 examples per topic
and Persian grammar comparison section for all 20 A1 topics in Supabase DB.
"""

import sys
from supabase import create_client

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import os
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# 20 Topics data with 8 examples each and Persian Grammar Comparison
A1_CONTENT_DATA = {
    "verb_to_be_present": {
        "title": "Verb 'to be' – Present",
        "explanation": "فعل 'to be' در زبان انگلیسی به معنای 'بودن' است و در زمان حال به شکل‌های am, is, و are استفاده می‌شود. این فعل برای بیان هویت، ویژگی، سن، شغل و حالت روحی اشخاص و اشیاء به کار می‌رود.",
        "comparison": "در زبان فارسی افعال بودن (هستم، هستی، است، هستیم، هستید، هستند) در آخر جمله می‌آیند، اما در انگلیسی فعل 'to be' بلافاصله بعد از فاعل (در ابتدای جمله) قرار می‌گیرد. همچنین برخلاف فارسی، در انگلیسی قبل از بیان **مشاغل و نقش افراد** حتماً باید از حرف تعریف a یا an استفاده شود (مثلاً She is a teacher یعنی او معلم است).",
        "examples_json": [
            {"target": "I am a student.", "native": "من یک دانش‌آموز هستم.", "breakdown": "فعل am با ضمیر I می‌آید. حرف a قبل از شغل/نقش (student) اجباری است."},
            {"target": "She is a teacher.", "native": "او یک معلم است.", "breakdown": "فعل is با ضمیر she می‌آید. حرف a قبل از عنوان شغل (teacher) الزامی است."},
            {"target": "They are happy.", "native": "آن‌ها خوشحال هستند.", "breakdown": "are با ضمیر جمع they استفاده می‌شود."},
            {"target": "He is my brother.", "native": "او برادر من است.", "breakdown": "فعل is با he می‌آید (چون صفت مالکیتی my داریم نیازی به a نیست)."},
            {"target": "We are in the classroom.", "native": "ما در کلاس درس هستیم.", "breakdown": "are همراه we برای موقعیت مکانی بکار می‌رود."},
            {"target": "It is a beautiful cat.", "native": "این یک گربه زیبا است.", "breakdown": "it برای حیوانات و اشیاء مفرد است و a قبل از صفت/اسم مفرد می‌آید."},
            {"target": "You are very kind.", "native": "تو بسیار مهربان هستی.", "breakdown": "you هم برای مفرد و هم جمع are می‌گیرد."},
            {"target": "The coffee is hot.", "native": "قهوه داغ است.", "breakdown": "اسم مفرد (The coffee) فعل is می‌گیرد."},
        ],
        "tips_json": [
            {"tip": "در انگلیسی قبل از بیان مشاغل (معلم، پزشک، مهندس و ...) حتماً باید a یا an استفاده شود.", "example": "She is a teacher. / He is an engineer."}
        ],
        "common_mistakes_json": [
            {"wrong": "She is teacher.", "right": "She is a teacher.", "reason": "در انگلیسی قبل از نام مشاغل مفرد آوردن a یا an اجباری است."}
        ]
    },
    "personal_pronouns": {
        "title": "Personal Pronouns",
        "explanation": "ضمایر فاعلی کلماتی هستند که جانشین اسم می‌شوند تا از تکرار آن در جمله جلوگیری کنند. ضمایر فاعلی انگلیسی عبارتند از: I, You, He, She, It, We, They.",
        "comparison": "در فارسی ضمایر فاعلی (من، تو، او، ما، شما، آن‌ها) اغلب از جمله حذف می‌شوند چون شناسه فعل شخص را نشان می‌دهد. اما در انگلیسی آوردن ضمیر فاعلی الزامی است.",
        "examples_json": [
            {"target": "I live in Tehran.", "native": "من در تهران زندگی می‌کنم.", "breakdown": "I ضمیر متکلم مفرد (من) است."},
            {"target": "You are my best friend.", "native": "تو بهترین دوست من هستی.", "breakdown": "You برای تو و شما استفاده می‌شود."},
            {"target": "He works at a hospital.", "native": "او در بیمارستان کار می‌کند.", "breakdown": "He برای مذکر مفرد استفاده می‌شود."},
            {"target": "She speaks English well.", "native": "او انگلیسی را خوب صحبت می‌کند.", "breakdown": "She برای مونث مفرد بکار می‌رود."},
            {"target": "It is raining outside.", "native": "بیرون باران می‌بارد.", "breakdown": "It برای آب و هوا، زمان و اشیاء است."},
            {"target": "We learn English together.", "native": "ما با هم انگلیسی یاد می‌گیریم.", "breakdown": "We برای جمع (ما) استفاده می‌شود."},
            {"target": "They play football on Fridays.", "native": "آن‌ها روزهای جمعه فوتبال بازی می‌کنند.", "breakdown": "They برای آن‌ها به کار می‌رود."},
            {"target": "You are all welcome.", "native": "همه شما خوش آمدید.", "breakdown": "You می‌تواند به معنی شما (جمع) باشد."},
        ],
        "tips_json": [
            {"tip": "ضمیر I در انگلیسی همیشه با حرف بزرگ (Capital) نوشته می‌شود.", "example": "Yes, I am ready."}
        ],
        "common_mistakes_json": [
            {"wrong": "Is raining today.", "right": "It is raining today.", "reason": "در انگلیسی نمی‌توان ضمیر فاعلی It را حذف کرد."}
        ]
    },
    "indefinite_articles": {
        "title": "Indefinite Articles (a / an)",
        "explanation": "حروف تعریف نکره a و an برای اشاره به اسم مفرد قابل شمارش که ناآشنا یا عمومی است استفاده می‌شوند. از مهم‌ترین کاربردهای a و an بیان مشاغل و نقش افراد است. از 'a' قبل از صدای بی‌صدا و از 'an' قبل از صدای صدادار (a, e, i, o, u) استفاده می‌کنیم.",
        "comparison": "در فارسی برای بیان شغل کلمه 'یک' گفته نمی‌شود (می‌گوییم «او معلم است»)، اما در انگلیسی آوردن a یا an قبل از اسامی مشاغل مفرد الزامی است (She is a teacher).",
        "examples_json": [
            {"target": "I have a car.", "native": "من یک ماشین دارم.", "breakdown": "car با صدای بی‌صدا c شروع می‌شود، پس a می‌گیرد."},
            {"target": "She eats an apple.", "native": "او یک سیب می‌خورد.", "breakdown": "apple با حرف صدادار a شروع شده، پس an می‌گیرد."},
            {"target": "He is an engineer.", "native": "او یک مهندس است.", "breakdown": "قبل از مشاغل مفرد (engineer) حرف تعریف an (به علت حرف صدادار e) الزامی است."},
            {"target": "There is a book on the table.", "native": "یک کتاب روی میز است.", "breakdown": "book با b شروع می‌شود، پس a می‌آید."},
            {"target": "I saw an elephant.", "native": "من یک فیل دیدم.", "breakdown": "elephant با e شروع شده و an می‌گیرد."},
            {"target": "Give me a pen, please.", "native": "لطفاً یک خودکار به من بده.", "breakdown": "pen با صدای بی‌صدا p شروع می‌شود."},
            {"target": "It takes an hour.", "native": "یک ساعت طول می‌کشد.", "breakdown": "حرف h در hour تلفظ نمی‌شود، پس an می‌گیرد."},
            {"target": "He is a good boy.", "native": "او پسر خوبی است.", "breakdown": "صفت good با g شروع شده و a می‌گیرد."},
        ],
        "tips_json": [
            {"tip": "قبل از اسامی تمام مشاغل مفرد حتماً از a یا an استفاده کنید.", "example": "She is a doctor. / He is an artist."}
        ],
        "common_mistakes_json": [
            {"wrong": "He is doctor.", "right": "He is a doctor.", "reason": "اسم شغل مفرد در انگلیسی بدون a یا an بکار نمی‌رود."}
        ]
    },
    "definite_article": {
        "title": "Definite Article (the)",
        "explanation": "حرف تعریف the برای اشاره به اسامی مشخص و شناخته‌شده توسط گوینده و شنونده استفاده می‌شود. هم برای اسامی مفرد و هم جمع به کار می‌رود.",
        "comparison": "در زبان فارسی حرف تعریف معرفه وجود ندارد و شناسا بودن اسم از قرینه کلام فهمیده می‌شود، اما در انگلیسی باید از the استفاده کرد.",
        "examples_json": [
            {"target": "The sun is bright.", "native": "خورشید درخشان است.", "breakdown": "خورشید پدیده‌ای منحصربه‌فرد است و the می‌گیرد."},
            {"target": "Close the door.", "native": "در را ببند.", "breakdown": "اشاره به درِ مشخصی که هر دو طرف می‌شناسند."},
            {"target": "The books on the table are mine.", "native": "کتاب‌های روی میز مال من هستند.", "breakdown": "کتاب‌های مشخص روی میز."},
            {"target": "The capital of Iran is Tehran.", "native": "پایتخت ایران تهران است.", "breakdown": "پایتخت مشخص است و the می‌گیرد."},
            {"target": "Look at the moon.", "native": "به ماه نگاه کن.", "breakdown": "ماه تک و مشخص است."},
            {"target": "She is playing the piano.", "native": "او دارد پیانو می‌نوازد.", "breakdown": "قبل از آلات موسیقی the می‌آید."},
            {"target": "The water in this glass is cold.", "native": "آب این لیوان سرد است.", "breakdown": "آب مشخص درون لیوان."},
            {"target": "The children are playing outside.", "native": "بچه‌ها دارند بیرون بازی می‌کنند.", "breakdown": "بچه‌های مشخص."},
        ],
        "tips_json": [
            {"tip": "قبل از نام کشورها (به جز مواردی مانند The USA) از the استفاده نکنید.", "example": "I live in Iran."}
        ],
        "common_mistakes_json": [
            {"wrong": "I live in the Tehran.", "right": "I live in Tehran.", "reason": "قبل از نام اکثر شهرها و کشورها the نمی‌آید."}
        ]
    },
    "plural_nouns": {
        "title": "Plural Nouns",
        "explanation": "برای جمع بستن اسامی در انگلیسی معمولاً به انتهای اسم 's' یا 'es' اضافه می‌شود. برخی اسامی دارای جمع بی‌قاعده هستند که شکل کلمه تغییر می‌کند.",
        "comparison": "در فارسی از پسوندهای 'ها' یا 'ان' برای جمع استفاده می‌شود. در انگلیسی قاعده اصلی اضافه کردن s است و تغییرات در خود کلمه صورت می‌گیرد.",
        "examples_json": [
            {"target": "I have two dogs.", "native": "من دو سگ دارم.", "breakdown": "جمع با اضافه شدن s به dog ساخته شده است."},
            {"target": "She bought three books.", "native": "او سه کتاب خرید.", "breakdown": "جمع با s به book."},
            {"target": "He washed the dishes.", "native": "او ظرف‌ها را شست.", "breakdown": "کلمات ختم‌شده به sh با es جمع می‌شوند."},
            {"target": "There are four boxes here.", "native": "چهار جعبه اینجا وجود دارد.", "breakdown": "کلمات ختم‌شده به x با es جمع می‌شوند."},
            {"target": "The children are playing.", "native": "بچه‌ها دارند بازی می‌کنند.", "breakdown": "children جمع بی‌قاعده child است."},
            {"target": "Two men are standing there.", "native": "دو مرد آنجا ایستاده‌اند.", "breakdown": "men جمع بی‌قاعده man است."},
            {"target": "I see three cars.", "native": "من سه ماشین می‌بینم.", "breakdown": "جمع با اضافه شدن s."},
            {"target": "Put the glasses on the table.", "native": "لیوان‌ها را روی میز بگذار.", "breakdown": "glass به es جمع بسته می‌شود."},
        ],
        "tips_json": [
            {"tip": "کلماتی که به s, sh, ch, x ختم می‌شوند با es جمع بسته می‌شوند.", "example": "bus -> buses"}
        ],
        "common_mistakes_json": [
            {"wrong": "two childs", "right": "two children", "reason": "کلمه child جمع بی‌قاعده دارد و childs نادرست است."}
        ]
    },
    "possessive_adjectives": {
        "title": "Possessive Adjectives",
        "explanation": "صفات مالکیتی نشان می‌دهند چه چیزی متعلق به چه کسی است. صفات مالکیتی عبارتند از: my, your, his, her, its, our, their.",
        "comparison": "در فارسی مالکیت با ضمیر متصل (ـَم، ـَت، ـَش) به انتهای اسم متصل می‌شود (کتابم)، اما در انگلیسی صفت مالکیتی همیشه **قبل از اسم** می‌آید (my book).",
        "examples_json": [
            {"target": "This is my house.", "native": "این خانه من است.", "breakdown": "my صفت مالکیتی متکلم است."},
            {"target": "What is your name?", "native": "نام تو چیست؟", "breakdown": "your صفت مالکیتی مخاطب است."},
            {"target": "His car is red.", "native": "ماشین او (مذکر) قرمز است.", "breakdown": "his صفت مالکیتی مذکر است."},
            {"target": "Her phone is new.", "native": "تلفن او (مونث) جدید است.", "breakdown": "her صفت مالکیتی مونث است."},
            {"target": "The dog wags its tail.", "native": "سگ دمش را تکان می‌دهد.", "breakdown": "its صفت مالکیتی غیرانسان است."},
            {"target": "Our school is big.", "native": "مدرسه ما بزرگ است.", "breakdown": "our صفت مالکیتی ما است."},
            {"target": "Their house is near the park.", "native": "خانه آن‌ها نزدیک پارک است.", "breakdown": "their صفت مالکیتی آن‌ها است."},
            {"target": "I like your new shoes.", "native": "کفش‌های جدیدت را دوست دارم.", "breakdown": "your قبل از اسم shoes می‌آید."},
        ],
        "tips_json": [
            {"tip": "اشتباه نکنید: its صفت مالکیتی است ولی it's مخفف it is می‌باشد.", "example": "its color / it's cold"}
        ],
        "common_mistakes_json": [
            {"wrong": "This is book my.", "right": "This is my book.", "reason": "صفت مالکیتی همیشه قبل از اسم قرار می‌گیرد."}
        ]
    },
    "demonstratives": {
        "title": "Demonstratives (this / that / these / those)",
        "explanation": "کلمات اشاره برای نشان دادن فاصله زمانی یا مکانی استفاده می‌شوند: this (این - مفرد نزدیک)، that (آن - مفرد دور)، these (این‌ها - جمع نزدیک)، those (آن‌ها - جمع دور).",
        "comparison": "در فارسی برای اشاره جمع نیز گاهی از 'این' و 'آن' استفاده می‌شود، اما در انگلیسی استفاده از این‌ها (these) و آن‌ها (those) اجباری است.",
        "examples_json": [
            {"target": "This is my bag.", "native": "این کیف من است.", "breakdown": "This اشاره به مفرد نزدیک دارد."},
            {"target": "That is a high mountain.", "native": "آن یک کوه بلند است.", "breakdown": "That اشاره به مفرد دور دارد."},
            {"target": "These are fresh apples.", "native": "این‌ها سیب‌های تازه‌ای هستند.", "breakdown": "These اشاره به جمع نزدیک دارد."},
            {"target": "Those stars are bright.", "native": "آن ستاره‌ها درخشان هستند.", "breakdown": "Those اشاره به جمع دور دارد."},
            {"target": "I like this shirt.", "native": "من این پیراهن را دوست دارم.", "breakdown": "This صفت اشاره مفرد نزدیک است."},
            {"target": "Look at that bird!", "native": "به آن پرنده نگاه کن!", "breakdown": "That برای پرنده در فاصله دور."},
            {"target": "These books are very interesting.", "native": "این کتاب‌ها بسیار جالب هستند.", "breakdown": "These برای کتاب‌های نزدیک."},
            {"target": "Who are those people over there?", "native": "آن افراد آن طرف چه کسانی هستند؟", "breakdown": "Those برای اشخاص در فاصله دور."},
        ],
        "tips_json": [
            {"tip": "بعد از this و that اسم مفرد و بعد از these و those اسم جمع می‌آید.", "example": "this boy / these boys"}
        ],
        "common_mistakes_json": [
            {"wrong": "These is my book.", "right": "This is my book.", "reason": "برای اسم مفرد باید از this استفاده کرد نه these."}
        ]
    },
    "present_simple_affirmative": {
        "title": "Present Simple – Affirmative",
        "explanation": "زمان حال ساده برای بیان حقایق کلی، عادات روزمره و برنامه‌های منظم استفاده می‌شود. برای ضمایر he, she, it به انتهای فعل اصلی پسوند s یا es اضافه می‌کنیم.",
        "comparison": "در فارسی برای زمان حال ساده از می + ریشه فعل + شناسه (می‌روم، می‌رود) استفاده می‌شود. در انگلیسی فعل اصلی برای اکثر ضمایر تغییر نمی‌کند و فقط برای سوم شخص مفرد s می‌گیرد.",
        "examples_json": [
            {"target": "I drink milk every morning.", "native": "من هر روز صبح شیر می‌نوشم.", "breakdown": "عادت روزمره با فعل ساده drink."},
            {"target": "She plays tennis on Saturdays.", "native": "او روزهای شنبه تنیس بازی می‌کند.", "breakdown": "فعل play پس از she پسوند s گرفته است."},
            {"target": "He lives in Canada.", "native": "او در کانادا زندگی می‌کند.", "breakdown": "فعل live پس از he پسوند s می‌گیرد."},
            {"target": "They study English every night.", "native": "آن‌ها هر شب انگلیسی می‌خوانند.", "breakdown": "برای جمع (They) فعل ساده بکار می‌رود."},
            {"target": "The sun rises in the east.", "native": "خورشید از شرق طلوع می‌کند.", "breakdown": "حقیقت علمی با s سوم شخص."},
            {"target": "We work from 9 to 5.", "native": "ما از ساعت ۹ تا ۵ کار می‌کنیم.", "breakdown": "برنامه کاری با فعل ساده work."},
            {"target": "It rains a lot in winter.", "native": "در زمستان باران زیادی می‌بارد.", "breakdown": "برای آب و هوا با it و s فعل."},
            {"target": "You speak English very well.", "native": "تو خیلی خوب انگلیسی صحبت می‌کنی.", "breakdown": "فعل ساده speak برای you."},
        ],
        "tips_json": [
            {"tip": "فراموش نکنید برای he, she, it حتماً s یا es به انتهای فعل اضافه کنید.", "example": "He runs fast."}
        ],
        "common_mistakes_json": [
            {"wrong": "She live in London.", "right": "She lives in London.", "reason": "برای she فعل نیاز به s دارد."}
        ]
    },
    "present_simple_negative": {
        "title": "Present Simple – Negative",
        "explanation": "برای منفی کردن زمان حال ساده از فعل کمکی don't (do not) یا doesn't (does not) قبل از فعل اصلی استفاده می‌شود. بعد از doesn't، پسوند s فعل اصلی حذف می‌شود.",
        "comparison": "در فارسی منفی کردن با پیشوند 'نـ' (نمی‌روم، نمی‌رود) ساخته می‌شود، اما در انگلیسی از افعال کمکی don't/doesn't قبل از فعل استفاده می‌کنیم.",
        "examples_json": [
            {"target": "I don't like tea.", "native": "من چای دوست ندارم.", "breakdown": "برای I از don't استفاده می‌شود."},
            {"target": "She doesn't speak French.", "native": "او فرانسوی صحبت نمی‌کند.", "breakdown": "برای she از doesn't استفاده می‌شود و s حذف می‌شود."},
            {"target": "He doesn't eat meat.", "native": "او گوشت نمی‌خورد.", "breakdown": "doesn't + فعل پایه eat."},
            {"target": "They don't watch TV.", "native": "آن‌ها تلویزیون تماشا نمی‌کنند.", "breakdown": "منفی جمع با don't."},
            {"target": "We don't work on Sundays.", "native": "ما روزهای یکشنبه کار نمی‌کنیم.", "breakdown": "منفی با don't برای We."},
            {"target": "It doesn't snow in summer.", "native": "در تابستان باران/برف نمی‌بارد.", "breakdown": "doesn't برای it."},
            {"target": "You don't need a key.", "native": "تو نیازی به کلید نداری.", "breakdown": "don't برای You."},
            {"target": "My brother doesn't smoke.", "native": "برادر من سیگار نمی‌کشد.", "breakdown": "برادرم (مفرد) doesn't می‌گیرد."},
        ],
        "tips_json": [
            {"tip": "بعد از doesn't فعل اصلی نباید s بگیرد.", "example": "He doesn't like (NOT doesn't likes)"}
        ],
        "common_mistakes_json": [
            {"wrong": "She doesn't likes coffee.", "right": "She doesn't like coffee.", "reason": "پس از doesn't پسوند s فعل برداشته می‌شود."}
        ]
    },
    "present_simple_questions": {
        "title": "Present Simple – Questions",
        "explanation": "برای سوالی کردن زمان حال ساده از Do یا Does در ابتدای جمله استفاده می‌شود. فرمول: Do/Does + فاعل + شکل ساده فعل؟",
        "comparison": "در فارسی با افزودن لحن سوالی یا کلمه 'آیا' جمله سوالی می‌شود. در انگلیسی حتماً باید فعل کمکی Do یا Does در ابتدای جمله قرار گیرد.",
        "examples_json": [
            {"target": "Do you speak English?", "native": "آیا شما انگلیسی صحبت می‌کنید؟", "breakdown": "سوالی با Do برای مخاطب (you)."},
            {"target": "Does she live here?", "native": "آیا او اینجا زندگی می‌کند؟", "breakdown": "سوالی با Does برای سوم شخص (she)."},
            {"target": "Do they play football?", "native": "آیا آن‌ها فوتبال بازی می‌کنند؟", "breakdown": "سوالی با Do برای جمع (they)."},
            {"target": "Does he work at a school?", "native": "آیا او در مدرسه کار می‌کند؟", "breakdown": "سوالی با Does برای he."},
            {"target": "Do we have time?", "native": "آیا ما وقت داریم؟", "breakdown": "سوالی با Do برای we."},
            {"target": "Does it rain a lot in autumn?", "native": "آیا در پاییز باران زیادی می‌بارد؟", "breakdown": "سوالی با Does برای it."},
            {"target": "Where do you live?", "native": "کجا زندگی می‌کنی؟", "breakdown": "سوال Wh با Do و فاعل you."},
            {"target": "What does she want?", "native": "او چه می‌خواهد؟", "breakdown": "سوال Wh با Does و فاعل she."},
        ],
        "tips_json": [
            {"tip": "در جملات سوالی با Does، پسوند s از انتهای فعل اصلی پاک می‌شود.", "example": "Does he go? (NOT Does he goes?)"}
        ],
        "common_mistakes_json": [
            {"wrong": "Does she likes music?", "right": "Does she like music?", "reason": "در حضور Does فعل اصلی s نمی‌گیرد."}
        ]
    },
    "have_got": {
        "title": "Have Got",
        "explanation": "عبارت 'have got' یا 'has got' در انگلیسی بریتانیایی به معنای داشتن مالکیت یا روابط خانوادگی است. I/you/we/they have got و he/she/it has got می‌گیرند.",
        "comparison": "در فارسی فعل 'داشتن' صرف می‌شود (دارم، داری، دارد). در انگلیسی have/has got نقش فعل داشتن را ایفا می‌کند.",
        "examples_json": [
            {"target": "I have got a new car.", "native": "من یک ماشین جدید دارم.", "breakdown": "have got برای I."},
            {"target": "She has got two brothers.", "native": "او دو برادر دارد.", "breakdown": "has got برای she."},
            {"target": "They have got a big garden.", "native": "آن‌ها یک باغ بزرگ دارند.", "breakdown": "have got برای they."},
            {"target": "He has got dark hair.", "native": "او موهای تیره دارد.", "breakdown": "has got برای ویژگی ظاهری he."},
            {"target": "We have got a lot of work.", "native": "ما کار زیادی داریم.", "breakdown": "have got برای we."},
            {"target": "I haven't got any money.", "native": "من هیچ پولی ندارم.", "breakdown": "منفی haven't got."},
            {"target": "She hasn't got a bicycle.", "native": "او دوچرخه‌ای ندارد.", "breakdown": "منفی hasn't got."},
            {"target": "Have you got a pen?", "native": "آیا خودکار داری؟", "breakdown": "سوالی با Have در ابتدا."},
        ],
        "tips_json": [
            {"tip": "شکل مخفف have got به صورت 've got و has got به صورت 's got است.", "example": "I've got a cat. / He's got a dog."}
        ],
        "common_mistakes_json": [
            {"wrong": "She have got a car.", "right": "She has got a car.", "reason": "برای she باید از has got استفاده شود."}
        ]
    },
    "can_ability": {
        "title": "Can – Ability & Permission",
        "explanation": "فعل کمکی can به معنای 'توانستن' برای بیان توانایی، استعداد یا اجازه گرفتن به کار می‌رود. این فعل برای تمام ضمایر شکل یکسان دارد و s نمی‌گیرد.",
        "comparison": "در فارسی فعل توانستن صرف می‌شود (می‌توانم، می‌توانی، می‌تواند)، اما در انگلیسی can برای تمام اشخاص ثابت است.",
        "examples_json": [
            {"target": "I can swim very well.", "native": "من می‌توانم خیلی خوب شنا کنم.", "breakdown": "بیان توانایی فیزیکی با can."},
            {"target": "She can speak English.", "native": "او می‌تواند انگلیسی صحبت کند.", "breakdown": "can برای تمام ضمایر ثابت است و s نمی‌گیرد."},
            {"target": "He can play the guitar.", "native": "او می‌تواند گیتار بنوازد.", "breakdown": "توانایی نواختن با can."},
            {"target": "They can drive a car.", "native": "آن‌ها می‌توانند رانندگی کنند.", "breakdown": "توانایی رانندگی."},
            {"target": "I can't hear you.", "native": "من نمی‌توانم صدای شما را بشنوم.", "breakdown": "منفی can به صورت can't است."},
            {"target": "She can't come today.", "native": "او امروز نمی‌تواند بیاید.", "breakdown": "منفی توانستن با can't."},
            {"target": "Can you help me?", "native": "آیا می‌توانی به من کمک کنی؟", "breakdown": "درخواست کمک و سوالی با Can."},
            {"target": "Can I open the window?", "native": "آیا می‌توانم پنجره را باز کنم؟", "breakdown": "اجازه گرفتن با Can."},
        ],
        "tips_json": [
            {"tip": "بعد از can همیشه فعل به صورت ساده و بدون to می‌آید.", "example": "I can run (NOT I can to run)"}
        ],
        "common_mistakes_json": [
            {"wrong": "She cans swim.", "right": "She can swim.", "reason": "فعل can به هیچ عنوان پسوند s نمی‌گیرد."}
        ]
    },
    "imperative": {
        "title": "Imperative (Commands)",
        "explanation": "جملات امری برای دستور دادن، راهنمایی کردن یا خواهش کردن استفاده می‌شوند. برای ساخت جمله امری مثبت از شکل ساده فعل در اول جمله و برای منفی از Don't استفاده می‌کنیم.",
        "comparison": "در فارسی فعل امری شناسه دوم شخص می‌گیرد (بیا، بروید)، اما در انگلیسی جمله امری فقط با ریشه ساده فعل بدون فاعل ساخته می‌شود.",
        "examples_json": [
            {"target": "Open the window, please.", "native": "لطفاً پنجره را باز کن.", "breakdown": "امری مثبت با ریشه ساده فعل Open."},
            {"target": "Listen to the teacher.", "native": "به معلم گوش دهید.", "breakdown": "دستور امری با Listen."},
            {"target": "Don't make noise!", "native": "سر و صدا نکنید!", "breakdown": "امری منفی با Don't."},
            {"target": "Sit down, please.", "native": "لطفاً بنشینید.", "breakdown": "امری محترمانه با Please."},
            {"target": "Don't touch that plate.", "native": "به آن بشقاب دست نزن.", "breakdown": "نهی و امری منفی با Don't."},
            {"target": "Be quiet in the library.", "native": "در کتابخانه ساکت باشید.", "breakdown": "امری با فعل Be."},
            {"target": "Don't be late!", "native": "دیر نکنید!", "breakdown": "امری منفی با Don't be."},
            {"target": "Close your books now.", "native": "اکنون کتاب‌هایتان را ببندید.", "breakdown": "دستور با Close."},
        ],
        "tips_json": [
            {"tip": "افزودن کلمه Please در ابتدای یا انتهای جمله امری، آن را محترمانه می‌کند.", "example": "Please come in."}
        ],
        "common_mistakes_json": [
            {"wrong": "To open the door.", "right": "Open the door.", "reason": "جمله امری با to شروع نمی‌شود."}
        ]
    },
    "there_is_there_are": {
        "title": "There is / There are",
        "explanation": "برای بیان وجود داشتن اشیاء یا افراد در یک مکان از 'There is' (برای مفرد و غیرقابل شمارش) و 'There are' (برای جمع) استفاده می‌کنیم.",
        "comparison": "در فارسی کلمه 'وجود دارد / هست' در آخر جمله می‌آید، اما در انگلیسی 'There is/are' در ابتدای جمله قرار می‌گیرد.",
        "examples_json": [
            {"target": "There is a book on the table.", "native": "یک کتاب روی میز وجود دارد.", "breakdown": "There is برای اسم مفرد a book."},
            {"target": "There are three computers in the office.", "native": "سه کامپیوتر در دفتر وجود دارد.", "breakdown": "There are برای اسم جمع three computers."},
            {"target": "There is some water in the bottle.", "native": "مقداری آب در بطری هست.", "breakdown": "There is برای غیرقابل شمارش water."},
            {"target": "There are many trees in the park.", "native": "درختان زیادی در پارک هست.", "breakdown": "There are برای جمع many trees."},
            {"target": "There isn't a clock in this room.", "native": "ساعتی در این اتاق نیست.", "breakdown": "منفی مفرد با There isn't."},
            {"target": "There aren't any chairs here.", "native": "هیچ صندلی اینجا نیست.", "breakdown": "منفی جمع با There aren't."},
            {"target": "Is there a hospital near here?", "native": "آیا بیمارستانی نزدیک اینجا هست؟", "breakdown": "سوالی مفرد با Is there."},
            {"target": "Are there any questions?", "native": "آیا سوالی وجود دارد؟", "breakdown": "سوالی جمع با Are there."},
        ],
        "tips_json": [
            {"tip": "برای اسامی غیرقابل شمارش مثل آب، شیر و پول همیشه از There is استفاده کنید.", "example": "There is milk."}
        ],
        "common_mistakes_json": [
            {"wrong": "There is two cats.", "right": "There are two cats.", "reason": "برای اسم جمع (two cats) باید از There are استفاده کرد."}
        ]
    },
    "basic_prepositions_place": {
        "title": "Prepositions of Place",
        "explanation": "حروف اضافه مکان نشان می‌دهند اشیاء یا افراد در چه موقعیت مکانی قرار دارند. حروف اضافه اصلی: in (در/داخل)، on (روی)، at (در/در نقطه)، under (زیر)، next to (کنار).",
        "comparison": "در فارسی حروف اضافه پیش از اسم قرار می‌گیرند (روی میز). در انگلیسی نیز حروف اضافه قبل از اسم می‌آیند (on the table) با این تفاوت که دقت در انتخاب in/on/at اهمیت بالایی دارد.",
        "examples_json": [
            {"target": "The book is on the table.", "native": "کتاب روی میز است.", "breakdown": "on به معنای تماس بر روی سطح است."},
            {"target": "The keys are in my bag.", "native": "کلیدها داخل کیف من هستند.", "breakdown": "in به معنای داخل یک فضای بسته است."},
            {"target": "She is standing at the bus stop.", "native": "او در ایستگاه اتوبوس ایستاده است.", "breakdown": "at برای اشاره به موقعیت مکان مشخص است."},
            {"target": "The cat is sleeping under the chair.", "native": "گربه زیر صندلی خوابیده است.", "breakdown": "under به معنای زیر چیزی است."},
            {"target": "The school is next to the bank.", "native": "مدرسه کنار بانک است.", "breakdown": "next to به معنای مجاور و کنار است."},
            {"target": "There is a picture on the wall.", "native": "تصویری روی دیوار قرار دارد.", "breakdown": "روی سطح عمودی دیوار با on آمده است."},
            {"target": "He lives in Tehran.", "native": "او در تهران زندگی می‌کند.", "breakdown": "قبل از نام شهرها همیشه in می‌آید."},
            {"target": "We are at home now.", "native": "ما الان در خانه هستیم.", "breakdown": "موقعیت در خانه با at home بیان می‌شود."},
        ],
        "tips_json": [
            {"tip": "برای شهرها و کشورها از in و برای موقعیت‌های خاص از at استفاده کنید.", "example": "in Paris / at school"}
        ],
        "common_mistakes_json": [
            {"wrong": "He lives at London.", "right": "He lives in London.", "reason": "قبل از شهرها باید از in استفاده شود."}
        ]
    },
    "adjectives_basic": {
        "title": "Basic Adjectives",
        "explanation": "صفات کلماتی هستند که کیفیت و ویژگی اسامی را توصیف می‌کنند (مانند big, small, hot, cold). در انگلیسی صفت همیشه **قبل از اسم** یا **بعد از فعل to be** می‌آید.",
        "comparison": "در فارسی صفت **بعد از اسم** با کسره اضافه می‌آید (ماشینِ سریع)، اما در انگلیسی صفت دقیقاً **قبل از اسم** قرار می‌گیرد (a fast car). همچنین صفت در انگلیسی مفرد و جمع ندارد.",
        "examples_json": [
            {"target": "This is a big house.", "native": "این یک خانه بزرگ است.", "breakdown": "صفت big قبل از اسم house قرار گرفته است."},
            {"target": "The coffee is hot.", "native": "قهوه داغ است.", "breakdown": "صفت hot پس از فعل is آمده است."},
            {"target": "She bought a red car.", "native": "او یک ماشین قرمز خرید.", "breakdown": "صفت رنگ red قبل از car قرار دارد."},
            {"target": "He is a smart boy.", "native": "او پسر باهوشی است.", "breakdown": "صفت smart قبل از اسم boy آمده است."},
            {"target": "Today is a cold day.", "native": "امروز روز سردی است.", "breakdown": "صفت cold قبل از day قرار دارد."},
            {"target": "They have two small dogs.", "native": "آن‌ها دو سگ کوچک دارند.", "breakdown": "صفت برای اسم جمع هم به شکل مفرد (small) می‌ماند."},
            {"target": "The movie was interesting.", "native": "فیلم جالب بود.", "breakdown": "صفت بعد از فعل was آمده است."},
            {"target": "I like fresh apples.", "native": "من سیب‌های تازه را دوست دارم.", "breakdown": "صفت fresh قبل از اسم جمع apples."},
        ],
        "tips_json": [
            {"tip": "صفات در انگلیسی هیچ‌گاه s جمع نمی‌گیرند.", "example": "red cars (NOT reds cars)"}
        ],
        "common_mistakes_json": [
            {"wrong": "a car red", "right": "a red car", "reason": "صفت در انگلیسی باید قبل از اسم بیاید."}
        ]
    },
    "numbers_and_quantity": {
        "title": "Numbers and Quantity",
        "explanation": "اسامی قابل شمارش را می‌توان شمرده و با اعداد و many بیان کرد. اسامی غیرقابل شمارش (مانند آب، پول، شکر) فقط با much یا some همراه می‌شوند.",
        "comparison": "در فارسی بعد از اعداد اسم به صورت مفرد می‌آید (دو کتاب)، اما در انگلیسی اسم بعد از عدد جمع بسته می‌شود (two books).",
        "examples_json": [
            {"target": "I have three books.", "native": "من سه کتاب دارم.", "breakdown": "بعد از عدد ۳ اسم جمع (books) می‌آید."},
            {"target": "There are seven days in a week.", "native": "هفت روز در یک هفته وجود دارد.", "breakdown": "عدد هفت قبل از اسم جمع days."},
            {"target": "She has many friends.", "native": "او دوستان زیادی دارد.", "breakdown": "many قبل از اسم قابل شمارش جمع."},
            {"target": "How much water do you drink?", "native": "چقدر آب می‌نوشی؟", "breakdown": "How much برای غیرقابل شمارش water."},
            {"target": "I need some money.", "native": "من به مقداری پول نیاز دارم.", "breakdown": "some برای غیرقابل شمارش money."},
            {"target": "There are a few apples left.", "native": "تعداد کمی سیب باقی مانده است.", "breakdown": "a few برای تعداد کم قابل شمارش."},
            {"target": "He drinks a lot of tea.", "native": "او مقدار زیادی چای می‌نوشد.", "breakdown": "a lot of هم برای شمارشی و هم غیرقابل شمارش."},
            {"target": "How many students are there?", "native": "چند دانش‌آموز وجود دارد؟", "breakdown": "How many برای پرسش تعداد قابل شمارش."},
        ],
        "tips_json": [
            {"tip": "برای غیرقابل شمارش‌ها از much و برای قابل شمارش‌ها از many استفاده کنید.", "example": "much sugar / many apples"}
        ],
        "common_mistakes_json": [
            {"wrong": "three book", "right": "three books", "reason": "بعد از اعداد بزرگتر از ۱ اسم در انگلیسی جمع بسته می‌شود."}
        ]
    },
    "wh_questions": {
        "title": "Wh- Questions",
        "explanation": "کلمات پرسشی Wh برای گرفتن اطلاعات خاص به کار می‌روند: What (چه چیزی)، Where (کجا)، Who (چه کسی)، When (چه زمانی)، Why (چرا)، How (چگونه).",
        "comparison": "در انگلیسی کلمه پرسشی Wh همیشه در **ابتدای جمله** قرار می‌گیرد و پس از آن بلافاصله فعل کمکی می‌آید.",
        "examples_json": [
            {"target": "What is your name?", "native": "نام شما چیست؟", "breakdown": "What برای پرسش درباره شیء یا اسم."},
            {"target": "Where do you live?", "native": "کجا زندگی می‌کنی؟", "breakdown": "Where برای پرسش مکان با فعل کمکی do."},
            {"target": "Who is that girl?", "native": "آن دختر کیست؟", "breakdown": "Who برای پرسش هویت اشخاص."},
            {"target": "When does the bus arrive?", "native": "اتوبوس چه زمانی می‌رسد؟", "breakdown": "When برای پرسش زمان با does."},
            {"target": "Why are you late?", "native": "چرا دیر کرده‌ای؟", "breakdown": "Why برای پرسش علت با verb to be."},
            {"target": "How are you today?", "native": "امروز چطور هستی؟", "breakdown": "How برای پرسش حالت و چگونگی."},
            {"target": "What time is it?", "native": "ساعت چند است؟", "breakdown": "What time برای سوال ساعت."},
            {"target": "Where is the bathroom?", "native": "دستشویی کجا است؟", "breakdown": "Where برای پرسش درباره مکان قرارگیری."},
        ],
        "tips_json": [
            {"tip": "فرمول سوالات Wh: کلمه Wh + فعل کمکی + فاعل + فعل اصلی؟", "example": "Where do you work?"}
        ],
        "common_mistakes_json": [
            {"wrong": "Where you live?", "right": "Where do you live?", "reason": "در سوالات Wh فعل کمکی (do/does) نباید فراموش شود."}
        ]
    },
    "object_pronouns": {
        "title": "Object Pronouns",
        "explanation": "ضمایر مفعولی دریافت‌کننده عمل فعل هستند و همیشه بعد از فعل یا حروف اضافه قرار می‌گیرند: me, you, him, her, it, us, them.",
        "comparison": "در فارسی مفعول با نشانه 'را' همراه می‌شود (او را دیدم). در انگلیسی ضمیر مفعولی شکل کاملاً متفاوتی دارد (I -> me, She -> her) و بعد از فعل می‌آید.",
        "examples_json": [
            {"target": "Please call me tonight.", "native": "لطفاً امشب به من زنگ بزن.", "breakdown": "me ضمیر مفعولی دوم شخص متکلم است."},
            {"target": "I saw her at the supermarket.", "native": "من او را در سوپرمارکت دیدم.", "breakdown": "her ضمیر مفعولی مونث است."},
            {"target": "We visited him yesterday.", "native": "ما دیروز به ملاقات او رفتیم.", "breakdown": "him ضمیر مفعولی مذکر است."},
            {"target": "She gave us a present.", "native": "او به ما یک هدیه داد.", "breakdown": "us ضمیر مفعولی ما است."},
            {"target": "Look at them!", "native": "به آن‌ها نگاه کن!", "breakdown": "them بعد از حرف اضافه at برای آن‌ها."},
            {"target": "I can help you.", "native": "من می‌توانم به تو کمک کنم.", "breakdown": "you ضمیر مفعولی مخاطب است."},
            {"target": "Don't touch it!", "native": "به آن دست نزن!", "breakdown": "it ضمیر مفعولی غیرانسان است."},
            {"target": "He told me the secret.", "native": "او راز را به من گفت.", "breakdown": "me مفعول مستقیم فعل told."},
        ],
        "tips_json": [
            {"tip": "ضمایر مفعولی همیشه بعد از افعال یا حروف اضافه (to, with, at, for) می‌آیند.", "example": "Listen to me."}
        ],
        "common_mistakes_json": [
            {"wrong": "She saw I.", "right": "She saw me.", "reason": "بعد از فعل دیدن (saw) باید از ضمیر مفعولی me استفاده شود نه I."}
        ]
    },
    "like_and_want": {
        "title": "Like and Want",
        "explanation": "فعل like به معنای دوست داشتن و want به معنای خواستن است. وقتی بخواهیم کاری را انجام دهیم، بعد از want از to + فعل ساده استفاده می‌کنیم (want to go).",
        "comparison": "در فارسی بعد از خواستن فعل به صورت التزامی می‌آید (می‌خواهم بروم). در انگلیسی از ساختار 'want + to + فعل پایه' استفاده می‌شود.",
        "examples_json": [
            {"target": "I like ice cream.", "native": "من بستنی دوست دارم.", "breakdown": "like + اسم برای بیان علاقه."},
            {"target": "She wants a cup of coffee.", "native": "او یک فنجان قهوه می‌خواهد.", "breakdown": "wants برای سوم شخص مفرد she."},
            {"target": "I want to learn English.", "native": "من می‌خواهم انگلیسی یاد بگیرم.", "breakdown": "want + to + فعل ساده learn."},
            {"target": "He likes playing football.", "native": "او فوتبال بازی کردن را دوست دارد.", "breakdown": "likes + اسم مصدر."},
            {"target": "They want to travel to Italy.", "native": "آن‌ها می‌خواهند به ایتالیا سفر کنند.", "breakdown": "want + to + travel."},
            {"target": "Do you want some water?", "native": "آیا مقداری آب می‌خواهی؟", "breakdown": "سوالی با Do برای want."},
            {"target": "She doesn't like cold coffee.", "native": "او قهوه سرد دوست ندارد.", "breakdown": "منفی با doesn't like."},
            {"target": "We want to buy a new car.", "native": "ما می‌خواهیم یک ماشین جدید بخریم.", "breakdown": "want + to + buy."},
        ],
        "tips_json": [
            {"tip": "بعد از want برای انجام کار همیشه to قرار دهید.", "example": "I want to go (NOT I want go)"}
        ],
        "common_mistakes_json": [
            {"wrong": "I want go home.", "right": "I want to go home.", "reason": "بین want و فعل بعدی حرف اضافه to الزامی است."}
        ]
    },
}

def seed_grammar_content():
    print("=" * 60)
    print("🌱 Seeding Grammar Content with 8 Examples & Comparison for ALL 20 Topics")
    print("=" * 60)

    lang_id = sb.table("languages").select("id").eq("code", "en").single().execute().data["id"]
    level_id = sb.table("levels").select("id").eq("code", "A1").single().execute().data["id"]

    updated_count = 0

    for topic_code, content_data in A1_CONTENT_DATA.items():
        # Get topic UUID
        topic_row = sb.table("grammar_topics").select("id").eq("language_id", lang_id).eq("level_id", level_id).eq("topic_code", topic_code).maybe_single().execute()
        if not topic_row.data:
            print(f"❌ Topic {topic_code} not found in DB!")
            continue

        topic_id = topic_row.data["id"]

        # Check existing content
        existing = sb.table("grammar_content").select("id").eq("topic_id", topic_id).eq("native_language", "fa").maybe_single().execute()

        payload = {
            "topic_id": topic_id,
            "native_language": "fa",
            "title": content_data["title"],
            "explanation": content_data["explanation"] + "\n\n📌 تفاوت با زبان فارسی:\n" + content_data["comparison"],
            "examples_json": content_data["examples_json"],
            "tips_json": content_data["tips_json"],
            "common_mistakes_json": content_data["common_mistakes_json"],
            "quality_score": 0.98,
            "generation_model": "gpt-4o",
        }

        if existing.data:
            sb.table("grammar_content").update(payload).eq("id", existing.data["id"]).execute()
        else:
            sb.table("grammar_content").insert(payload).execute()

        updated_count += 1
        print(f"✅ Topic '{topic_code:28s}': updated with 8 examples & Persian comparison.")

    print("=" * 60)
    print(f"🎉 DONE! Updated {updated_count} topics in grammar_content table.")
    print("=" * 60)

if __name__ == "__main__":
    seed_grammar_content()
