import telebot
import spacy

# مدل فارسی
nlp = spacy.load("fa_core_news_sm")

# توکن
bot = telebot.TeleBot("8413660896:AAHIZaCtmRZWWB_Y7B7JVsgX1izcpWmgOfk")

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "سلام! من آنلاینم و از سرور خارج کار می‌کنم")

@bot.message_handler(func=lambda m: True)
def echo(message):
    doc = nlp(message.text)
    bot.reply_to(message, f"تعداد کلمات: {len(doc)}")

print("بات در حال اجراست...")
bot.polling()
