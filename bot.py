import telebot
import re
import random
import os

# --- توکن از محیط ---
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("خطا: BOT_TOKEN پیدا نشد!")
    exit()

bot = telebot.TeleBot(TOKEN)

# --- لیست فحش‌ها ---
BAD_WORDS = [
    'کص', 'کیر', 'جنده', 'مادرجنده', 'گایید', 'گاییدن', 'لاشی', 'حرومزاده',
    'گوه', 'گوز', 'سگ', 'کونی', 'مادرسگ', 'پدرسگ', 'فاحشه', 'قهوه', 'کصکش'
]

# --- سناریوها: هر دسته ۱۰ سوال + ۱۰ گزینه ---
scenarios = {
    'مصاحبه': {
        'questions': [
            "چرا این شغل رو می‌خوای؟",
            "بزرگ‌ترین نقطه قوتت چیه؟",
            "چطور با فشار کاری کنار میای؟",
            "یک دستاورد مهم در کار قبلیت چیه؟",
            "چرا باید تو رو استخدام کنیم؟",
            "در ۵ سال آینده خودت رو کجا می‌بینی؟",
            "چطور با انتقاد برخورد می‌کنی؟",
            "یک مثال از کار تیمی بزن.",
            "چطور اولویت‌بندی می‌کنی؟",
            "سوال دیگه‌ای داری از ما؟"
        ],
        'options': [
            ["علاقه و مهارت دارم", "برای پول", "به خاطر تیم"],
            ["مهارت فنی", "تجربه", "انعطاف‌پذیری"],
            ["مدیریت زمان", "استرس دارم", "اضافه‌کاری"],
            ["پروژه موفق", "افزایش فروش", "هیچ چیز خاص"],
            ["مهارت و انگیزه", "نیاز به کار", "بهتر از بقیه"],
            ["مدیریت", "کارمند ارشد", "نمی‌دونم"],
            ["پذیرش و اصلاح", "دفاع از خود", "نادیده گرفتن"],
            ["همکاری موفق", "رهبری تیم", "تنها کار کردم"],
            ["لیست وظایف", "اولویت‌بندی", "همه با هم"],
            ["بله، درباره تیم", "خیر", "حقوق چنده؟"]
        ],
        'positive': ['مهارت', 'علاقه', 'انعطاف', 'همکاری', 'اصلاح', 'مدیریت', 'پذیرش', 'اولویت', 'تیم'],
        'negative': ['پول', 'استرس', 'تنها', 'دفاع', 'نادیده', 'نمی‌دونم', 'حقوق', 'اضافه']
    },
    'مذاکره': {
        'questions': [
            "در مذاکره حقوق، چی می‌گی؟",
            "مشتری عصبانی، چطور آرومش می‌کنی؟",
            "توافق دوطرفه پیشنهاد بده.",
            "در بن‌بست مذاکره، چی کار می‌کنی؟",
            "چطور اعتماد ایجاد می‌کنی؟",
            "در مذاکره فروش، تخفیف می‌دی؟",
            "مذاکره با مدیر برای مرخصی چطوره؟",
            "در اختلاف قیمت، چی می‌گی؟",
            "مذاکره با همکار برای شیفت چطوره؟",
            "آخرین پیشنهاد تو چیه؟"
        ],
        'options': [
            ["ارزشم رو نشون می‌دم", "تهدید به رفتن", "درخواست زیاد"],
            ["عذرخواهی + راه‌حل", "دفاع", "نادیده"],
            ["هر دو سود کنیم", "من ببرم", "تو ببر"],
            ["سازش", "ترک مذاکره", "اصرار"],
            ["شفافیت", "قول", "دروغ مصلحتی"],
            ["بله، با شرط", "خیر", "زیاد"],
            ["دلیل موجه", "التماس", "تهدید"],
            ["قیمت منصفانه", "تخفیف", "نه"],
            ["همکاری", "من کار می‌کنم", "تو کار کن"],
            ["این آخریه", "هنوز می‌تونم", "قبول کن"]
        ],
        'positive': ['ارزش', 'راه‌حل', 'سود', 'سازش', 'شفافیت', 'دلیل', 'منصفانه', 'همکاری'],
        'negative': ['تهدید', 'دفاع', 'ترک', 'دروغ', 'التماس', 'تخفیف', 'نه', 'من ببرم']
    },
    'تعارض': {
        'questions': [
            "اختلاف بر سر پروژه، چی کار می‌کنی؟",
            "تعارض شخصیتی با همکار چطور؟",
            "شایعه در تیم، راهکارت چیه؟",
            "مدیر اشتباه کرد، چی می‌گی؟",
            "همکار وظایفش رو انجام نمی‌ده، چی؟",
            "در جلسه، بحث داغ شد، چی کار می‌کنی؟",
            "تعارض بر سر زمان تحویل چطور؟",
            "همکار انتقاد تند کرد، چی می‌گی؟",
            "در تیم، دو نفر دعوا کردن، چی؟",
            "تعارض با مشتری، چطور حل می‌کنی؟"
        ],
        'options': [
            ["جلسه می‌ذارم", "نادیده", "داد می‌زنم"],
            ["حرف می‌زنم", "فاصله", "شایعه"],
            ["شفاف‌سازی", "نادیده", "پاسخ با شایعه"],
            ["محترمانه اشاره", "مستقیم انتقاد", "هیچی"],
            ["یادآوری", "انتقام", "گزارش به مدیر"],
            ["میانجی‌گری", "ترک جلسه", "داد زدن"],
            ["مذاکره زمان", "اضافه‌کاری", "تحویل ندادن"],
            ["گوش دادن", "دفاع", "حمله"],
            ["میانجی", "طرفداری", "نادیده"],
            ["گوش + راه‌حل", "دفاع", "قطع ارتباط"]
        ],
        'positive': ['جلسه', 'حرف', 'شفاف', 'محترمانه', 'یادآوری', 'میانجی', 'مذاکره', 'گوش', 'راه‌حل'],
        'negative': ['داد', 'فاصله', 'شایعه', 'انتقام', 'ترک', 'اضافه', 'دفاع', 'حمله', 'قطع']
    }
}

user_state = {}

# --- کیبوردها ---
def main_menu_keyboard():
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add("مصاحبه", "مذاکره", "تعارض")
    return markup

def scenario_keyboard(options):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for opt in options:
        markup.add(opt)
    markup.add("سوال بعدی", "برگشت به منو")
    return markup

# --- تشخیص فحش ---
def has_bad_word(text):
    txt = text.lower()
    return any(bad in txt for bad in BAD_WORDS)

# --- واکنش‌ها ---
POSITIVE_REACTIONS = ["عالی بود!", "آفرین!", "دمت گرم!", "حرفه‌ای!", "اینو بلدی!"]
NEGATIVE_REACTIONS = ["وای نه!", "اینو دیگه نگو!", "بیا دوباره امتحان کنیم", "نه بابا!"]

# --- دستورات ---
@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.chat.id
    user_state[uid] = {'scenario': None, 'step': 0, 'score': 0}
    welcome = (
        "*مهارت‌یار* | آموزش مهارت‌های نرم\n\n"
        "یکی از سناریوها رو انتخاب کن:\n\n"
        "دکمه بزن یا تایپ کن"
    )
    bot.send_message(uid, welcome, parse_mode='Markdown', reply_markup=main_menu_keyboard())

@bot.message_handler(commands=['help'])
def help_cmd(msg):
    help_text = (
        "*راهنمای مهارت‌یار*\n\n"
        "1. `/start` → شروع\n"
        "2. دکمه یا تایپ → جواب\n"
        "3. امتیاز + فیدبک\n"
        "4. ۱۰ سوال در هر سناریو\n"
        "5. دکمه برگشت همیشه فعاله"
    )
    bot.reply_to(msg, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['about'])
def about_cmd(msg):
    about_text = (
        "*درباره ما*\n\n"
        "ساخته شده توسط:\n"
        "• *ارشیا*\n"
        "• *محمدرضا*\n\n"
        "پروژه دانشگاهی | ۱۴۰۴\n"
        "هدف: تقویت مهارت‌های نرم"
    )
    bot.reply_to(msg, about_text, parse_mode='Markdown')

@bot.message_handler(func=lambda m: True)
def handle(msg):
    uid = msg.chat.id
    txt = msg.text.strip()

    if uid not in user_state:
        start(msg)
        return

    st = user_state[uid]

    # --- برگشت به منو ---
    if txt == "برگشت به منو":
        bot.reply_to(msg, "برگشتیم به منوی اصلی!", reply_markup=main_menu_keyboard())
        user_state[uid] = {'scenario': None, 'step': 0, 'score': 0}
        return

    # --- فحش ---
    if has_bad_word(txt):
        bot.reply_to(msg, "این حرفا تو محیط کار نمی‌زنن!\nبیا دوباره، با ادب", 
                     reply_markup=telebot.types.ReplyKeyboardRemove())
        return

    # --- انتخاب سناریو ---
    if st['scenario'] is None:
        key = txt.lower()
        if key in scenarios:
            st['scenario'] = key
            st['step'] = 1
            q = scenarios[key]['questions'][0]
            opts = scenarios[key]['options'][0]
            bot.reply_to(msg, f"سناریو **{key}** شروع شد!\nسوال ۱: {q}", 
                         reply_markup=scenario_keyboard(opts))
        else:
            bot.reply_to(msg, "لطفاً یکی از سناریوها رو انتخاب کن: مصاحبه، مذاکره، تعارض")
        return

    scenario = scenarios[st['scenario']]

    # --- سوال بعدی ---
    if txt == "سوال بعدی":
        st['step'] += 1
        if st['step'] <= len(scenario['questions']):
            q = scenario['questions'][st['step']-1]
            opts = scenario['options'][st['step']-1]
            bot.reply_to(msg, f"سوال {st['step']}: {q}", reply_markup=scenario_keyboard(opts))
        return

    # --- تحلیل پاسخ ---
    words = [w.lower() for w in re.findall(r'\b\w+\b', txt) if len(w) > 2]
    pos_cnt = sum(1 for w in words if any(p in w for p in scenario['positive']))
    neg_cnt = sum(1 for w in words if any(n in w for n in scenario['negative']))

    score = max(0, min(10, 5 + pos_cnt - neg_cnt))
    st['score'] += score

    reaction = random.choice(POSITIVE_REACTIONS) if score >= 6 else random.choice(NEGATIVE_REACTIONS)
    tip = random.choice(scenario['positive'])
    feedback = f"{reaction}\nامتیاز: **{score}/10**\nپیشنهاد: روی **{tip}** تمرکز کن"

    # --- سوال بعدی ---
    st['step'] += 1
    if st['step'] <= len(scenario['questions']):
        nxt_q = scenario['questions'][st['step']-1]
        nxt_opts = scenario['options'][st['step']-1]
        bot.reply_to(msg, f"{feedback}\n\nسوال {st['step']}: {nxt_q}", 
                     reply_markup=scenario_keyboard(nxt_opts))
    else:
        total = st['score'] / len(scenario['questions'])
        report = f"سناریو تموم شد!\nامتیاز نهایی: **{total:.1f}/10**"
        bot.reply_to(msg, f"{feedback}\n\n{report}", reply_markup=main_menu_keyboard())
        user_state[uid] = {'scenario': None, 'step': 0, 'score': 0}

print("بات در حال اجراست...")
bot.polling()
