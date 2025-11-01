import telebot
import os

# --- از متغیر محیطی استفاده کن ---
bot = telebot.TeleBot(os.getenv("BOT_TOKEN"))

# بقیه کد...
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام! من آنلاینم و از سرور خارج کار می‌کنم")

@bot.message_handler(func=lambda m: True)
def echo(message):
    doc = nlp(message.text)
    bot.reply_to(message, f"تعداد کلمات: {len(doc)}")

print("بات در حال اجراست...")
bot.polling()
