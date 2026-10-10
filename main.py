import os
import telebot
from flask import Flask
from threading import Thread
from handlers import register_handlers
from dummy_poster import start_dummy_poster  # ডামি পোস্টার ইমপোর্ট করা হলো

# আপনার বোট টোকেন ও ফায়ারবেস URL
TOKEN = '8681169433:AAFtdmBgqZmnZjFFfzj5eioAy-OzeGhZSwQ'
bot = telebot.TeleBot(TOKEN)
FIREBASE_URL = "https://taskzone365-default-rtdb.firebaseio.com/"

# পূর্বের ওয়েবহুক থাকলে তা রিমোভ বা ডিলিট করে দেওয়া (কনফ্লিক্ট দূর করার জন্য)
try:
    bot.remove_webhook()
except Exception as e:
    print(f"Webhook remove error: {e}")

# হ্যান্ডলার রেজিস্টার করা
register_handlers(bot, FIREBASE_URL)

# ডামি ইউজারের অটোমেটিক পোস্টার থ্রেড চালু করা
start_dummy_poster(bot)

# রেন্ডার পোর্টের ফ্লাস্ক সার্ভার (24/7 সচল রাখার জন্য)
app = Flask('')

@app.route('/')
def home():
    return "Task Zone Bot is running live!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.start()

if __name__ == '__main__':
    keep_alive()
    print("Task Zone Bot is running successfully with complete integration...")
    bot.infinity_polling()
