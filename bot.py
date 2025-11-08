import telebot
import re
import random
import os

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("خطا: BOT_TOKEN پیدا نشد!")
    exit()

bot = telebot.TeleBot(TOKEN)

# --- لیست فحش‌ها (می‌تونی بیشتر کنی) ---
BAD_WORDS = [
    'کص', 'کیر', 'جنده', 'مادرجنده', 'گایید', 'گاییدن', 'لاشی', 'حرومزاده',
    'گوه', 'گوز', 'سگ', 'کونی', 'مادرسگ', 'پدرسگ', 'فاحشه', 'قهوه', 'کصکش'
]

# --- سناریوها + جواب‌های آماده ---
scenarios = {
    'مصاحبه': {
        'questions': [
            "چرا این شغل رو می‌خوای؟",
            "چطور با تعارض در تیم برخورد می‌کنی؟",
            "یک مثال از حل مسئله بزن."
        ],
        'options': [
            ["علاقه‌مندم و مهارت دارم", "برای پول و تجربه", "به خاطر تیم قوی"],
            ["آروم صحبت می‌کنم", "میانجی می‌شم", "نادیده می‌گیرم"],
            ["یک باگ رو رفع کردم", "تیم رو متحد کردم", "ساعت‌ها کار کردم"]
        ],
        'positive': ['همدلی', 'همکاری', 'خلاقیت', 'گوش', 'ارتباط', 'علاقه', 'متحد', 'رفع'],
        'negative': ['عصبانی', 'اجتناب', 'تقصیر', 'نادیده', 'تنها']
    },
    'مذاکره': {
        'questions': [
            "در مذاکره برای حقوق بیشتر، چی می‌گی؟",
            "چطور با مشتری عصبانی مذاکره می‌کنی؟",
            "یک توافق دوطرفه پیشنهاد بده."
        ],
        'options': [
            ["ارزشم رو نشون می‌دم", "تهدید به رفتن", "درخواست معقول"],
            ["عذرخواهی + راه‌حل", "دفاع از خودم", "نادیده گرفتن"],
            ["هر دو سود کنیم", "من ببرم", "تو ببر"]
        ],
        'positive': ['توافق', 'انعطاف', 'تحلیل', 'اعتماد', 'حل', 'ارزش', 'راه‌حل'],
        'negative': ['اصرار', 'فشار', 'دروغ', 'رد', 'تهدید']
    },
    'تعارض': {
        'questions': [
            "در اختلاف بر سر پروژه، چی کار می‌کنی؟",
            "چطور تعارض شخصیتی رو مدیریت می‌کنی؟",
            "راهکار برای شایعه در تیم چیه؟"
        ],
        'options': [
            ["جلسه می‌ذارم", "نادیده می‌گیرم", "داد می‌زنم"],
            ["حرف می‌زنم", "فاصله می‌گیرم", "شایعه می‌کنم"],
            ["شفاف‌سازی", "نادیده گرفتن", "پاسخ با شایعه"]
        ],
        'positive': ['میانجی', 'گوش', 'سازش', 'مثبت', 'آموزش', 'جلسه', 'شفاف'],
        'negative': ['جنگ', 'نادیده', 'سرزنش', 'فرار', 'شایعه', 'داد']
    }
}

user_state = {}

# --- تابع ساخت کیبورد ---
def make_keyboard(options):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for opt in options:
        markup.add(opt)
    markup.add("سوال بعدی")  # همیشه باشه
    return markup

# --- تشخیص فحش ---
def has_bad_word(text):
    txt = text.lower()
    return any(bad in txt for bad in BAD_WORDS)

# --- واکنش‌های بامزه ---
POSITIVE_REACTIONS = ["عالی بود!", "آفرین!", "دمت گرم!", "حرفه‌ای!", "اینو بلدی!"]
NEGATIVE_REACTIONS = ["وای نه!", "اینو دیگه نگو!", "بیا دوباره امتحان کنیم", "نه بابا!"]

@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.chat.id
    user_state[uid] = {'scenario': None, 'step': 0, 'score': 0}
    bot.reply_to(msg, "سلام! من بات آموزش مهارت‌های نرم هستم\nسناریو انتخاب کن:", 
                 reply_markup=telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add("مصاحبه", "مذاکره", "تعارض"))

@bot.message_handler(func=lambda m: True)
def handle(msg):
    uid = msg.chat.id
    txt = msg.text.strip()

    if uid not in user_state:
        start(msg)
        return

    st = user_state[uid]

    # --- تشخیص فحش ---
    if has_bad_word(txt):
        bot.reply_to(msg, "ای وای! این حرفا تو محیط کار نمی‌زنن\nبیا دوباره امتحان کن، با ادب", 
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
                         reply_markup=make_keyboard(opts))
        else:
            bot.reply_to(msg, "لطفاً یکی از سناریوها رو انتخاب کن: مصاحبه، مذاکره، تعارض")
        return

    scenario = scenarios[st['scenario']]

    # --- اگر دکمه "سوال بعدی" ---
    if txt == "سوال بعدی":
        st['step'] += 1
        if st['step'] <= len(scenario['questions']):
            q = scenario['questions'][st['step']-1]
            opts = scenario['options'][st['step']-1]
            bot.reply_to(msg, f"سوال {st['step']}: {q}", reply_markup=make_keyboard(opts))
        return

    # --- تحلیل پاسخ ---
    words = [w.lower() for w in re.findall(r'\b\w+\b', txt) if len(w) > 2]
    pos_cnt = sum(1 for w in words if any(p in w for p in scenario['positive']))
    neg_cnt = sum(1 for w in words if any(n in w for n in scenario['negative']))

    score = max(0, min(10, 5 + pos_cnt - neg_cnt))
    st['score'] += score

    # --- واکنش بامزه ---
    reaction = random.choice(POSITIVE_REACTIONS) if score >= 6 else random.choice(NEGATIVE_REACTIONS)
    tip = random.choice(scenario['positive'])
    feedback = f"{reaction}\nامتیاز: **{score}/10**\nپیشنهاد: روی **{tip}** تمرکز کن"

    # --- سوال بعدی ---
    st['step'] += 1
    if st['step'] <= len(scenario['questions']):
        nxt_q = scenario['questions'][st['step']-1]
        nxt_opts = scenario['options'][st['step']-1]
        bot.reply_to(msg, f"{feedback}\n\nسوال {st['step']}: {nxt_q}", 
                     reply_markup=make_keyboard(nxt_opts))
    else:
        total = st['score'] / len(scenario['questions'])
        report = f"سناریو تموم شد!\nامتیاز نهایی: **{total:.1f}/10**"
        bot.reply_to(msg, f"{feedback}\n\n{report}", 
                     reply_markup=telebot.types.ReplyKeyboardRemove())
        del user_state[uid]

print("بات در حال اجراست...")
bot.polling()
