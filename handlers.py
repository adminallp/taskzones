import requests
import json
import telebot

# main.py থেকে bot এবং FIREBASE_URL ইম্পোর্ট করে ব্যবহার করা যাবে
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
        
        # যদি ইউজার নতুন হয় এবং রেফারেল কোড বাধ্যতামূলক করতে চান
        if not user_data:
            if not referred_by:
                bot.reply_to(message, "⚠️ দুঃখিত! সিস্টেমে রেজিস্ট্রেশন করার জন্য অবশ্যই কারো না কারো রেফারেল লিংক বা কোড ব্যবহার করতে হবে। সঠিক রেফারেল লিংক দিয়ে পুনরায় চেষ্টা করুন।")
                return
            
            # নতুন ইউজারের ডাটা তৈরি
            user_data = {
                'first_name': first_name,
                'username': username,
                'task_balance': 0.0,
                'referral_balance': 0.0,
                'referred_by': referred_by,
                'team_members': []
            }
            requests.put(user_url, json=json.dumps(user_data))
            
            # রেফারকারী ইউজারের টিম এবং ব্যালেন্স আপডেট করা (যেমন: ডিরেক্ট রেফার বোনাস ৳৭০)
            if str(referred_by) != str(user_id):
                ref_url = f"{FIREBASE_URL}/users/{referred_by}.json"
                ref_res = requests.get(ref_url)
                ref_data = ref_res.json()
                if ref_data:
                    team = ref_data.get('team_members', [])
                    team.append({'user_id': user_id, 'name': first_name})
                    ref_balance = ref_data.get('referral_balance', 0.0) + 70.0
                    requests.patch(ref_url, json=json.dumps({'team_members': team, 'referral_balance': ref_balance}))
            
            bot.reply_to(message, f"🎉 অভিনন্দন, {first_name}! সফলভাবে রেফারেল কোড ভেরিফাই হয়ে আপনার রেজিস্ট্রেশন সম্পন্ন হয়েছে।")
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

    # ২. মেনু অপশন হ্যান্ডলার
    @bot.message_handler(func=lambda message: True)
    def handle_menu_options(message):
        user_id = message.from_user.id
        text = message.text
        
        if text == "📋 উপলব্ধ কাজসমূহ":
            task_text = (
                "🎯 **বর্তমান কাজসমূহ:**\n\n"
                "1️⃣ **ভিডিও মেকিং:** ৩০-৪০ সেকেন্ডের শর্ট ভিডিও (রিওয়ার্ড: ৳১০ - ৳১৫)\n"
                "2️⃣ **ভয়েস ওভার:** ভালো কন্ঠস্বরে ভয়েস প্রদান (রিওয়ার্ড: ৳৫ - ৳৮)\n"
                "3️⃣ **সোশ্যাল শেয়ারিং:** ফেসবুকে লিংক শেয়ার\n\n"
                "💡 কাজ সম্পন্ন করে তার প্রুফ সরাসরি এই বোটে পাঠিয়ে দিন!"
            )
            bot.reply_to(message, task_text, parse_mode="Markdown")
            
        elif text == "💰 আমার ব্যালেন্স":
            user_url = f"{FIREBASE_URL}/users/{user_id}.json"
            user_data = requests.get(user_url).json()
            if user_data:
                t_bal = user_data.get('task_balance', 0.0)
                r_bal = user_data.get('referral_balance', 0.0)
                bal_text = (
                    f"💳 **আপনার অ্যাকাউন্ট ব্যালেন্স:**\n\n"
                    f"🛠️ কাজের ব্যালেন্স (Task Balance): ৳{t_bal}\n"
                    f"🎁 রেফারেল ব্যালেন্স (Referral Balance): ৳{r_bal}\n"
                    f"💵 **মোট ব্যালেন্স:** ৳{t_bal + r_bal}"
                )
                bot.reply_to(message, bal_text, parse_mode="Markdown")
                
        elif text == "👤 প্রোফাইল ও টিম":
            user_url = f"{FIREBASE_URL}/users/{user_id}.json"
            user_data = requests.get(user_url).json()
            if user_data:
                name = user_data.get('first_name')
                t_bal = user_data.get('task_balance', 0.0)
                r_bal = user_data.get('referral_balance', 0.0)
                team = user_data.get('team_members', [])
                
                profile_text = (
                    f"👤 **ইউজার প্রোফাইল**\n\n"
                    f"🏷️ নাম: {name}\n"
                    f"🆔 আইডি: `{user_id}`\n"
                    f"🛠️ কাজের ব্যালেন্স: ৳{t_bal}\n"
                    f"🎁 রেফারেল ব্যালেন্স: ৳{r_bal}\n"
                    f"👥 মোট টিম মেম্বার: {len(team)} জন\n"
                )
                bot.reply_to(message, profile_text, parse_mode="Markdown")
                
        elif text == "🔗 রেফারেল লিংক":
            ref_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
            ref_msg = (
                f"🔗 **আপনার রেফারেল লিংক:**\n`{ref_link}`\n\n"
                "এই লিংকটি শেয়ার করুন। এর মাধ্যমে নতুন ইউজার জয়েন করলে বাধ্যতামূলকভাবে আপনার রেফারেল কাউন্ট হবে!"
            )
            bot.reply_to(message, ref_msg, parse_mode="Markdown")
