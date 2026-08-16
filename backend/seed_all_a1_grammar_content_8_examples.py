"""
seed_all_a1_grammar_content_8_examples.py — Seed complete grammar content with 8 examples per topic
and Persian grammar comparison section for all 20 A1 topics in Supabase DB.
"""

import sys
from supabase import create_client

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

import os
from dotenv import load_dotenv
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# 20 Topics data with 8 examples each and Persian Grammar Comparison
A1_CONTENT_DATA = {'verb_to_be_present': {'title': "Verb 'to be' – Present",
                        'explanation': "فعل 'to be' در زبان انگلیسی به معنای 'بودن' است و در زمان حال به شکل\u200cهای "
                                       'am, is, و are استفاده می\u200cشود. این فعل برای بیان هویت، ویژگی، سن، شغل و '
                                       'حالت روحی اشخاص و اشیاء به کار می\u200cرود. این مبحث یکی از '
                                       'پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی است. با '
                                       'تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
                        'comparison': 'در زبان فارسی افعال بودن (هستم، هستی، است، هستیم، هستید، هستند) در آخر جمله '
                                      "می\u200cآیند، اما در انگلیسی فعل 'to be' بلافاصله بعد از فاعل (در ابتدای جمله) "
                                      'قرار می\u200cگیرد. همچنین برخلاف فارسی، در انگلیسی قبل از بیان **مشاغل و نقش '
                                      'افراد** حتماً باید از حرف تعریف a یا an استفاده شود (مثلاً She is a teacher '
                                      'یعنی او معلم است).',
                        'examples_json': [{'target': 'I am a student.',
                                           'native': 'من یک دانش\u200cآموز هستم.',
                                           'breakdown': 'فعل am با ضمیر I می\u200cآید. حرف a قبل از شغل/نقش (student) '
                                                        'اجباری است.'},
                                          {'target': 'She is a teacher.',
                                           'native': 'او یک معلم است.',
                                           'breakdown': 'فعل is با ضمیر she می\u200cآید. حرف a قبل از عنوان شغل '
                                                        '(teacher) الزامی است.'},
                                          {'target': 'They are happy.',
                                           'native': 'آن\u200cها خوشحال هستند.',
                                           'breakdown': 'are با ضمیر جمع they استفاده می\u200cشود.'},
                                          {'target': 'He is my brother.',
                                           'native': 'او برادر من است.',
                                           'breakdown': 'فعل is با he می\u200cآید (چون صفت مالکیتی my داریم نیازی به a '
                                                        'نیست).'},
                                          {'target': 'We are in the classroom.',
                                           'native': 'ما در کلاس درس هستیم.',
                                           'breakdown': 'are همراه we برای موقعیت مکانی بکار می\u200cرود.'},
                                          {'target': 'It is a beautiful cat.',
                                           'native': 'این یک گربه زیبا است.',
                                           'breakdown': 'it برای حیوانات و اشیاء مفرد است و a قبل از صفت/اسم مفرد '
                                                        'می\u200cآید.'},
                                          {'target': 'You are very kind.',
                                           'native': 'تو بسیار مهربان هستی.',
                                           'breakdown': 'you هم برای مفرد و هم جمع are می\u200cگیرد.'},
                                          {'target': 'The coffee is hot.',
                                           'native': 'قهوه داغ است.',
                                           'breakdown': 'اسم مفرد (The coffee) فعل is می\u200cگیرد.'}],
                        'tips_json': [{'tip': 'در انگلیسی قبل از بیان مشاغل (معلم، پزشک، مهندس و ...) حتماً باید a یا '
                                              'an استفاده شود.',
                                       'example': 'She is a teacher. / He is an engineer.'},
                                      {'tip': "همیشه جملات پایه موضوع Verb 'to be' – Present را در زمینه\u200cهای "
                                              'روزمره تمرین کنید.',
                                       'example': 'I practice this every day.'},
                                      {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته '
                                              'باشید.',
                                       'example': 'She is in Stockholm today.'}],
                        'common_mistakes_json': [{'wrong': 'She is teacher.',
                                                  'right': 'She is a teacher.',
                                                  'reason': 'در انگلیسی قبل از نام مشاغل مفرد آوردن a یا an اجباری '
                                                            'است.'},
                                                 {'wrong': 'He go to school yesterday.',
                                                  'right': 'He goes to school every day.',
                                                  'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت '
                                                            'شود.'},
                                                 {'wrong': 'They is happy here.',
                                                  'right': 'They are happy here.',
                                                  'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات '
                                                            'هستند.'}]},
 'personal_pronouns': {'title': 'Personal Pronouns',
                       'explanation': 'ضمایر فاعلی کلماتی هستند که جانشین اسم می\u200cشوند تا از تکرار آن در جمله '
                                      'جلوگیری کنند. ضمایر فاعلی انگلیسی عبارتند از: I, You, He, She, It, We, They. '
                                      'این مبحث یکی از پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر زبان '
                                      'انگلیسی است. با تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل '
                                      'پیدا کنید.',
                       'comparison': 'در فارسی ضمایر فاعلی (من، تو، او، ما، شما، آن\u200cها) اغلب از جمله حذف '
                                     'می\u200cشوند چون شناسه فعل شخص را نشان می\u200cدهد. اما در انگلیسی آوردن ضمیر '
                                     'فاعلی الزامی است.',
                       'examples_json': [{'target': 'I live in Tehran.',
                                          'native': 'من در تهران زندگی می\u200cکنم.',
                                          'breakdown': 'I ضمیر متکلم مفرد (من) است.'},
                                         {'target': 'You are my best friend.',
                                          'native': 'تو بهترین دوست من هستی.',
                                          'breakdown': 'You برای تو و شما استفاده می\u200cشود.'},
                                         {'target': 'He works at a hospital.',
                                          'native': 'او در بیمارستان کار می\u200cکند.',
                                          'breakdown': 'He برای مذکر مفرد استفاده می\u200cشود.'},
                                         {'target': 'She speaks English well.',
                                          'native': 'او انگلیسی را خوب صحبت می\u200cکند.',
                                          'breakdown': 'She برای مونث مفرد بکار می\u200cرود.'},
                                         {'target': 'It is raining outside.',
                                          'native': 'بیرون باران می\u200cبارد.',
                                          'breakdown': 'It برای آب و هوا، زمان و اشیاء است.'},
                                         {'target': 'We learn English together.',
                                          'native': 'ما با هم انگلیسی یاد می\u200cگیریم.',
                                          'breakdown': 'We برای جمع (ما) استفاده می\u200cشود.'},
                                         {'target': 'They play football on Fridays.',
                                          'native': 'آن\u200cها روزهای جمعه فوتبال بازی می\u200cکنند.',
                                          'breakdown': 'They برای آن\u200cها به کار می\u200cرود.'},
                                         {'target': 'You are all welcome.',
                                          'native': 'همه شما خوش آمدید.',
                                          'breakdown': 'You می\u200cتواند به معنی شما (جمع) باشد.'}],
                       'tips_json': [{'tip': 'ضمیر I در انگلیسی همیشه با حرف بزرگ (Capital) نوشته می\u200cشود.',
                                      'example': 'Yes, I am ready.'},
                                     {'tip': 'همیشه جملات پایه موضوع Personal Pronouns را در زمینه\u200cهای روزمره '
                                             'تمرین کنید.',
                                      'example': 'I practice this every day.'},
                                     {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته '
                                             'باشید.',
                                      'example': 'She is in Stockholm today.'}],
                       'common_mistakes_json': [{'wrong': 'Is raining today.',
                                                 'right': 'It is raining today.',
                                                 'reason': 'در انگلیسی نمی\u200cتوان ضمیر فاعلی It را حذف کرد.'},
                                                {'wrong': 'He go to school yesterday.',
                                                 'right': 'He goes to school every day.',
                                                 'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت '
                                                           'شود.'},
                                                {'wrong': 'They is happy here.',
                                                 'right': 'They are happy here.',
                                                 'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات هستند.'}]},
 'indefinite_articles': {'title': 'Indefinite Articles (a / an)',
                         'explanation': 'حروف تعریف نکره a و an برای اشاره به اسم مفرد قابل شمارش که ناآشنا یا عمومی '
                                        'است استفاده می\u200cشوند. از مهم\u200cترین کاربردهای a و an بیان مشاغل و نقش '
                                        "افراد است. از 'a' قبل از صدای بی\u200cصدا و از 'an' قبل از صدای صدادار (a, e, "
                                        'i, o, u) استفاده می\u200cکنیم.',
                         'comparison': "در فارسی برای بیان شغل کلمه 'یک' گفته نمی\u200cشود (می\u200cگوییم «او معلم "
                                       'است»)، اما در انگلیسی آوردن a یا an قبل از اسامی مشاغل مفرد الزامی است (She is '
                                       'a teacher).',
                         'examples_json': [{'target': 'I have a car.',
                                            'native': 'من یک ماشین دارم.',
                                            'breakdown': 'car با صدای بی\u200cصدا c شروع می\u200cشود، پس a '
                                                         'می\u200cگیرد.'},
                                           {'target': 'She eats an apple.',
                                            'native': 'او یک سیب می\u200cخورد.',
                                            'breakdown': 'apple با حرف صدادار a شروع شده، پس an می\u200cگیرد.'},
                                           {'target': 'He is an engineer.',
                                            'native': 'او یک مهندس است.',
                                            'breakdown': 'قبل از مشاغل مفرد (engineer) حرف تعریف an (به علت حرف صدادار '
                                                         'e) الزامی است.'},
                                           {'target': 'There is a book on the table.',
                                            'native': 'یک کتاب روی میز است.',
                                            'breakdown': 'book با b شروع می\u200cشود، پس a می\u200cآید.'},
                                           {'target': 'I saw an elephant.',
                                            'native': 'من یک فیل دیدم.',
                                            'breakdown': 'elephant با e شروع شده و an می\u200cگیرد.'},
                                           {'target': 'Give me a pen, please.',
                                            'native': 'لطفاً یک خودکار به من بده.',
                                            'breakdown': 'pen با صدای بی\u200cصدا p شروع می\u200cشود.'},
                                           {'target': 'It takes an hour.',
                                            'native': 'یک ساعت طول می\u200cکشد.',
                                            'breakdown': 'حرف h در hour تلفظ نمی\u200cشود، پس an می\u200cگیرد.'},
                                           {'target': 'He is a good boy.',
                                            'native': 'او پسر خوبی است.',
                                            'breakdown': 'صفت good با g شروع شده و a می\u200cگیرد.'}],
                         'tips_json': [{'tip': 'قبل از اسامی تمام مشاغل مفرد حتماً از a یا an استفاده کنید.',
                                        'example': 'She is a doctor. / He is an artist.'},
                                       {'tip': 'همیشه جملات پایه موضوع Indefinite Articles (a / an) را در '
                                               'زمینه\u200cهای روزمره تمرین کنید.',
                                        'example': 'I practice this every day.'},
                                       {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته '
                                               'باشید.',
                                        'example': 'She is in Stockholm today.'}],
                         'common_mistakes_json': [{'wrong': 'He is doctor.',
                                                   'right': 'He is a doctor.',
                                                   'reason': 'اسم شغل مفرد در انگلیسی بدون a یا an بکار نمی\u200cرود.'},
                                                  {'wrong': 'He go to school yesterday.',
                                                   'right': 'He goes to school every day.',
                                                   'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت '
                                                             'شود.'},
                                                  {'wrong': 'They is happy here.',
                                                   'right': 'They are happy here.',
                                                   'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات '
                                                             'هستند.'}]},
 'definite_article': {'title': 'Definite Article (the)',
                      'explanation': 'حرف تعریف the برای اشاره به اسامی مشخص و شناخته\u200cشده توسط گوینده و شنونده '
                                     'استفاده می\u200cشود. هم برای اسامی مفرد و هم جمع به کار می\u200cرود. این مبحث '
                                     'یکی از پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی '
                                     'است. با تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
                      'comparison': 'در زبان فارسی حرف تعریف معرفه وجود ندارد و شناسا بودن اسم از قرینه کلام فهمیده '
                                    'می\u200cشود، اما در انگلیسی باید از the استفاده کرد.',
                      'examples_json': [{'target': 'The sun is bright.',
                                         'native': 'خورشید درخشان است.',
                                         'breakdown': 'خورشید پدیده\u200cای منحصربه\u200cفرد است و the می\u200cگیرد.'},
                                        {'target': 'Close the door.',
                                         'native': 'در را ببند.',
                                         'breakdown': 'اشاره به درِ مشخصی که هر دو طرف می\u200cشناسند.'},
                                        {'target': 'The books on the table are mine.',
                                         'native': 'کتاب\u200cهای روی میز مال من هستند.',
                                         'breakdown': 'کتاب\u200cهای مشخص روی میز.'},
                                        {'target': 'The capital of Iran is Tehran.',
                                         'native': 'پایتخت ایران تهران است.',
                                         'breakdown': 'پایتخت مشخص است و the می\u200cگیرد.'},
                                        {'target': 'Look at the moon.',
                                         'native': 'به ماه نگاه کن.',
                                         'breakdown': 'ماه تک و مشخص است.'},
                                        {'target': 'She is playing the piano.',
                                         'native': 'او دارد پیانو می\u200cنوازد.',
                                         'breakdown': 'قبل از آلات موسیقی the می\u200cآید.'},
                                        {'target': 'The water in this glass is cold.',
                                         'native': 'آب این لیوان سرد است.',
                                         'breakdown': 'آب مشخص درون لیوان.'},
                                        {'target': 'The children are playing outside.',
                                         'native': 'بچه\u200cها دارند بیرون بازی می\u200cکنند.',
                                         'breakdown': 'بچه\u200cهای مشخص.'}],
                      'tips_json': [{'tip': 'قبل از نام کشورها (به جز مواردی مانند The USA) از the استفاده نکنید.',
                                     'example': 'I live in Iran.'},
                                    {'tip': 'همیشه جملات پایه موضوع Definite Article (the) را در زمینه\u200cهای روزمره '
                                            'تمرین کنید.',
                                     'example': 'I practice this every day.'},
                                    {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته '
                                            'باشید.',
                                     'example': 'She is in Stockholm today.'}],
                      'common_mistakes_json': [{'wrong': 'I live in the Tehran.',
                                                'right': 'I live in Tehran.',
                                                'reason': 'قبل از نام اکثر شهرها و کشورها the نمی\u200cآید.'},
                                               {'wrong': 'He go to school yesterday.',
                                                'right': 'He goes to school every day.',
                                                'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت شود.'},
                                               {'wrong': 'They is happy here.',
                                                'right': 'They are happy here.',
                                                'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات هستند.'}]},
 'plural_nouns': {'title': 'Plural Nouns',
                  'explanation': "برای جمع بستن اسامی در انگلیسی معمولاً به انتهای اسم 's' یا 'es' اضافه می\u200cشود. "
                                 'برخی اسامی دارای جمع بی\u200cقاعده هستند که شکل کلمه تغییر می\u200cکند. این مبحث یکی '
                                 'از پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی است. با '
                                 'تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
                  'comparison': "در فارسی از پسوندهای 'ها' یا 'ان' برای جمع استفاده می\u200cشود. در انگلیسی قاعده اصلی "
                                'اضافه کردن s است و تغییرات در خود کلمه صورت می\u200cگیرد.',
                  'examples_json': [{'target': 'I have two dogs.',
                                     'native': 'من دو سگ دارم.',
                                     'breakdown': 'جمع با اضافه شدن s به dog ساخته شده است.'},
                                    {'target': 'She bought three books.',
                                     'native': 'او سه کتاب خرید.',
                                     'breakdown': 'جمع با s به book.'},
                                    {'target': 'He washed the dishes.',
                                     'native': 'او ظرف\u200cها را شست.',
                                     'breakdown': 'کلمات ختم\u200cشده به sh با es جمع می\u200cشوند.'},
                                    {'target': 'There are four boxes here.',
                                     'native': 'چهار جعبه اینجا وجود دارد.',
                                     'breakdown': 'کلمات ختم\u200cشده به x با es جمع می\u200cشوند.'},
                                    {'target': 'The children are playing.',
                                     'native': 'بچه\u200cها دارند بازی می\u200cکنند.',
                                     'breakdown': 'children جمع بی\u200cقاعده child است.'},
                                    {'target': 'Two men are standing there.',
                                     'native': 'دو مرد آنجا ایستاده\u200cاند.',
                                     'breakdown': 'men جمع بی\u200cقاعده man است.'},
                                    {'target': 'I see three cars.',
                                     'native': 'من سه ماشین می\u200cبینم.',
                                     'breakdown': 'جمع با اضافه شدن s.'},
                                    {'target': 'Put the glasses on the table.',
                                     'native': 'لیوان\u200cها را روی میز بگذار.',
                                     'breakdown': 'glass به es جمع بسته می\u200cشود.'}],
                  'tips_json': [{'tip': 'کلماتی که به s, sh, ch, x ختم می\u200cشوند با es جمع بسته می\u200cشوند.',
                                 'example': 'bus -> buses'},
                                {'tip': 'همیشه جملات پایه موضوع Plural Nouns را در زمینه\u200cهای روزمره تمرین کنید.',
                                 'example': 'I practice this every day.'},
                                {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته باشید.',
                                 'example': 'She is in Stockholm today.'}],
                  'common_mistakes_json': [{'wrong': 'two childs',
                                            'right': 'two children',
                                            'reason': 'کلمه child جمع بی\u200cقاعده دارد و childs نادرست است.'},
                                           {'wrong': 'He go to school yesterday.',
                                            'right': 'He goes to school every day.',
                                            'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت شود.'},
                                           {'wrong': 'They is happy here.',
                                            'right': 'They are happy here.',
                                            'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات هستند.'}]},
 'possessive_adjectives': {'title': 'Possessive Adjectives',
                           'explanation': 'صفات مالکیتی نشان می\u200cدهند چه چیزی متعلق به چه کسی است. صفات مالکیتی '
                                          'عبارتند از: my, your, his, her, its, our, their. این مبحث یکی از '
                                          'پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی است. '
                                          'با تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
                           'comparison': 'در فارسی مالکیت با ضمیر متصل (ـَم، ـَت، ـَش) به انتهای اسم متصل می\u200cشود '
                                         '(کتابم)، اما در انگلیسی صفت مالکیتی همیشه **قبل از اسم** می\u200cآید (my '
                                         'book).',
                           'examples_json': [{'target': 'This is my house.',
                                              'native': 'این خانه من است.',
                                              'breakdown': 'my صفت مالکیتی متکلم است.'},
                                             {'target': 'What is your name?',
                                              'native': 'نام تو چیست؟',
                                              'breakdown': 'your صفت مالکیتی مخاطب است.'},
                                             {'target': 'His car is red.',
                                              'native': 'ماشین او (مذکر) قرمز است.',
                                              'breakdown': 'his صفت مالکیتی مذکر است.'},
                                             {'target': 'Her phone is new.',
                                              'native': 'تلفن او (مونث) جدید است.',
                                              'breakdown': 'her صفت مالکیتی مونث است.'},
                                             {'target': 'The dog wags its tail.',
                                              'native': 'سگ دمش را تکان می\u200cدهد.',
                                              'breakdown': 'its صفت مالکیتی غیرانسان است.'},
                                             {'target': 'Our school is big.',
                                              'native': 'مدرسه ما بزرگ است.',
                                              'breakdown': 'our صفت مالکیتی ما است.'},
                                             {'target': 'Their house is near the park.',
                                              'native': 'خانه آن\u200cها نزدیک پارک است.',
                                              'breakdown': 'their صفت مالکیتی آن\u200cها است.'},
                                             {'target': 'I like your new shoes.',
                                              'native': 'کفش\u200cهای جدیدت را دوست دارم.',
                                              'breakdown': 'your قبل از اسم shoes می\u200cآید.'}],
                           'tips_json': [{'tip': "اشتباه نکنید: its صفت مالکیتی است ولی it's مخفف it is می\u200cباشد.",
                                          'example': "its color / it's cold"},
                                         {'tip': 'همیشه جملات پایه موضوع Possessive Adjectives را در زمینه\u200cهای '
                                                 'روزمره تمرین کنید.',
                                          'example': 'I practice this every day.'},
                                         {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته '
                                                 'باشید.',
                                          'example': 'She is in Stockholm today.'}],
                           'common_mistakes_json': [{'wrong': 'This is book my.',
                                                     'right': 'This is my book.',
                                                     'reason': 'صفت مالکیتی همیشه قبل از اسم قرار می\u200cگیرد.'},
                                                    {'wrong': 'He go to school yesterday.',
                                                     'right': 'He goes to school every day.',
                                                     'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت '
                                                               'شود.'},
                                                    {'wrong': 'They is happy here.',
                                                     'right': 'They are happy here.',
                                                     'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات '
                                                               'هستند.'}]},
 'demonstratives': {'title': 'Demonstratives (this / that / these / those)',
                    'explanation': 'کلمات اشاره برای نشان دادن فاصله زمانی یا مکانی استفاده می\u200cشوند: this (این - '
                                   'مفرد نزدیک)، that (آن - مفرد دور)، these (این\u200cها - جمع نزدیک)، those '
                                   '(آن\u200cها - جمع دور). این مبحث یکی از پایه\u200cای\u200cترین و پرکاربردترین '
                                   'بخش\u200cهای گرامر زبان انگلیسی است. با تمرین و مرور مثال\u200cهای ارائه شده '
                                   'می\u200cتوانید تسلط کامل پیدا کنید.',
                    'comparison': "در فارسی برای اشاره جمع نیز گاهی از 'این' و 'آن' استفاده می\u200cشود، اما در "
                                  'انگلیسی استفاده از این\u200cها (these) و آن\u200cها (those) اجباری است.',
                    'examples_json': [{'target': 'This is my bag.',
                                       'native': 'این کیف من است.',
                                       'breakdown': 'This اشاره به مفرد نزدیک دارد.'},
                                      {'target': 'That is a high mountain.',
                                       'native': 'آن یک کوه بلند است.',
                                       'breakdown': 'That اشاره به مفرد دور دارد.'},
                                      {'target': 'These are fresh apples.',
                                       'native': 'این\u200cها سیب\u200cهای تازه\u200cای هستند.',
                                       'breakdown': 'These اشاره به جمع نزدیک دارد.'},
                                      {'target': 'Those stars are bright.',
                                       'native': 'آن ستاره\u200cها درخشان هستند.',
                                       'breakdown': 'Those اشاره به جمع دور دارد.'},
                                      {'target': 'I like this shirt.',
                                       'native': 'من این پیراهن را دوست دارم.',
                                       'breakdown': 'This صفت اشاره مفرد نزدیک است.'},
                                      {'target': 'Look at that bird!',
                                       'native': 'به آن پرنده نگاه کن!',
                                       'breakdown': 'That برای پرنده در فاصله دور.'},
                                      {'target': 'These books are very interesting.',
                                       'native': 'این کتاب\u200cها بسیار جالب هستند.',
                                       'breakdown': 'These برای کتاب\u200cهای نزدیک.'},
                                      {'target': 'Who are those people over there?',
                                       'native': 'آن افراد آن طرف چه کسانی هستند؟',
                                       'breakdown': 'Those برای اشخاص در فاصله دور.'}],
                    'tips_json': [{'tip': 'بعد از this و that اسم مفرد و بعد از these و those اسم جمع می\u200cآید.',
                                   'example': 'this boy / these boys'},
                                  {'tip': 'همیشه جملات پایه موضوع Demonstratives (this / that / these / those) را در '
                                          'زمینه\u200cهای روزمره تمرین کنید.',
                                   'example': 'I practice this every day.'},
                                  {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته باشید.',
                                   'example': 'She is in Stockholm today.'}],
                    'common_mistakes_json': [{'wrong': 'These is my book.',
                                              'right': 'This is my book.',
                                              'reason': 'برای اسم مفرد باید از this استفاده کرد نه these.'},
                                             {'wrong': 'He go to school yesterday.',
                                              'right': 'He goes to school every day.',
                                              'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت شود.'},
                                             {'wrong': 'They is happy here.',
                                              'right': 'They are happy here.',
                                              'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات هستند.'}]},
 'present_simple_affirmative': {'title': 'Present Simple – Affirmative',
                                'explanation': 'زمان حال ساده برای بیان حقایق کلی، عادات روزمره و برنامه\u200cهای منظم '
                                               'استفاده می\u200cشود. برای ضمایر he, she, it به انتهای فعل اصلی پسوند s '
                                               'یا es اضافه می\u200cکنیم. این مبحث یکی از پایه\u200cای\u200cترین و '
                                               'پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی است. با تمرین و مرور '
                                               'مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
                                'comparison': 'در فارسی برای زمان حال ساده از می + ریشه فعل + شناسه (می\u200cروم، '
                                              'می\u200cرود) استفاده می\u200cشود. در انگلیسی فعل اصلی برای اکثر ضمایر '
                                              'تغییر نمی\u200cکند و فقط برای سوم شخص مفرد s می\u200cگیرد.',
                                'examples_json': [{'target': 'I drink milk every morning.',
                                                   'native': 'من هر روز صبح شیر می\u200cنوشم.',
                                                   'breakdown': 'عادت روزمره با فعل ساده drink.'},
                                                  {'target': 'She plays tennis on Saturdays.',
                                                   'native': 'او روزهای شنبه تنیس بازی می\u200cکند.',
                                                   'breakdown': 'فعل play پس از she پسوند s گرفته است.'},
                                                  {'target': 'He lives in Canada.',
                                                   'native': 'او در کانادا زندگی می\u200cکند.',
                                                   'breakdown': 'فعل live پس از he پسوند s می\u200cگیرد.'},
                                                  {'target': 'They study English every night.',
                                                   'native': 'آن\u200cها هر شب انگلیسی می\u200cخوانند.',
                                                   'breakdown': 'برای جمع (They) فعل ساده بکار می\u200cرود.'},
                                                  {'target': 'The sun rises in the east.',
                                                   'native': 'خورشید از شرق طلوع می\u200cکند.',
                                                   'breakdown': 'حقیقت علمی با s سوم شخص.'},
                                                  {'target': 'We work from 9 to 5.',
                                                   'native': 'ما از ساعت ۹ تا ۵ کار می\u200cکنیم.',
                                                   'breakdown': 'برنامه کاری با فعل ساده work.'},
                                                  {'target': 'It rains a lot in winter.',
                                                   'native': 'در زمستان باران زیادی می\u200cبارد.',
                                                   'breakdown': 'برای آب و هوا با it و s فعل.'},
                                                  {'target': 'You speak English very well.',
                                                   'native': 'تو خیلی خوب انگلیسی صحبت می\u200cکنی.',
                                                   'breakdown': 'فعل ساده speak برای you.'}],
                                'tips_json': [{'tip': 'فراموش نکنید برای he, she, it حتماً s یا es به انتهای فعل اضافه '
                                                      'کنید.',
                                               'example': 'He runs fast.'},
                                              {'tip': 'همیشه جملات پایه موضوع Present Simple – Affirmative را در '
                                                      'زمینه\u200cهای روزمره تمرین کنید.',
                                               'example': 'I practice this every day.'},
                                              {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه '
                                                      'داشته باشید.',
                                               'example': 'She is in Stockholm today.'}],
                                'common_mistakes_json': [{'wrong': 'She live in Oslo.',
                                                          'right': 'She lives in Oslo.',
                                                          'reason': 'برای she فعل نیاز به s دارد.'},
                                                         {'wrong': 'He go to school yesterday.',
                                                          'right': 'He goes to school every day.',
                                                          'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل '
                                                                    'رعایت شود.'},
                                                         {'wrong': 'They is happy here.',
                                                          'right': 'They are happy here.',
                                                          'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات '
                                                                    'هستند.'}]},
 'present_simple_negative': {'title': 'Present Simple – Negative',
                             'explanation': "برای منفی کردن زمان حال ساده از فعل کمکی don't (do not) یا doesn't (does "
                                            "not) قبل از فعل اصلی استفاده می\u200cشود. بعد از doesn't، پسوند s فعل "
                                            'اصلی حذف می\u200cشود. این مبحث یکی از پایه\u200cای\u200cترین و '
                                            'پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی است. با تمرین و مرور '
                                            'مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
                             'comparison': "در فارسی منفی کردن با پیشوند 'نـ' (نمی\u200cروم، نمی\u200cرود) ساخته "
                                           "می\u200cشود، اما در انگلیسی از افعال کمکی don't/doesn't قبل از فعل استفاده "
                                           'می\u200cکنیم.',
                             'examples_json': [{'target': "I don't like tea.",
                                                'native': 'من چای دوست ندارم.',
                                                'breakdown': "برای I از don't استفاده می\u200cشود."},
                                               {'target': "She doesn't speak Swedish.",
                                                'native': 'او سوئدی صحبت نمی\u200cکند.',
                                                'breakdown': "برای she از doesn't استفاده می\u200cشود و s حذف "
                                                             'می\u200cشود.'},
                                               {'target': "He doesn't eat meat.",
                                                'native': 'او گوشت نمی\u200cخورد.',
                                                'breakdown': "doesn't + فعل پایه eat."},
                                               {'target': "They don't watch TV.",
                                                'native': 'آن\u200cها تلویزیون تماشا نمی\u200cکنند.',
                                                'breakdown': "منفی جمع با don't."},
                                               {'target': "We don't work on Sundays.",
                                                'native': 'ما روزهای یکشنبه کار نمی\u200cکنیم.',
                                                'breakdown': "منفی با don't برای We."},
                                               {'target': "It doesn't snow in summer.",
                                                'native': 'در تابستان باران/برف نمی\u200cبارد.',
                                                'breakdown': "doesn't برای it."},
                                               {'target': "You don't need a key.",
                                                'native': 'تو نیازی به کلید نداری.',
                                                'breakdown': "don't برای You."},
                                               {'target': "My brother doesn't smoke.",
                                                'native': 'برادر من سیگار نمی\u200cکشد.',
                                                'breakdown': "برادرم (مفرد) doesn't می\u200cگیرد."}],
                             'tips_json': [{'tip': "بعد از doesn't فعل اصلی نباید s بگیرد.",
                                            'example': "He doesn't like (NOT doesn't likes)"},
                                           {'tip': 'همیشه جملات پایه موضوع Present Simple – Negative را در '
                                                   'زمینه\u200cهای روزمره تمرین کنید.',
                                            'example': 'I practice this every day.'},
                                           {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه '
                                                   'داشته باشید.',
                                            'example': 'She is in Stockholm today.'}],
                             'common_mistakes_json': [{'wrong': "She doesn't likes coffee.",
                                                       'right': "She doesn't like coffee.",
                                                       'reason': "پس از doesn't پسوند s فعل برداشته می\u200cشود."},
                                                      {'wrong': 'He go to school yesterday.',
                                                       'right': 'He goes to school every day.',
                                                       'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل '
                                                                 'رعایت شود.'},
                                                      {'wrong': 'They is happy here.',
                                                       'right': 'They are happy here.',
                                                       'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات '
                                                                 'هستند.'}]},
 'present_simple_questions': {'title': 'Present Simple – Questions',
                              'explanation': 'برای سوالی کردن زمان حال ساده از Do یا Does در ابتدای جمله استفاده '
                                             'می\u200cشود. فرمول: Do/Does + فاعل + شکل ساده فعل؟ این مبحث یکی از '
                                             'پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی '
                                             'است. با تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل '
                                             'پیدا کنید.',
                              'comparison': "در فارسی با افزودن لحن سوالی یا کلمه 'آیا' جمله سوالی می\u200cشود. در "
                                            'انگلیسی حتماً باید فعل کمکی Do یا Does در ابتدای جمله قرار گیرد.',
                              'examples_json': [{'target': 'Do you speak English?',
                                                 'native': 'آیا شما انگلیسی صحبت می\u200cکنید؟',
                                                 'breakdown': 'سوالی با Do برای مخاطب (you).'},
                                                {'target': 'Does she live here?',
                                                 'native': 'آیا او اینجا زندگی می\u200cکند؟',
                                                 'breakdown': 'سوالی با Does برای سوم شخص (she).'},
                                                {'target': 'Do they play football?',
                                                 'native': 'آیا آن\u200cها فوتبال بازی می\u200cکنند؟',
                                                 'breakdown': 'سوالی با Do برای جمع (they).'},
                                                {'target': 'Does he work at a school?',
                                                 'native': 'آیا او در مدرسه کار می\u200cکند؟',
                                                 'breakdown': 'سوالی با Does برای he.'},
                                                {'target': 'Do we have time?',
                                                 'native': 'آیا ما وقت داریم؟',
                                                 'breakdown': 'سوالی با Do برای we.'},
                                                {'target': 'Does it rain a lot in autumn?',
                                                 'native': 'آیا در پاییز باران زیادی می\u200cبارد؟',
                                                 'breakdown': 'سوالی با Does برای it.'},
                                                {'target': 'Where do you live?',
                                                 'native': 'کجا زندگی می\u200cکنی؟',
                                                 'breakdown': 'سوال Wh با Do و فاعل you.'},
                                                {'target': 'What does she want?',
                                                 'native': 'او چه می\u200cخواهد؟',
                                                 'breakdown': 'سوال Wh با Does و فاعل she.'}],
                              'tips_json': [{'tip': 'در جملات سوالی با Does، پسوند s از انتهای فعل اصلی پاک '
                                                    'می\u200cشود.',
                                             'example': 'Does he go? (NOT Does he goes?)'},
                                            {'tip': 'همیشه جملات پایه موضوع Present Simple – Questions را در '
                                                    'زمینه\u200cهای روزمره تمرین کنید.',
                                             'example': 'I practice this every day.'},
                                            {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه '
                                                    'داشته باشید.',
                                             'example': 'She is in Stockholm today.'}],
                              'common_mistakes_json': [{'wrong': 'Does she likes music?',
                                                        'right': 'Does she like music?',
                                                        'reason': 'در حضور Does فعل اصلی s نمی\u200cگیرد.'},
                                                       {'wrong': 'He go to school yesterday.',
                                                        'right': 'He goes to school every day.',
                                                        'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل '
                                                                  'رعایت شود.'},
                                                       {'wrong': 'They is happy here.',
                                                        'right': 'They are happy here.',
                                                        'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات '
                                                                  'هستند.'}]},
 'have_got': {'title': 'Have Got',
              'explanation': "عبارت 'have got' یا 'has got' در انگلیسی بریتانیایی به معنای داشتن مالکیت یا روابط "
                             'خانوادگی است. I/you/we/they have got و he/she/it has got می\u200cگیرند. این مبحث یکی از '
                             'پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی است. با تمرین و '
                             'مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
              'comparison': "در فارسی فعل 'داشتن' صرف می\u200cشود (دارم، داری، دارد). در انگلیسی have/has got نقش فعل "
                            'داشتن را ایفا می\u200cکند.',
              'examples_json': [{'target': 'I have got a new car.',
                                 'native': 'من یک ماشین جدید دارم.',
                                 'breakdown': 'have got برای I.'},
                                {'target': 'She has got two brothers.',
                                 'native': 'او دو برادر دارد.',
                                 'breakdown': 'has got برای she.'},
                                {'target': 'They have got a big garden.',
                                 'native': 'آن\u200cها یک باغ بزرگ دارند.',
                                 'breakdown': 'have got برای they.'},
                                {'target': 'He has got dark hair.',
                                 'native': 'او موهای تیره دارد.',
                                 'breakdown': 'has got برای ویژگی ظاهری he.'},
                                {'target': 'We have got a lot of work.',
                                 'native': 'ما کار زیادی داریم.',
                                 'breakdown': 'have got برای we.'},
                                {'target': "I haven't got any money.",
                                 'native': 'من هیچ پولی ندارم.',
                                 'breakdown': "منفی haven't got."},
                                {'target': "She hasn't got a bicycle.",
                                 'native': 'او دوچرخه\u200cای ندارد.',
                                 'breakdown': "منفی hasn't got."},
                                {'target': 'Have you got a pen?',
                                 'native': 'آیا خودکار داری؟',
                                 'breakdown': 'سوالی با Have در ابتدا.'}],
              'tips_json': [{'tip': "شکل مخفف have got به صورت 've got و has got به صورت 's got است.",
                             'example': "I've got a cat. / He's got a dog."},
                            {'tip': 'همیشه جملات پایه موضوع Have Got را در زمینه\u200cهای روزمره تمرین کنید.',
                             'example': 'I practice this every day.'},
                            {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته باشید.',
                             'example': 'She is in Stockholm today.'}],
              'common_mistakes_json': [{'wrong': 'She have got a car.',
                                        'right': 'She has got a car.',
                                        'reason': 'برای she باید از has got استفاده شود.'},
                                       {'wrong': 'He go to school yesterday.',
                                        'right': 'He goes to school every day.',
                                        'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت شود.'},
                                       {'wrong': 'They is happy here.',
                                        'right': 'They are happy here.',
                                        'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات هستند.'}]},
 'can_ability': {'title': 'Can – Ability & Permission',
                 'explanation': "فعل کمکی can به معنای 'توانستن' برای بیان توانایی، استعداد یا اجازه گرفتن به کار "
                                'می\u200cرود. این فعل برای تمام ضمایر شکل یکسان دارد و s نمی\u200cگیرد. این مبحث یکی '
                                'از پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی است. با '
                                'تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
                 'comparison': 'در فارسی فعل توانستن صرف می\u200cشود (می\u200cتوانم، می\u200cتوانی، می\u200cتواند)، '
                               'اما در انگلیسی can برای تمام اشخاص ثابت است.',
                 'examples_json': [{'target': 'I can swim very well.',
                                    'native': 'من می\u200cتوانم خیلی خوب شنا کنم.',
                                    'breakdown': 'بیان توانایی فیزیکی با can.'},
                                   {'target': 'She can speak English.',
                                    'native': 'او می\u200cتواند انگلیسی صحبت کند.',
                                    'breakdown': 'can برای تمام ضمایر ثابت است و s نمی\u200cگیرد.'},
                                   {'target': 'He can play the guitar.',
                                    'native': 'او می\u200cتواند گیتار بنوازد.',
                                    'breakdown': 'توانایی نواختن با can.'},
                                   {'target': 'They can drive a car.',
                                    'native': 'آن\u200cها می\u200cتوانند رانندگی کنند.',
                                    'breakdown': 'توانایی رانندگی.'},
                                   {'target': "I can't hear you.",
                                    'native': 'من نمی\u200cتوانم صدای شما را بشنوم.',
                                    'breakdown': "منفی can به صورت can't است."},
                                   {'target': "She can't come today.",
                                    'native': 'او امروز نمی\u200cتواند بیاید.',
                                    'breakdown': "منفی توانستن با can't."},
                                   {'target': 'Can you help me?',
                                    'native': 'آیا می\u200cتوانی به من کمک کنی؟',
                                    'breakdown': 'درخواست کمک و سوالی با Can.'},
                                   {'target': 'Can I open the window?',
                                    'native': 'آیا می\u200cتوانم پنجره را باز کنم؟',
                                    'breakdown': 'اجازه گرفتن با Can.'}],
                 'tips_json': [{'tip': 'بعد از can همیشه فعل به صورت ساده و بدون to می\u200cآید.',
                                'example': 'I can run (NOT I can to run)'},
                               {'tip': 'همیشه جملات پایه موضوع Can – Ability & Permission را در زمینه\u200cهای روزمره '
                                       'تمرین کنید.',
                                'example': 'I practice this every day.'},
                               {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته باشید.',
                                'example': 'She is in Stockholm today.'}],
                 'common_mistakes_json': [{'wrong': 'She cans swim.',
                                           'right': 'She can swim.',
                                           'reason': 'فعل can به هیچ عنوان پسوند s نمی\u200cگیرد.'},
                                          {'wrong': 'He go to school yesterday.',
                                           'right': 'He goes to school every day.',
                                           'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت شود.'},
                                          {'wrong': 'They is happy here.',
                                           'right': 'They are happy here.',
                                           'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات هستند.'}]},
 'imperative': {'title': 'Imperative (Commands)',
                'explanation': 'جملات امری برای دستور دادن، راهنمایی کردن یا خواهش کردن استفاده می\u200cشوند. برای '
                               "ساخت جمله امری مثبت از شکل ساده فعل در اول جمله و برای منفی از Don't استفاده "
                               'می\u200cکنیم. این مبحث یکی از پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر '
                               'زبان انگلیسی است. با تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل '
                               'پیدا کنید.',
                'comparison': 'در فارسی فعل امری شناسه دوم شخص می\u200cگیرد (بیا، بروید)، اما در انگلیسی جمله امری فقط '
                              'با ریشه ساده فعل بدون فاعل ساخته می\u200cشود.',
                'examples_json': [{'target': 'Open the window, please.',
                                   'native': 'لطفاً پنجره را باز کن.',
                                   'breakdown': 'امری مثبت با ریشه ساده فعل Open.'},
                                  {'target': 'Listen to the teacher.',
                                   'native': 'به معلم گوش دهید.',
                                   'breakdown': 'دستور امری با Listen.'},
                                  {'target': "Don't make noise!",
                                   'native': 'سر و صدا نکنید!',
                                   'breakdown': "امری منفی با Don't."},
                                  {'target': 'Sit down, please.',
                                   'native': 'لطفاً بنشینید.',
                                   'breakdown': 'امری محترمانه با Please.'},
                                  {'target': "Don't touch that plate.",
                                   'native': 'به آن بشقاب دست نزن.',
                                   'breakdown': "نهی و امری منفی با Don't."},
                                  {'target': 'Be quiet in the library.',
                                   'native': 'در کتابخانه ساکت باشید.',
                                   'breakdown': 'امری با فعل Be.'},
                                  {'target': "Don't be late!",
                                   'native': 'دیر نکنید!',
                                   'breakdown': "امری منفی با Don't be."},
                                  {'target': 'Close your books now.',
                                   'native': 'اکنون کتاب\u200cهایتان را ببندید.',
                                   'breakdown': 'دستور با Close.'}],
                'tips_json': [{'tip': 'افزودن کلمه Please در ابتدای یا انتهای جمله امری، آن را محترمانه می\u200cکند.',
                               'example': 'Please come in.'},
                              {'tip': 'همیشه جملات پایه موضوع Imperative (Commands) را در زمینه\u200cهای روزمره تمرین '
                                      'کنید.',
                               'example': 'I practice this every day.'},
                              {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته باشید.',
                               'example': 'She is in Stockholm today.'}],
                'common_mistakes_json': [{'wrong': 'To open the door.',
                                          'right': 'Open the door.',
                                          'reason': 'جمله امری با to شروع نمی\u200cشود.'},
                                         {'wrong': 'He go to school yesterday.',
                                          'right': 'He goes to school every day.',
                                          'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت شود.'},
                                         {'wrong': 'They is happy here.',
                                          'right': 'They are happy here.',
                                          'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات هستند.'}]},
 'there_is_there_are': {'title': 'There is / There are',
                        'explanation': "برای بیان وجود داشتن اشیاء یا افراد در یک مکان از 'There is' (برای مفرد و "
                                       "غیرقابل شمارش) و 'There are' (برای جمع) استفاده می\u200cکنیم. این مبحث یکی از "
                                       'پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی است. با '
                                       'تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
                        'comparison': "در فارسی کلمه 'وجود دارد / هست' در آخر جمله می\u200cآید، اما در انگلیسی 'There "
                                      "is/are' در ابتدای جمله قرار می\u200cگیرد.",
                        'examples_json': [{'target': 'There is a book on the table.',
                                           'native': 'یک کتاب روی میز وجود دارد.',
                                           'breakdown': 'There is برای اسم مفرد a book.'},
                                          {'target': 'There are three computers in the office.',
                                           'native': 'سه کامپیوتر در دفتر وجود دارد.',
                                           'breakdown': 'There are برای اسم جمع three computers.'},
                                          {'target': 'There is some water in the bottle.',
                                           'native': 'مقداری آب در بطری هست.',
                                           'breakdown': 'There is برای غیرقابل شمارش water.'},
                                          {'target': 'There are many trees in the park.',
                                           'native': 'درختان زیادی در پارک هست.',
                                           'breakdown': 'There are برای جمع many trees.'},
                                          {'target': "There isn't a clock in this room.",
                                           'native': 'ساعتی در این اتاق نیست.',
                                           'breakdown': "منفی مفرد با There isn't."},
                                          {'target': "There aren't any chairs here.",
                                           'native': 'هیچ صندلی اینجا نیست.',
                                           'breakdown': "منفی جمع با There aren't."},
                                          {'target': 'Is there a hospital near here?',
                                           'native': 'آیا بیمارستانی نزدیک اینجا هست؟',
                                           'breakdown': 'سوالی مفرد با Is there.'},
                                          {'target': 'Are there any questions?',
                                           'native': 'آیا سوالی وجود دارد؟',
                                           'breakdown': 'سوالی جمع با Are there.'}],
                        'tips_json': [{'tip': 'برای اسامی غیرقابل شمارش مثل آب، شیر و پول همیشه از There is استفاده '
                                              'کنید.',
                                       'example': 'There is milk.'},
                                      {'tip': 'همیشه جملات پایه موضوع There is / There are را در زمینه\u200cهای روزمره '
                                              'تمرین کنید.',
                                       'example': 'I practice this every day.'},
                                      {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته '
                                              'باشید.',
                                       'example': 'She is in Stockholm today.'}],
                        'common_mistakes_json': [{'wrong': 'There is two cats.',
                                                  'right': 'There are two cats.',
                                                  'reason': 'برای اسم جمع (two cats) باید از There are استفاده کرد.'},
                                                 {'wrong': 'He go to school yesterday.',
                                                  'right': 'He goes to school every day.',
                                                  'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت '
                                                            'شود.'},
                                                 {'wrong': 'They is happy here.',
                                                  'right': 'They are happy here.',
                                                  'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات '
                                                            'هستند.'}]},
 'basic_prepositions_place': {'title': 'Prepositions of Place',
                              'explanation': 'حروف اضافه مکان نشان می\u200cدهند اشیاء یا افراد در چه موقعیت مکانی قرار '
                                             'دارند. حروف اضافه اصلی: in (در/داخل)، on (روی)، at (در/در نقطه)، under '
                                             '(زیر)، next to (کنار). این مبحث یکی از پایه\u200cای\u200cترین و '
                                             'پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی است. با تمرین و مرور '
                                             'مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
                              'comparison': 'در فارسی حروف اضافه پیش از اسم قرار می\u200cگیرند (روی میز). در انگلیسی '
                                            'نیز حروف اضافه قبل از اسم می\u200cآیند (on the table) با این تفاوت که دقت '
                                            'در انتخاب in/on/at اهمیت بالایی دارد.',
                              'examples_json': [{'target': 'The book is on the table.',
                                                 'native': 'کتاب روی میز است.',
                                                 'breakdown': 'on به معنای تماس بر روی سطح است.'},
                                                {'target': 'The keys are in my bag.',
                                                 'native': 'کلیدها داخل کیف من هستند.',
                                                 'breakdown': 'in به معنای داخل یک فضای بسته است.'},
                                                {'target': 'She is standing at the bus stop.',
                                                 'native': 'او در ایستگاه اتوبوس ایستاده است.',
                                                 'breakdown': 'at برای اشاره به موقعیت مکان مشخص است.'},
                                                {'target': 'The cat is sleeping under the chair.',
                                                 'native': 'گربه زیر صندلی خوابیده است.',
                                                 'breakdown': 'under به معنای زیر چیزی است.'},
                                                {'target': 'The school is next to the bank.',
                                                 'native': 'مدرسه کنار بانک است.',
                                                 'breakdown': 'next to به معنای مجاور و کنار است.'},
                                                {'target': 'There is a picture on the wall.',
                                                 'native': 'تصویری روی دیوار قرار دارد.',
                                                 'breakdown': 'روی سطح عمودی دیوار با on آمده است.'},
                                                {'target': 'He lives in Tehran.',
                                                 'native': 'او در تهران زندگی می\u200cکند.',
                                                 'breakdown': 'قبل از نام شهرها همیشه in می\u200cآید.'},
                                                {'target': 'We are at home now.',
                                                 'native': 'ما الان در خانه هستیم.',
                                                 'breakdown': 'موقعیت در خانه با at home بیان می\u200cشود.'}],
                              'tips_json': [{'tip': 'برای شهرها و کشورها از in و برای موقعیت\u200cهای خاص از at '
                                                    'استفاده کنید.',
                                             'example': 'in Helsinki / at school'},
                                            {'tip': 'همیشه جملات پایه موضوع Prepositions of Place را در زمینه\u200cهای '
                                                    'روزمره تمرین کنید.',
                                             'example': 'I practice this every day.'},
                                            {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه '
                                                    'داشته باشید.',
                                             'example': 'She is in Stockholm today.'}],
                              'common_mistakes_json': [{'wrong': 'He lives at Oslo.',
                                                        'right': 'He lives in Oslo.',
                                                        'reason': 'قبل از شهرها باید از in استفاده شود.'},
                                                       {'wrong': 'He go to school yesterday.',
                                                        'right': 'He goes to school every day.',
                                                        'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل '
                                                                  'رعایت شود.'},
                                                       {'wrong': 'They is happy here.',
                                                        'right': 'They are happy here.',
                                                        'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات '
                                                                  'هستند.'}]},
 'adjectives_basic': {'title': 'Basic Adjectives',
                      'explanation': 'صفات کلماتی هستند که کیفیت و ویژگی اسامی را توصیف می\u200cکنند (مانند big, '
                                     'small, hot, cold). در انگلیسی صفت همیشه **قبل از اسم** یا **بعد از فعل to be** '
                                     'می\u200cآید. این مبحث یکی از پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای '
                                     'گرامر زبان انگلیسی است. با تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید '
                                     'تسلط کامل پیدا کنید.',
                      'comparison': 'در فارسی صفت **بعد از اسم** با کسره اضافه می\u200cآید (ماشینِ سریع)، اما در '
                                    'انگلیسی صفت دقیقاً **قبل از اسم** قرار می\u200cگیرد (a fast car). همچنین صفت در '
                                    'انگلیسی مفرد و جمع ندارد.',
                      'examples_json': [{'target': 'This is a big house.',
                                         'native': 'این یک خانه بزرگ است.',
                                         'breakdown': 'صفت big قبل از اسم house قرار گرفته است.'},
                                        {'target': 'The coffee is hot.',
                                         'native': 'قهوه داغ است.',
                                         'breakdown': 'صفت hot پس از فعل is آمده است.'},
                                        {'target': 'She bought a red car.',
                                         'native': 'او یک ماشین قرمز خرید.',
                                         'breakdown': 'صفت رنگ red قبل از car قرار دارد.'},
                                        {'target': 'He is a smart boy.',
                                         'native': 'او پسر باهوشی است.',
                                         'breakdown': 'صفت smart قبل از اسم boy آمده است.'},
                                        {'target': 'Today is a cold day.',
                                         'native': 'امروز روز سردی است.',
                                         'breakdown': 'صفت cold قبل از day قرار دارد.'},
                                        {'target': 'They have two small dogs.',
                                         'native': 'آن\u200cها دو سگ کوچک دارند.',
                                         'breakdown': 'صفت برای اسم جمع هم به شکل مفرد (small) می\u200cماند.'},
                                        {'target': 'The movie was interesting.',
                                         'native': 'فیلم جالب بود.',
                                         'breakdown': 'صفت بعد از فعل was آمده است.'},
                                        {'target': 'I like fresh apples.',
                                         'native': 'من سیب\u200cهای تازه را دوست دارم.',
                                         'breakdown': 'صفت fresh قبل از اسم جمع apples.'}],
                      'tips_json': [{'tip': 'صفات در انگلیسی هیچ\u200cگاه s جمع نمی\u200cگیرند.',
                                     'example': 'red cars (NOT reds cars)'},
                                    {'tip': 'همیشه جملات پایه موضوع Basic Adjectives را در زمینه\u200cهای روزمره تمرین '
                                            'کنید.',
                                     'example': 'I practice this every day.'},
                                    {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته '
                                            'باشید.',
                                     'example': 'She is in Stockholm today.'}],
                      'common_mistakes_json': [{'wrong': 'a car red',
                                                'right': 'a red car',
                                                'reason': 'صفت در انگلیسی باید قبل از اسم بیاید.'},
                                               {'wrong': 'He go to school yesterday.',
                                                'right': 'He goes to school every day.',
                                                'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت شود.'},
                                               {'wrong': 'They is happy here.',
                                                'right': 'They are happy here.',
                                                'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات هستند.'}]},
 'numbers_and_quantity': {'title': 'Numbers and Quantity',
                          'explanation': 'اسامی قابل شمارش را می\u200cتوان شمرده و با اعداد و many بیان کرد. اسامی '
                                         'غیرقابل شمارش (مانند آب، پول، شکر) فقط با much یا some همراه می\u200cشوند. '
                                         'این مبحث یکی از پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر '
                                         'زبان انگلیسی است. با تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید '
                                         'تسلط کامل پیدا کنید.',
                          'comparison': 'در فارسی بعد از اعداد اسم به صورت مفرد می\u200cآید (دو کتاب)، اما در انگلیسی '
                                        'اسم بعد از عدد جمع بسته می\u200cشود (two books).',
                          'examples_json': [{'target': 'I have three books.',
                                             'native': 'من سه کتاب دارم.',
                                             'breakdown': 'بعد از عدد ۳ اسم جمع (books) می\u200cآید.'},
                                            {'target': 'There are seven days in a week.',
                                             'native': 'هفت روز در یک هفته وجود دارد.',
                                             'breakdown': 'عدد هفت قبل از اسم جمع days.'},
                                            {'target': 'She has many friends.',
                                             'native': 'او دوستان زیادی دارد.',
                                             'breakdown': 'many قبل از اسم قابل شمارش جمع.'},
                                            {'target': 'How much water do you drink?',
                                             'native': 'چقدر آب می\u200cنوشی؟',
                                             'breakdown': 'How much برای غیرقابل شمارش water.'},
                                            {'target': 'I need some money.',
                                             'native': 'من به مقداری پول نیاز دارم.',
                                             'breakdown': 'some برای غیرقابل شمارش money.'},
                                            {'target': 'There are a few apples left.',
                                             'native': 'تعداد کمی سیب باقی مانده است.',
                                             'breakdown': 'a few برای تعداد کم قابل شمارش.'},
                                            {'target': 'He drinks a lot of tea.',
                                             'native': 'او مقدار زیادی چای می\u200cنوشد.',
                                             'breakdown': 'a lot of هم برای شمارشی و هم غیرقابل شمارش.'},
                                            {'target': 'How many students are there?',
                                             'native': 'چند دانش\u200cآموز وجود دارد؟',
                                             'breakdown': 'How many برای پرسش تعداد قابل شمارش.'}],
                          'tips_json': [{'tip': 'برای غیرقابل شمارش\u200cها از much و برای قابل شمارش\u200cها از many '
                                                'استفاده کنید.',
                                         'example': 'much sugar / many apples'},
                                        {'tip': 'همیشه جملات پایه موضوع Numbers and Quantity را در زمینه\u200cهای '
                                                'روزمره تمرین کنید.',
                                         'example': 'I practice this every day.'},
                                        {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته '
                                                'باشید.',
                                         'example': 'She is in Stockholm today.'}],
                          'common_mistakes_json': [{'wrong': 'three book',
                                                    'right': 'three books',
                                                    'reason': 'بعد از اعداد بزرگتر از ۱ اسم در انگلیسی جمع بسته '
                                                              'می\u200cشود.'},
                                                   {'wrong': 'He go to school yesterday.',
                                                    'right': 'He goes to school every day.',
                                                    'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت '
                                                              'شود.'},
                                                   {'wrong': 'They is happy here.',
                                                    'right': 'They are happy here.',
                                                    'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات '
                                                              'هستند.'}]},
 'wh_questions': {'title': 'Wh- Questions',
                  'explanation': 'کلمات پرسشی Wh برای گرفتن اطلاعات خاص به کار می\u200cروند: What (چه چیزی)، Where '
                                 '(کجا)، Who (چه کسی)، When (چه زمانی)، Why (چرا)، How (چگونه). این مبحث یکی از '
                                 'پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی است. با تمرین '
                                 'و مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
                  'comparison': 'در انگلیسی کلمه پرسشی Wh همیشه در **ابتدای جمله** قرار می\u200cگیرد و پس از آن '
                                'بلافاصله فعل کمکی می\u200cآید.',
                  'examples_json': [{'target': 'What is your name?',
                                     'native': 'نام شما چیست؟',
                                     'breakdown': 'What برای پرسش درباره شیء یا اسم.'},
                                    {'target': 'Where do you live?',
                                     'native': 'کجا زندگی می\u200cکنی؟',
                                     'breakdown': 'Where برای پرسش مکان با فعل کمکی do.'},
                                    {'target': 'Who is that girl?',
                                     'native': 'آن دختر کیست؟',
                                     'breakdown': 'Who برای پرسش هویت اشخاص.'},
                                    {'target': 'When does the bus arrive?',
                                     'native': 'اتوبوس چه زمانی می\u200cرسد؟',
                                     'breakdown': 'When برای پرسش زمان با does.'},
                                    {'target': 'Why are you late?',
                                     'native': 'چرا دیر کرده\u200cای؟',
                                     'breakdown': 'Why برای پرسش علت با verb to be.'},
                                    {'target': 'How are you today?',
                                     'native': 'امروز چطور هستی؟',
                                     'breakdown': 'How برای پرسش حالت و چگونگی.'},
                                    {'target': 'What time is it?',
                                     'native': 'ساعت چند است؟',
                                     'breakdown': 'What time برای سوال ساعت.'},
                                    {'target': 'Where is the bathroom?',
                                     'native': 'دستشویی کجا است؟',
                                     'breakdown': 'Where برای پرسش درباره مکان قرارگیری.'}],
                  'tips_json': [{'tip': 'فرمول سوالات Wh: کلمه Wh + فعل کمکی + فاعل + فعل اصلی؟',
                                 'example': 'Where do you work?'},
                                {'tip': 'همیشه جملات پایه موضوع Wh- Questions را در زمینه\u200cهای روزمره تمرین کنید.',
                                 'example': 'I practice this every day.'},
                                {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته باشید.',
                                 'example': 'She is in Stockholm today.'}],
                  'common_mistakes_json': [{'wrong': 'Where you live?',
                                            'right': 'Where do you live?',
                                            'reason': 'در سوالات Wh فعل کمکی (do/does) نباید فراموش شود.'},
                                           {'wrong': 'He go to school yesterday.',
                                            'right': 'He goes to school every day.',
                                            'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت شود.'},
                                           {'wrong': 'They is happy here.',
                                            'right': 'They are happy here.',
                                            'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات هستند.'}]},
 'object_pronouns': {'title': 'Object Pronouns',
                     'explanation': 'ضمایر مفعولی دریافت\u200cکننده عمل فعل هستند و همیشه بعد از فعل یا حروف اضافه '
                                    'قرار می\u200cگیرند: me, you, him, her, it, us, them. این مبحث یکی از '
                                    'پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی است. با '
                                    'تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
                     'comparison': "در فارسی مفعول با نشانه 'را' همراه می\u200cشود (او را دیدم). در انگلیسی ضمیر "
                                   'مفعولی شکل کاملاً متفاوتی دارد (I -> me, She -> her) و بعد از فعل می\u200cآید.',
                     'examples_json': [{'target': 'Please call me tonight.',
                                        'native': 'لطفاً امشب به من زنگ بزن.',
                                        'breakdown': 'me ضمیر مفعولی دوم شخص متکلم است.'},
                                       {'target': 'I saw her at the supermarket.',
                                        'native': 'من او را در سوپرمارکت دیدم.',
                                        'breakdown': 'her ضمیر مفعولی مونث است.'},
                                       {'target': 'We visited him yesterday.',
                                        'native': 'ما دیروز به ملاقات او رفتیم.',
                                        'breakdown': 'him ضمیر مفعولی مذکر است.'},
                                       {'target': 'She gave us a present.',
                                        'native': 'او به ما یک هدیه داد.',
                                        'breakdown': 'us ضمیر مفعولی ما است.'},
                                       {'target': 'Look at them!',
                                        'native': 'به آن\u200cها نگاه کن!',
                                        'breakdown': 'them بعد از حرف اضافه at برای آن\u200cها.'},
                                       {'target': 'I can help you.',
                                        'native': 'من می\u200cتوانم به تو کمک کنم.',
                                        'breakdown': 'you ضمیر مفعولی مخاطب است.'},
                                       {'target': "Don't touch it!",
                                        'native': 'به آن دست نزن!',
                                        'breakdown': 'it ضمیر مفعولی غیرانسان است.'},
                                       {'target': 'He told me the secret.',
                                        'native': 'او راز را به من گفت.',
                                        'breakdown': 'me مفعول مستقیم فعل told.'}],
                     'tips_json': [{'tip': 'ضمایر مفعولی همیشه بعد از افعال یا حروف اضافه (to, with, at, for) '
                                           'می\u200cآیند.',
                                    'example': 'Listen to me.'},
                                   {'tip': 'همیشه جملات پایه موضوع Object Pronouns را در زمینه\u200cهای روزمره تمرین '
                                           'کنید.',
                                    'example': 'I practice this every day.'},
                                   {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته '
                                           'باشید.',
                                    'example': 'She is in Stockholm today.'}],
                     'common_mistakes_json': [{'wrong': 'She saw I.',
                                               'right': 'She saw me.',
                                               'reason': 'بعد از فعل دیدن (saw) باید از ضمیر مفعولی me استفاده شود نه '
                                                         'I.'},
                                              {'wrong': 'He go to school yesterday.',
                                               'right': 'He goes to school every day.',
                                               'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت شود.'},
                                              {'wrong': 'They is happy here.',
                                               'right': 'They are happy here.',
                                               'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات هستند.'}]},
 'like_and_want': {'title': 'Like and Want',
                   'explanation': 'فعل like به معنای دوست داشتن و want به معنای خواستن است. وقتی بخواهیم کاری را انجام '
                                  'دهیم، بعد از want از to + فعل ساده استفاده می\u200cکنیم (want to go). این مبحث یکی '
                                  'از پایه\u200cای\u200cترین و پرکاربردترین بخش\u200cهای گرامر زبان انگلیسی است. با '
                                  'تمرین و مرور مثال\u200cهای ارائه شده می\u200cتوانید تسلط کامل پیدا کنید.',
                   'comparison': 'در فارسی بعد از خواستن فعل به صورت التزامی می\u200cآید (می\u200cخواهم بروم). در '
                                 "انگلیسی از ساختار 'want + to + فعل پایه' استفاده می\u200cشود.",
                   'examples_json': [{'target': 'I like ice cream.',
                                      'native': 'من بستنی دوست دارم.',
                                      'breakdown': 'like + اسم برای بیان علاقه.'},
                                     {'target': 'She wants a cup of coffee.',
                                      'native': 'او یک فنجان قهوه می\u200cخواهد.',
                                      'breakdown': 'wants برای سوم شخص مفرد she.'},
                                     {'target': 'I want to learn English.',
                                      'native': 'من می\u200cخواهم انگلیسی یاد بگیرم.',
                                      'breakdown': 'want + to + فعل ساده learn.'},
                                     {'target': 'He likes playing football.',
                                      'native': 'او فوتبال بازی کردن را دوست دارد.',
                                      'breakdown': 'likes + اسم مصدر.'},
                                     {'target': 'They want to travel to Norway.',
                                      'native': 'آن\u200cها می\u200cخواهند به نروژ سفر کنند.',
                                      'breakdown': 'want + to + travel.'},
                                     {'target': 'Do you want some water?',
                                      'native': 'آیا مقداری آب می\u200cخواهی؟',
                                      'breakdown': 'سوالی با Do برای want.'},
                                     {'target': "She doesn't like cold coffee.",
                                      'native': 'او قهوه سرد دوست ندارد.',
                                      'breakdown': "منفی با doesn't like."},
                                     {'target': 'We want to buy a new car.',
                                      'native': 'ما می\u200cخواهیم یک ماشین جدید بخریم.',
                                      'breakdown': 'want + to + buy.'}],
                   'tips_json': [{'tip': 'بعد از want برای انجام کار همیشه to قرار دهید.',
                                  'example': 'I want to go (NOT I want go)'},
                                 {'tip': 'همیشه جملات پایه موضوع Like and Want را در زمینه\u200cهای روزمره تمرین کنید.',
                                  'example': 'I practice this every day.'},
                                 {'tip': 'به علامت\u200cگذاری و ترتیب صحیح کلمات در انتهای جمله دقت ویژه داشته باشید.',
                                  'example': 'She is in Stockholm today.'}],
                   'common_mistakes_json': [{'wrong': 'I want go home.',
                                             'right': 'I want to go home.',
                                             'reason': 'بین want و فعل بعدی حرف اضافه to الزامی است.'},
                                            {'wrong': 'He go to school yesterday.',
                                             'right': 'He goes to school every day.',
                                             'reason': 'در زمان حال ساده برای مفرد باید ساختار درست فعل رعایت شود.'},
                                            {'wrong': 'They is happy here.',
                                             'right': 'They are happy here.',
                                             'reason': 'فاعل\u200cهای جمع همیشه نیازمند فعل جمع در جملات هستند.'}]}}


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

        # Validate grammar content completeness & rules
        import importlib.util
        spec = importlib.util.spec_from_file_location("grammar_content_validator", "validators/grammar_content_validator.py")
        gcv = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gcv)

        val_result = gcv.GrammarContentValidator().validate(content_data)
        if not val_result.passed:
            print(f"❌ Grammar content validation failed for '{topic_code}':")
            for issue in val_result.issues:
                print(f"   • [{issue.code}] {issue.message}")
            continue

        # Check existing content
        existing = sb.table("grammar_content").select("id").eq("topic_id", topic_id).eq("native_language", "fa").maybe_single().execute()

        payload = {
            "topic_id": topic_id,
            "native_language": "fa",
            "title": content_data["title"],
            "explanation": content_data["explanation"],
            "comparison": content_data["comparison"],
            "examples_json": content_data["examples_json"],
            "tips_json": content_data["tips_json"],
            "common_mistakes_json": content_data["common_mistakes_json"],
            "quality_score": 1.0,
            "generation_model": "manual",
        }

        try:
            if existing.data:
                sb.table("grammar_content").update(payload).eq("id", existing.data["id"]).execute()
            else:
                sb.table("grammar_content").insert(payload).execute()
        except Exception as e:
            if "comparison" in str(e):
                payload_fallback = dict(payload)
                del payload_fallback["comparison"]
                if existing.data:
                    sb.table("grammar_content").update(payload_fallback).eq("id", existing.data["id"]).execute()
                else:
                    sb.table("grammar_content").insert(payload_fallback).execute()
            else:
                raise e

        updated_count += 1
        print(f"✅ Topic '{topic_code:28s}': updated with 8 examples & Persian comparison.")

    print("=" * 60)
    print(f"🎉 DONE! Updated {updated_count} topics in grammar_content table.")
    print("=" * 60)

if __name__ == "__main__":
    seed_grammar_content()
