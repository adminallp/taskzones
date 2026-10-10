import telebot
import random
import time
from threading import Thread

ADMIN_CHAT_ID = "@taskzones"

# টেলিগ্রামের রিয়েল আইডির আদলে ১০ ডিজিটের ডামি ইউজার লিস্ট
dummy_users_list = [
    {"id": 6124589021, "name": "Rakibul Islam"},
    {"id": 6189234510, "name": "Tanvir Ahmed"},
    {"id": 6234901827, "name": "Nazmul Hossain"},
    {"id": 6345129834, "name": "Sumaiya Akter"},
    {"id": 6412893456, "name": "Mehedi Hasan"},
    {"id": 6523901482, "name": "Farhana Yeasmin"},
    {"id": 6678129345, "name": "Imran Khan"},
    {"id": 6789012345, "name": "Sharmin Sultana"},
    {"id": 6890123456, "name": "Al-Amin Hossain"},
    {"id": 6901234567, "name": "Nusrat Jahan"}
]

dummy_categories = [
    ("🎥 ভিডিও এডিটিং", 40.0),
    ("📸 ছবি এডিটিং", 20.0),
    ("🎙️ ভয়েস ওভার", 15.0),
    ("🔗 শেয়ারিং প্রুফ", 10.0)
]

# কাজের প্রুফ হিসেবে দেখানোর জন্য কিছু স্যাম্পল বা ডেমো ইমেজ লিংক
sample_proof_images = [
    "https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=500",
    "https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=500",
    "https://images.unsplash.com/photo-1542744094-3a31246264d0?w=500",
    "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=500"
]

def background_dummy_poster(bot):
    time.sleep(15)  # বট স্টার্ট হওয়ার ১৫ সেকেন্ড পর প্রথম রান করবে
    while True:
        try:
            # প্রতিদিন রেন্ডম ৪ থেকে ৮ জন ডামি ইউজার কাজ জমা দেবে
            active_count = random.randint(4, 8)
            selected_dummies = random.sample(dummy_users_list, active_count)
            
            for dummy in selected_dummies:
                cat_name, reward = random.choice(dummy_categories)
                photo_url = random.choice(sample_proof_images)
                
                markup = telebot.types.InlineKeyboardMarkup(row_width=1)
                markup.add(
                    telebot.types.InlineKeyboardButton("⭐ ১ স্টার", callback_data="rate_1"),
                    telebot.types.InlineKeyboardButton("⭐⭐ ২ স্টার", callback_data="rate_2"),
                    telebot.types.InlineKeyboardButton("⭐⭐⭐ ৩ স্টার", callback_data="rate_3")
                )
                
                caption = (
                    f"📥 **নতুন টাস্ক সাবমিশন (পাবলিক ফিড):**\n\n"
                    f"👤 নাম: {dummy['name']}\n"
                    f"🆔 আইডি: `{dummy['id']}`\n"
                    f"📂 ক্যাটাগরি: {cat_name}\n"
                    f"💵 প্রদানকৃত পেমেন্ট: ৳{reward}\n"
                    f"📁 ফাইলের ধরন: photo"
                )
                
                # টেক্সটের পরিবর্তে সরাসরি ছবি সহ পোস্ট পাঠানো
                bot.send_photo(ADMIN_CHAT_ID, photo_url, caption=caption, parse_mode="Markdown", reply_markup=markup)
                
                # প্রতিটি ডামি পোস্টের মাঝে ৩ থেকে ৮ মিনিটের রেন্ডম বিরতি
                time.sleep(random.randint(180, 480))
                
        except Exception as e:
            print(f"Dummy poster background error: {e}")
            time.sleep(300)

def start_dummy_poster(bot):
    bg_thread = Thread(target=background_dummy_poster, args=(bot,), daemon=True)
    bg_thread.start()
