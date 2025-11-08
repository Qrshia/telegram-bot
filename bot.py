import telebot
import re
import random
import os

# --- توکن از محیط (در Render اضافه می‌کنیم) ---
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("خطا: BOT_TOKEN پیدا نشد!")
    exit()

bot = telebot.TeleBot(TOKEN)

# سناریوها + کلمات کلیدی
scenarios = {
    'مصاحبه': {
        'questions': [
            "چرا این شغل رو می‌خوای؟",
            "چطور با تعارض در تیم برخورد می‌کنی؟",
            "یک مثال از حل مسئله بزن."
        ],
        'positive': ['همدلی', 'همکاری', 'خلاقیت', 'گوش', 'ارتباط'],
        'negative': ['عصبانی', 'اجتناب', 'تقصیر', 'نادیده']
    },
    'مذاکره': {
        'questions': [
            "در مذاکره برای حقوق بیشتر، چی می‌گی؟",
            "چطور با مشتری عصبانی مذاکره می‌کنی؟",
            "یک توافق دوطرفه پیشنهاد بده."
        ],
        'positive': ['توافق', 'انعطاف', 'تحلیل', 'اعتماد', 'حل'],
        'negative': ['اصرار', 'فشار', 'دروغ', 'رد']
    },
    'تعارض': {
        'questions': [
            "در اختلاف بر سر پروژه، چی کار می‌کنی؟",
            "چطور تعارض شخصیتی رو مدیریت می‌کنی؟",
            "راهکار برای شایعه در تیم چیه؟"
        ],
        'positive': ['میانجی', 'گوش', 'سازش', 'مثبت', 'آموزش'],
        'negative': ['جنگ', 'نادیده', 'سرزنش', 'فرار']
    }
}

user_state = {}

@bot.message_handler(commands=['start'])
def start(msg):
    uid = msg.chat.id
    user_state[uid] = {'scenario': None, 'step': 0, 'score': 0}
    bot.reply_to(msg, "سلام! من بات آموزش مهارت‌های نرم هستم.\nسناریو انتخاب کن: **مصاحبه** | **مذاکره** | **تعارض**")

@bot.message_handler(func=lambda m: True)
def handle(msg):
    uid = msg.chat.id
    txt = msg.text.strip()

    if uid not in user_state:
        start(msg)
        return

    st = user_state[uid]

    if st['scenario'] is None:
        scenario_key = txt.lower()
        if scenario_key in scenarios:
            st['scenario'] = scenario_key
            st['step'] = 1
            q = scenarios[scenario_key]['questions'][0]
            bot.reply_to(msg, f"سناریو **{scenario_key}** شروع شد.\nسوال ۱: {q}")
        else:
            bot.reply_to(msg, "سناریو معتبر انتخاب کن: مصاحبه، مذاکره یا تعارض")
        return

    # تحلیل پاسخ
    words = [w.lower() for w in re.findall(r'\b\w+\b', txt) if len(w) > 2]
    pos_cnt = sum(1 for w in words if any(p in w for p in scenarios[st['scenario']]['positive']))
    neg_cnt = sum(1 for w in words if any(n in w for n in scenarios[st['scenario']]['negative']))

    score = max(0, min(10, 5 + pos_cnt - neg_cnt))
    st['score'] += score

    tip = random.choice(scenarios[st['scenario']]['positive'])
    feedback = f"امتیاز این پاسخ: **{score}/10**\nپیشنهاد: روی **{tip}** بیشتر تمرکز کن."

    st['step'] += 1
    if st['step'] <= len(scenarios[st['scenario']]['questions']):
        nxt = scenarios[st['scenario']]['questions'][st['step']-1]
        bot.reply_to(msg, f"{feedback}\n\nسوال {st['step']}: {nxt}")
    else:
        total = st['score'] / len(scenarios[st['scenario']]['questions'])
        report = f"سناریو تمام شد!\nامتیاز کلی: **{total:.1f}/10**"
        bot.reply_to(msg, f"{feedback}\n\n{report}")
        del user_state[uid]

print("بات در حال اجراست...")
bot.polling()
