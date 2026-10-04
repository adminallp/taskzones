import os
import telebot
from flask import Flask
from threading import Thread

# আপনার তৈরি করা আলাদা handlers.py ফাইল থেকে ফাংশনটি ইম্পোর্ট করা হলো
from handlers import register_handlers

# আপনার Task Zone টেলিগ্রাম বোটের টোকেন
TOKEN = '8681169433:AAFtdmBgqZmnZjFFfzj5eioAy-OzeGhZSwQ'
bot = telebot.TeleBot(TOKEN)

# আপনার ফায়ারবেস রিয়েলটাইম ডাটাবেজ URL
FIREBASE_URL = "https://taskzone365-default-rtdb.firebaseio.com/"

# handlers.py এর সমস্ত কমান্ড এবং মেসেজ হ্যান্ডলার এখানে রেজিস্টার করা হলো
register_handlers(bot, FIREBASE_URL)

# রেন্ডার পোর্টের প্রয়োজনীয়তা পূরণের জন্য ফ্লাস্ক সার্ভার
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

# বোট রান করার জন্য
if __name__ == '__main__':
    # ফ্লাস্ক সার্ভার ব্যাকগ্রাউন্ডে চালু করা যাতে রেন্ডার পোর্ট ওপেন পায়
    keep_alive()
    print("Task Zone Bot is running successfully with modular structure...")
    bot.infinity_polling()
