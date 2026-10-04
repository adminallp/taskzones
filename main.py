import telebot
import requests
import json

# আপনার Task Zone টেলিগ্রাম বোটের টোকেন
TOKEN = '8681169433:AAFtdmBgqZmnZjFFfzj5eioAy-OzeGhZSwQ'
bot = telebot.TeleBot(TOKEN)

# আপনার ফায়ারবেস রিয়েলটাইম ডাটাবেজ URL
FIREBASE_URL = "https://taskzone365-default-rtdb.firebaseio.com/"

# স্টার্ট কমান্ড হ্যান্ডলার (ইউজার রেজিস্ট্রেশন)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    username = message.from_user.username or "No Username"
    first_name = message.from_user.first_name
    
    # ফায়ারবেসে ইউজারের ডাটা চেক করা
    user_url = f"{FIREBASE_URL}/users/{user_id}.json"
    response = requests.get(user_url)
    user_data = response.json()
    
    # যদি ইউজার ডাটাবেজে না থাকে, তবে নতুন ইউজার হিসেবে সেভ করা
    if not user_data:
        new_user = {
            'username': username,
            'first_name': first_name,
            'balance': 0,
            'strike': 0
        }
        requests.put(user_url, json=json.dumps(new_user))
        print(f"New user added to Firebase: {user_id}")
    
    welcome_text = (
        f"স্বাগতম, {first_name}!\n\n"
        "Task Zone-এ আপনাকে স্বাগতম। এখানে আপনি ভয়েস ওভার বা বিভিন্ন টাস্ক সাবমিট করতে পারবেন।\n"
        "আপনার কাজ জমা দিতে নিচের নিয়মে ভয়েস, অডিও বা স্ক্রিনশট পাঠান।"
    )
    bot.reply_to(message, welcome_text)

# মিডিয়া ফাইল হ্যান্ডলার (ভয়েস, ছবি বা অডিও টেলিগ্রাম ক্লাউডে রেখে শুধু file_id ডাটাবেজে রাখা)
@bot.message_handler(content_types=['photo', 'voice', 'audio', 'document'])
def handle_media(message):
    file_id = None
    file_type = ""
    
    if message.photo:
        file_id = message.photo[-1].file_id
        file_type = "photo"
    elif message.voice:
        file_id = message.voice.file_id
        file_type = "voice"
    elif message.audio:
        file_id = message.audio.file_id
        file_type = "audio"
    elif message.document:
        file_id = message.document.file_id
        file_type = "document"
        
    user_id = message.from_user.id
    
    # ফায়ারবেসে ইউজারের সাবমিশন বা ফাইল আইডি লগ সেভ করা
    submissions_url = f"{FIREBASE_URL}/submissions/{user_id}.json"
    submission_data = {
        'file_id': file_id,
        'file_type': file_type,
        'status': 'pending'
    }
    requests.post(submissions_url, json=json.dumps(submission_data))
    
    bot.reply_to(message, f"আপনার {file_type} সফলভাবে জমা হয়েছে এবং সিস্টেমে রেকর্ড করা হয়েছে!")
    print(f"Saved {file_type} from User {user_id}, File ID: {file_id}")

# বোট রান করার জন্য
if __name__ == '__main__':
    print("Task Zone Bot is running successfully...")
    bot.infinity_polling()
