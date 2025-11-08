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

# --- سناریوها: ۱۰ سوال + ۳ گزینه واضح و واقعی ---
scenarios = {
    'مصاحبه': {
        'questions': [
            "چرا این شغل رو می‌خوای؟",
            "بزرگ‌ترین نقطه قوتت چیه؟",
            "با فشار کاری چطوری کنار میای؟",
            "یه دستاورد خفن از کار قبلیت بگو",
            "چرا باید تو رو استخدام کنیم؟",
            "۵ سال دیگه خودتو کجا می‌بینی؟",
            "اگه انتقاد کنن، چی می‌گی؟",
            "یه مثال از کار تیمی بزن",
            "چطوری کارات رو اولویت‌بندی می‌کنی؟",
            "سوالی از ما داری؟"
        ],
        'options': [
            ["علاقه دارم و مهارت دارم", "برای تجربه و یادگیری", "فقط برای پول"],
            ["حل مسئله و یادگیری سریع", "کار تیمی خوبه", "نمی‌دونم"],
            ["آروم می‌مونم و برنامه می‌ریزم", "اضافه‌کاری می‌کنم", "استرس می‌گیرم و عصبی می‌شم"],
            ["پروژه رو با موفقیت تموم کردم", "فروش رو ۲۰٪ بالا بردم", "هیچ دستاوردی نداشتم"],
            ["مهارت دارم و انگیزه‌م بالاست", "نیاز به کار دارم", "بهتر از بقیه نیستم"],
            ["مدیریت یه تیم", "کارمند ارشد", "هنوز نمی‌دونم"],
            ["ممنون، سعی می‌کنم بهتر بشم", "دفاع می‌کنم", "نادیده می‌گیرم"],
            ["با تیم یه پروژه رو تحویل دادیم", "رهبری کردم", "تنها کار کردم"],
            ["لیست می‌نویسم و اولویت می‌دم", "اولویت‌بندی می‌کنم", "همه کارا رو با هم"],
            ["درباره فرهنگ شرکت", "خیر", "حقوق چنده؟"]
        ],
        'positive': ['علاقه', 'مهارت', 'یادگیری', 'حل مسئله', 'انگیزه', 'مدیریت', 'پذیرش', 'اصلاح', 'اولویت', 'تیم', 'فرهنگ'],
        'negative': ['پول', 'استرس', 'تنها', 'دفاع', 'نادیده', 'نمی‌دونم', 'حقوق', 'عصبی']
    },
    'مذاکره': {
        'questions': [
            "حقوق بیشتر می‌خوای، چی می‌گی؟",
            "مشتری عصبانیه، چطوری آرومش می‌کنی؟",
            "توافق دوطرفه پیشنهاد بده",
            "مذاکره بن‌بست خورد، چی کار می‌کنی؟",
            "چطوری اعتماد جلب می‌کنی؟",
            "تخفیف می‌دی تو فروش؟",
            "از مدیر مرخصی می‌خوای، چی می‌گی؟",
            "اختلاف قیمت داری، چطوری حل می‌کنی؟",
            "شیفت با همکار، چطوری مذاکره می‌کنی؟",
            "آخرین حرفت تو مذاکره چیه؟"
        ],
        'options': [
            ["با توجه به مهارت‌هام، حقوق بالاتری می‌خوام", "درخواست می‌کنم", "تهدید به رفتن"],
            ["عذرخواهی + راه‌حل می‌دم", "گوش می‌دم", "نادیده می‌گیرم"],
            ["هر دو سود کنیم", "من کمی سود", "من همه سود"],
            ["سازش می‌کنم", "ادامه می‌دم", "ترک می‌کنم"],
            ["شفاف و صادقم", "قول می‌دم", "دروغ مصلحتی"],
            ["بله، با شرط خرید بیشتر", "کمی تخفیف", "نه، قیمت ثابته"],
            ["دلیل موجه دارم", "التماس می‌کنم", "تهدید می‌کنم"],
            ["قیمت منصفانه پیشنهاد می‌دم", "تخفیف می‌دم", "نه"],
            ["همکاری می‌کنیم", "من کار می‌کنم", "تو کار کن"],
            ["این بهترین پیشنهاده", "هنوز می‌تونم", "قبول کن وگرنه می‌رم"]
        ],
        'positive': ['مهارت', 'راه‌حل', 'سود', 'سازش', 'شفاف', 'دلیل', 'منصفانه', 'همکاری', 'شرط', 'بهترین'],
        'negative': ['تهدید', 'دفاع', 'ترک', 'دروغ', 'التماس', 'نه', 'من همه سود']
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
        'options': [
            ["جلسه می‌ذارم و حرف می‌زنیم", "نادیده می‌گیرم", "داد می‌زنم"],
            ["حرفه‌ای رفتار می‌کنم", "فاصله می‌گیرم", "شایعه می‌کنم"],
            ["شفاف‌سازی می‌کنم", "نادیده می‌گیرم", "پاسخ با شایعه"],
            ["محترمانه اشاره می‌کنم", "مستقیم انتقاد", "هیچی نمی‌گم"],
            ["یادآوری می‌کنم", "گزارش به مدیر", "انتقام می‌گیرم"],
            ["میانجی‌گری می‌کنم", "ترک جلسه", "داد می‌زنم"],
            ["مذاکره زمان می‌کنم", "اضافه‌کاری", "تحویل نمی‌دم"],
            ["گوش می‌دم و اصلاح می‌کنم", "دفاع می‌کنم", "حمله می‌کنم"],
            ["میانجی می‌شم", "طرفداری می‌کنم", "نادیده می‌گیرم"],
            ["گوش + راه‌حل", "دفاع", "قطع ارتباط"]
        ],
        'positive': ['جلسه', 'حرف', 'شفاف', 'محترم', 'یادآوری', 'میانجی', 'مذاکره', 'گوش', 'راه‌حل', 'حرفه‌ای'],
        'negative': ['داد', 'فاصله', 'شایعه', 'انتقام', 'ترک', 'اضافه', 'دفاع', 'حمله', 'قطع']
    }
}

user_state = {}

# --- کیبورد ---
def scenario_keyboard(options, step, total):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    for opt in options:
        markup.add(opt)
    row = []
    if step > 1:
        row.append("سوال قبلی")
    if step < total:
        row.append("سوال بعدی")
    row.append("برگشت به منو")
    markup.row(*row)
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
    bot.reply_to(msg, "*راهنما*\n\n1. دکمه بزن یا تایپ کن\n2. هر سوال ۳ گزینه واضح داره\n3. نمره هر سوال جدا\n4. سوال قبلی/بعدی بزن\n5. برگشت به منو", parse_mode='Markdown')

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
            opts = scenarios[key]['options'][0]
            bot.reply_to(msg, f"سناریو **{key}** شروع شد!\n\nسوال ۱: {q}", reply_markup=scenario_keyboard(opts, 1, st['total_questions']))
        else:
            bot.reply_to(msg, "یکی از اینا رو انتخاب کن: مصاحبه، مذاکره، تعارض")
        return

    scenario = scenarios[st['scenario']]
    total = st['total_questions']

    # --- سوال قبلی ---
    if txt == "سوال قبلی" and st['step'] > 1:
        st['step'] -= 1
        q = scenario['questions'][st['step']-1]
        opts = scenario['options'][st['step']-1]
        bot.reply_to(msg, f"سوال {st['step']}: {q}", reply_markup=scenario_keyboard(opts, st['step'], total))
        return

    # --- سوال بعدی ---
    if txt == "سوال بعدی" and st['step'] < total:
        st['step'] += 1
        q = scenario['questions'][st['step']-1]
        opts = scenario['options'][st['step']-1]
        bot.reply_to(msg, f"سوال {st['step']}: {q}", reply_markup=scenario_keyboard(opts, st['step'], total))
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
        nxt_opts = scenario['options'][st['step']-1]
        bot.reply_to(msg, f"{feedback}\n\nسوال {st['step']}: {nxt_q}", reply_markup=scenario_keyboard(nxt_opts, st['step'], total))
    else:
        report_lines = [f"سوال {i+1}: **{s}/10**" for i, s in enumerate(st['scores'])]
        total_avg = sum(st['scores']) / len(st['scores'])
        report = "سناریو تموم شد!\n\n" + "\n".join(report_lines) + f"\n\nمیانگین: **{total_avg:.1f}/10**"
        bot.reply_to(msg, f"{feedback}\n\n{report}", reply_markup=telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True).add("مصاحبه", "مذاکره", "تعارض"))
        del user_state[uid]

print("بات در حال اجراست...")
bot.polling()
