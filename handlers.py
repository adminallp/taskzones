import requests
import json
import telebot

def register_handlers(bot, FIREBASE_URL):

    # ১. স্টার্ট কমান্ড ও বাধ্যতামূলক রেফারেল চেক
    @bot.message_handler(commands=['start'])
    def send_welcome(message):
        user_id = message.from_user.id
        first_name = message.from_user.first_name
        username = message.from_user.username or "No Username"
        
        args = message.text.split()
        referred_by = args[1] if len(args) > 1 else None
        
        user_url = f"{FIREBASE_URL}/users/{user_id}.json"
        res = requests.get(user_url)
        user_data = res.json()
        
        # যদি ইউজার ডাটাবেজে না থাকে
        if not user_data:
            if not referred_by:
                bot.reply_to(message, "⚠️ দুঃখিত! সিস্টেমে রেজিস্ট্রেশন করার জন্য অবশ্যই কারো না কারো রেফারেল লিংক বা কোড ব্যবহার করতে হবে। সঠিক রেফারেল লিংক দিয়ে পুনরায় চেষ্টা করুন।")
                return
            
            # নতুন ইউজারের সঠিক ডাটা স্ট্রাকচার
            user_data = {
                'username': username,
                'first_name': first_name,
                'balance': 0.0,
                'task_balance': 0.0,
                'referral_balance': 0.0,
                'referred_by': referred_by,
                'team_members': [],
                'strike': 0
            }
            # dict-কে সরাসরি json হিসেবে পাঠানো (json.dumps ছাড়া রিকুয়েস্টের ঝামেলা এড়াতে)
            requests.put(user_url, json=user_data)
            
            # রেফারকারী ইউজারের ব্যালেন্স ও টিম আপডেট করা (যেমন: রেফার বোনাস ৳১০)
            if str(referred_by) != str(user_id):
                ref_url = f"{FIREBASE_URL}/users/{referred_by}.json"
                ref_res = requests.get(ref_url)
                ref_data = ref_res.json()
                if ref_data:
                    team = ref_data.get('team_members', [])
                    team.append({'user_id': user_id, 'name': first_name})
                    
                    current_ref_bal = float(ref_data.get('referral_balance', 0.0))
                    new_ref_bal = current_ref_bal + 10.0
                    
                    requests.patch(ref_url, json={
                        'team_members': team, 
                        'referral_balance': new_ref_bal
                    })
            
            bot.reply_to(message, f"🎉 অভিনন্দন, {first_name}! সফলভাবে রেফারেল ভেরিফাই হয়ে আপনার রেজিস্ট্রেশন সম্পন্ন হয়েছে।")
        else:
            bot.reply_to(message, f"স্বাগতম ব্যাক, {first_name}! আপনি ইতিমধ্যেই রেজিস্টার্ড আছেন।")

        show_main_menu(bot, message.chat.id)

    def show_main_menu(bot, chat_id):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            telebot.types.KeyboardButton("📋 উপলব্ধ কাজসমূহ"),
            telebot.types.KeyboardButton("💰 আমার ব্যালেন্স"),
            telebot.types.KeyboardButton("👤 প্রোফাইল ও টিম"),
            telebot.types.KeyboardButton("🔗 রেফারেল লিংক")
        )
        bot.send_message(chat_id, "নিচের মেনু থেকে আপনার প্রয়োজনীয় অপশনটি বেছে নিন:", reply_markup=markup)

    # ২. মেনু অপশন এবং টেক্সট বাটন হ্যান্ডলার
    @bot.message_handler(func=lambda message: message.text in ["📋 উপলব্ধ কাজসমূহ", "💰 আমার ব্যালেন্স", "👤 প্রোফাইল ও টিম", "🔗 রেফারেল লিংক"])
    def handle_menu_options(message):
        user_id = message.from_user.id
        text = message.text
        
        user_url = f"{FIREBASE_URL}/users/{user_id}.json"
        user_data = requests.get(user_url).json()
        
        # রেজিস্টার্ড না থাকলে আটকে দেওয়া
        if not user_data:
            bot.reply_to(message, "⚠️ প্রথমে /start কমান্ড দিয়ে রেজিস্ট্রেশন সম্পন্ন করুন!")
            return

        if text == "📋 উপলব্ধ কাজসমূহ":
            task_text = (
                "🎯 **বর্তমান কাজসমূহ:**\n\n"
                "1️⃣ **ভিডিও মেকিং:** ৩০-৪০ সেকেন্ডের শর্ট ভিডিও\n"
                "2️⃣ **ভয়েস ওভার:** ভালো কন্ঠস্বরে ভয়েস প্রদান\n"
                "3️⃣ **সোশ্যাল শেয়ারিং:** ফেসবুকে লিংক শেয়ার\n\n"
                "💡 **নিয়ম:** কাজ সম্পন্ন করে তার স্ক্রিনশট, ভয়েস বা প্রমাণ সরাসরি এই বোটে পাঠিয়ে দিন! সাথে সাথে আপনার অ্যাকাউন্টে ব্যালেন্স যোগ হয়ে যাবে।"
            )
            bot.reply_to(message, task_text, parse_mode="Markdown")
            
        elif text == "💰 আমার ব্যালেন্স":
            t_bal = float(user_data.get('task_balance', 0.0))
            r_bal = float(user_data.get('referral_balance', 0.0))
            total_bal = t_bal + r_bal
            
            bal_text = (
                f"💳 **আপনার অ্যাকাউন্ট ব্যালেন্স:**\n\n"
                f"🛠️ কাজের ব্যালেন্স: ৳{t_bal}\n"
                f"🎁 রেফারেল ব্যালেন্স: ৳{r_bal}\n"
                f"💵 **মোট ব্যালেন্স:** ৳{total_bal}"
            )
            bot.reply_to(message, bal_text, parse_mode="Markdown")
                
        elif text == "👤 প্রোফাইল ও টিম":
            name = user_data.get('first_name', 'User')
            t_bal = float(user_data.get('task_balance', 0.0))
            r_bal = float(user_data.get('referral_balance', 0.0))
            team = user_data.get('team_members', [])
            
            profile_text = (
                f"👤 **ইউজার প্রোফাইল**\n\n"
                f"🏷️ নাম: {name}\n"
                f"🆔 আইডি: `{user_id}`\n"
                f"🛠️ কাজের ব্যালেন্স: ৳{t_bal}\n"
                f"🎁 রেফারেল ব্যালেন্স: ৳{r_bal}\n"
                f"👥 মোট টিম মেম্বার: {len(team)} জন"
            )
            bot.reply_to(message, profile_text, parse_mode="Markdown")
                
        elif text == "🔗 রেফারেল লিংক":
            ref_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
            ref_msg = (
                f"🔗 **আপনার রেফারেল লিংক:**\n`{ref_link}`\n\n"
                "এই লিংকটি শেয়ার করুন। এর মাধ্যমে নতুন ইউজার জয়েন করলে বাধ্যতামূলকভাবে আপনার রেফারেল কাউন্ট হবে এবং বোনাস যোগ হবে!"
            )
            bot.reply_to(message, ref_msg, parse_mode="Markdown")

    # ৩. কাজ বা মিডিয়া (ভয়েস, ছবি, অডিও, ডকুমেন্ট) সাবমিট করার হ্যান্ডলার
    @bot.message_handler(content_types=['photo', 'voice', 'audio', 'document'])
    def handle_media(message):
        user_id = message.from_user.id
        
        # ইউজার রেজিস্টার্ড কি না চেক করা
        user_url = f"{FIREBASE_URL}/users/{user_id}.json"
        user_data = requests.get(user_url).json()
        
        if not user_data:
            bot.reply_to(message, "⚠️️ কাজ জমা দেওয়ার আগে দয়া করে /start লিখে রেজিস্ট্রেশন করুন।")
            return

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
            
        # সাবমিশন লগ সেভ করা
        submissions_url = f"{FIREBASE_URL}/submissions/{user_id}.json"
        submission_data = {
            'file_id': file_id,
            'file_type': file_type,
            'status': 'approved'
        }
        requests.post(submissions_url, json=submission_data)
        
        # সাথে সাথে কাজের ব্যালেন্স বাড়িয়ে দেওয়া (যেমন: প্রতি কাজের জন্য ৳১০ করে অটো অ্যাড)
        current_task_bal = float(user_data.get('task_balance', 0.0))
        new_task_bal = current_task_bal + 10.0
        
        requests.patch(user_url, json={'task_balance': new_task_bal})
        
        bot.reply_to(message, f"✅ আপনার {file_type} সফলভাবে জমা হয়েছে! টাস্ক সম্পন্ন হওয়ায় আপনার অ্যাকাউন্টে **৳১০** যোগ করা হয়েছে। নতুন ব্যালেন্স দেখতে 'আমার ব্যালেন্স' এ ক্লিক করুন।", parse_mode="Markdown")
