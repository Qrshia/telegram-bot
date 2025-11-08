import telebot
import re
import random
import os

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("خطا: BOT_TOKEN پیدا نشد!")
    exit()

bot = telebot.TeleBot(TOKEN)

# --- فحش‌ها ---
BAD_WORDS = ['کص', 'کیر', 'جنده', 'گایید', 'لاشی', 'حرومزاده', 'گوه', 'سگ', 'کونی', 'مادرجنده']

# --- سناریوها (۱۰ سوال خودمونی) ---
scenarios = {
    'مصاحبه': {
        'questions': [
            "چرا این کار رو می‌خوای؟",
            "نقطه قوتت چیه؟",
            "با فشار کاری چطوری کنار میای؟",
            "یه دستاورد خفن از کار قبلیت بگو.",
            "چرا باید تو رو استخدام کنیم؟",
            "۵ سال دیگه خودتو کجا می‌بینی؟",
            "اگه انتقاد کنن، چی می‌گی؟",
            "یه مثال از کار تیمی بزن.",
            "چطوری کارات رو اولویت‌بندی می‌کنی؟",
            "سوالی از ما داری؟"
        ],
        'positive': ['علاقه', 'مهارت', 'انعطاف', 'همکاری', 'اصلاح', 'مدیریت', 'پذیرش', 'اولویت', 'تیم', 'خفن', 'بهتر'],
        'negative': ['پول', 'استرس', 'تنها', 'دفاع', 'نادیده', 'نمی‌دونم', 'حقوق', 'اضافه']
    },
    'مذاکره': {
        'questions': [
            "حقوق بیشتر می‌خوای، چی می‌گی؟",
            "مشتری عصبانیه، چطوری آرومش می‌کنی؟",
            "یه توافق دوطرفه پیشنهاد بده.",
            "مذاکره به بن‌بست خورد، چی کار می‌کنی؟",
            "چطوری اعتماد جلب می‌کنی؟",
            "تخفیف می‌دی تو فروش؟",
            "از مدیر مرخصی می‌خوای، چی می‌گی؟",
            "اختلاف قیمت داری، چطوری حل می‌کنی؟",
            "شیفت با همکار، چطوری مذاکره می‌کنی؟",
            "آخرین حرفت تو مذاکره چیه؟"
        ],
        'positive': ['ارزش', 'راه‌حل', 'سود', 'سازش', 'شفاف', 'دلیل', 'منصفانه', 'همکاری', 'آروم', 'اعتماد'],
        'negative': ['تهدید', 'دفاع', 'ترک', 'دروغ', 'التماس', 'زیاد', 'نه', 'من ببرم']
    },
    'تعارض': {
        'questions': [
            "تو پروژه با همکار اختلاف داری، چی کار می‌کنی؟",
            "با همکارت شخصیتاً جور نیستی، چی؟",
            "شایعه تو تیم پیچیده، راهکارت چیه؟",
            "مدیر اشتباه کرده، بهش چی می‌گی؟",
            "همکار وظایفش رو انجام نمی‌ده، چی؟",
            "تو جلسه بحث داغ شد، چی کار می‌کنی؟",
            "زمان تحویل مشکل داره، چطوری حل می‌کنی؟",
            "همکار انتقاد تند کرد، چی جواب می‌دی؟",
            "دو نفر تو تیم دعوا کردن، چی؟",
            "با مشتری اختلاف داری، چطوری حل می‌کنی؟"
        ],
        'positive': ['جلسه', 'حرف', 'شفاف', 'محترم', 'یادآوری', 'میانجی', 'مذاکره', 'گوش', 'راه‌حل', 'آروم'],
        'negative': ['داد', 'فاصله', 'شایعه', 'انتقام', 'ترک', 'اضافه', 'دفاع', 'حمله', 'قطع']
    }
}

user_state = {}

# --- کیبورد ---
def navigation_keyboard(step, total):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    if step > 1:
        markup.add("سوال قبلی")
    if step < total:
        markup.add("سوال بعدی")
    markup.add("برگشت به منو")
    return markup

# --- تشخیص فحش ---
def has_bad_word(text):
    return any(bad in text.lower() for bad in BAD_WORDS)

# --- واکنش‌ها ---
POSITIVE_REACTIONS = ["عالیه!", "آفرین!", "دمت گرم!", "حرفه‌ای!", "اینو بلدی!"]
NEGATIVE_REACTIONS = ["اوف!", "اینو دیگه نگو!", "بیا دوباره امتحان کنیم", "نه بابا!"]

# --- دستورات ---
@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.chat.id
    user_state[uid] = {'scenario': None, 'step': 0, 'scores': [], 'total_questions': 0}
    welcome = (
        "*مهارت‌یار* | آموزش مهارت‌های نرم\n\n"
        "یکی رو انتخاب کن:\n\n"
        "مصاحبه | مذاکره | تعارض"
    )
    bot.send_message(uid, welcome, parse_mode='Markdown', reply_markup=telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add("مصاحبه", "مذاکره", "تعارض"))

@bot.message_handler(commands=['help'])
def help_cmd(msg):
    bot.reply_to(msg, "*راهنما*\n\n1. `/start` شروع کن\n2. جواب بده (تایپ کن)\n3. هر سوال نمره جدا داره\n4. سوال قبلی/بعدی بزن\n5. هر وقت خواستی برگرد منو", parse_mode='Markdown')

@bot.message_handler(commands=['about'])
def about_cmd(msg):
    bot.reply_to(msg, "*درباره ما*\n\nساخته شده توسط:\n• *ارشیا*\n• *محمدرضا*\n\nپروژه دانشگاهی | ۱۴۰۴", parse_mode='Markdown')

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
        bot.reply_to(msg, "برگشتیم! دوباره انتخاب کن:", reply_markup=telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add("مصاحبه", "مذاکره", "تعارض"))
        user_state[uid] = {'scenario': None, 'step': 0, 'scores': [], 'total_questions': 0}
        return

    # --- فحش ---
    if has_bad_word(txt):
        bot.reply_to(msg, "این حرفا تو محیط کار نمی‌زنن!\nبیا دوباره، با ادب", reply_markup=telebot.types.ReplyKeyboardRemove())
        return

    # --- انتخاب سناریو ---
    if st['scenario'] is None:
        key = txt.lower()
        if key in scenarios:
            st['scenario'] = key
            st['step'] = 1
            st['total_questions'] = len(scenarios[key]['questions'])
            st['scores'] = []
            q = scenarios[key]['questions'][0]
            bot.reply_to(msg, f"سناریو **{key}** شروع شد!\n\nسوال ۱: {q}", reply_markup=navigation_keyboard(1, st['total_questions']))
        else:
            bot.reply_to(msg, "یکی از اینا رو انتخاب کن: مصاحبه، مذاکره، تعارض")
        return

    scenario = scenarios[st['scenario']]
    total = st['total_questions']

    # --- سوال قبلی ---
    if txt == "سوال قبلی" and st['step'] > stakes:
        st['step'] -= 1
        q = scenario['questions'][st['step']-1]
        bot.reply_to(msg, f"سوال {st['step']}: {q}", reply_markup=navigation_keyboard(st['step'], total))
        return

    # --- سوال بعدی ---
    if txt == "سوال بعدی" and st['step'] < total:
        st['step'] += 1
        q = scenario['questions'][st['step']-1]
        bot.reply_to(msg, f"سوال {st['step']}: {q}", reply_markup=navigation_keyboard(st['step'], total))
        return

    # --- تحلیل پاسخ ---
    words = [w.lower() for w in re.findall(r'\b\w+\b', txt) if len(w) > 2]
    pos_cnt = sum(1 for w in words if any(p in w for p in scenario['positive']))
    neg_cnt = sum(1 for w in words if any(n in w for n in scenario['negative']))

    score = max(0, min(10, 5 + pos_cnt - neg_cnt))
    st['scores'].append(score)

    reaction = random.choice(POSITIVE_REACTIONS) if score >= 6 else random.choice(NEGATIVE_REACTIONS)
    tip = random.choice(scenario['positive'])
    feedback = f"{reaction}\nامتیاز این سوال: **{score}/10**\nپیشنهاد: روی **{tip}** کار کن"

    # --- سوال بعدی ---
    st['step'] += 1
    if st['step'] <= total:
        nxt_q = scenario['questions'][st['step']-1]
        bot.reply_to(msg, f"{feedback}\n\nسوال {st['step']}: {nxt_q}", reply_markup=navigation_keyboard(st['step'], total))
    else:
        # --- گزارش نهایی با نمره هر سوال ---
        report_lines = [f"سوال {i+1}: **{score}/10**" for i, score in enumerate(st['scores'])]
        total_avg = sum(st['scores']) / len(st['scores'])
        report = "سناریو تموم شد!\n\n" + "\n".join(report_lines) + f"\n\nمیانگین: **{total_avg:.1f}/10**"
        bot.reply_to(msg, f"{feedback}\n\n{report}", reply_markup=telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add("مصاحبه", "مذاکره", "تعارض"))
        del user_state[uid]

print("بات در حال اجراست...")
bot.polling()
