import requests
import json
import telebot

# আপনার টেলিগ্রাম চ্যানেলের ইউজারনেম এখানে সেট করা হলো
ADMIN_CHAT_ID = "@taskzones" 

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
        
        if not user_data:
            if not referred_by:
                bot.reply_to(message, "⚠️ দুঃখিত! সিস্টেমে রেজিস্ট্রেশন করার জন্য অবশ্যই কারো না কারো রেফারেল লিংক বা কোড ব্যবহার করতে হবে। সঠিক রেফারেল লিংক দিয়ে পুনরায় চেষ্টা করুন।")
                return
            
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
            requests.put(user_url, json=user_data)
            
            if str(referred_by) != str(user_id):
                ref_url = f"{FIREBASE_URL}/users/{referred_by}.json"
                ref_res = requests.get(ref_url)
                ref_data = ref_res.json()
                if ref_data:
                    team = ref_data.get('team_members', [])
                    team.append({'user_id': user_id, 'name': first_name})
                    current_ref_bal = float(ref_data.get('referral_balance', 0.0))
                    new_ref_bal = current_ref_bal + 10.0
                    requests.patch(ref_url, json={'team_members': team, 'referral_balance': new_ref_bal})
            
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

    # ২. মেনু অপশন হ্যান্ডলার
    @bot.message_handler(func=lambda message: message.text in ["📋 উপলব্ধ কাজসমূহ", "💰 আমার ব্যালেন্স", "👤 প্রোফাইল ও টিম", "🔗 রেফারেল লিংক"])
    def handle_menu_options(message):
        user_id = message.from_user.id
        text = message.text
        
        user_url = f"{FIREBASE_URL}/users/{user_id}.json"
        user_data = requests.get(user_url).json()
        
        if not user_data:
            bot.reply_to(message, "⚠️ প্রথমে /start কমান্ড দিয়ে রেজিস্ট্রেশন সম্পন্ন করুন!")
            return

        if text == "📋 উপলব্ধ কাজসমূহ":
            task_text = (
                "🎯 **বর্তমান কাজসমূহ:**\n\n"
                "1️⃣ **ভিডিও মেকিং:** ৩০-৪০ সেকেন্ডের শর্ট ভিডিও\n"
                "2️⃣ **ভয়েস ওভার:** ভালো কন্ঠস্বরে ভয়েস প্রদান\n"
                "3️⃣ **সোশ্যাল শেয়ারিং:** ফেসবুকে লিংক শেয়ার\n\n"
                "💡 **নিয়ম:** কাজ সম্পন্ন করে তার প্রমাণ (স্ক্রিনশট বা ফাইল) সরাসরি এই বোটে পাঠান। একই প্রুফ বারবার পাঠালে স্ট্রাইক খাওয়া হবে!"
            )
            bot.reply_to(message, task_text, parse_mode="Markdown")
            
        elif text == "💰 আমার ব্যালেন্স":
            t_bal = float(user_data.get('task_balance', 0.0))
            r_bal = float(user_data.get('referral_balance', 0.0))
            total_bal = t_bal + r_bal
            strike_count = user_data.get('strike', 0)
            
            bal_text = (
                f"💳 **আপনার অ্যাকাউন্ট ব্যালেন্স:**\n\n"
                f"🛠️ কাজের ব্যালেন্স: ৳{t_bal}\n"
                f"🎁 রেফারেল ব্যালেন্স: ৳{r_bal}\n"
                f"💵 **মোট ব্যালেন্স:** ৳{total_bal}\n"
                f"⚠️ **স্ট্রাইক/ওয়ার্নিং:** {strike_count} টি"
            )
            bot.reply_to(message, bal_text, parse_mode="Markdown")
                
        elif text == "👤 প্রোফাইল ও টিম":
            name = user_data.get('first_name', 'User')
            t_bal = float(user_data.get('task_balance', 0.0))
            r_bal = float(user_data.get('referral_balance', 0.0))
            team = user_data.get('team_members', [])
            strike_count = user_data.get('strike', 0)
            
            profile_text = (
                f"👤 **ইউজার প্রোফাইল**\n\n"
                f"🏷️ নাম: {name}\n"
                f"🆔 আইডি: `{user_id}`\n"
                f"🛠️ কাজের ব্যালেন্স: ৳{t_bal}\n"
                f"🎁 রেফারেল ব্যালেন্স: ৳{r_bal}\n"
                f"👥 মোট টিম মেম্বার: {len(team)} জন\n"
                f"⚠️ স্ট্রাইক: {strike_count} টি"
            )
            bot.reply_to(message, profile_text, parse_mode="Markdown")
                
        elif text == "🔗 রেফারেল লিংক":
            ref_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
            ref_msg = (
                f"🔗 **আপনার রেফারেল লিংক:**\n`{ref_link}`\n\n"
                "এই লিংকটি শেয়ার করুন। এর মাধ্যমে নতুন ইউজার জয়েন করলে আপনার রেফারেল ব্যালেন্স যোগ হবে!"
            )
            bot.reply_to(message, ref_msg, parse_mode="Markdown")

    # ৩. কাজ বা মিডিয়া সাবমিট হ্যান্ডলার (ডুপ্লিকেট চেক, স্ট্রাইক সিস্টেম ও স্টার রেটিং সহ)
    @bot.message_handler(content_types=['photo', 'voice', 'audio', 'document'])
    def handle_media(message):
        user_id = message.from_user.id
        user_url = f"{FIREBASE_URL}/users/{user_id}.json"
        user_data = requests.get(user_url).json()
        
        if not user_data:
            bot.reply_to(message, "⚠ কাজ জমা দেওয়ার আগে দয়া করে /start লিখে রেজিস্ট্রেশন করুন।")
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

        # ডুপ্লিকেট সাবমিশন বা স্প্যাম চেক করা
        submissions_url = f"{FIREBASE_URL}/submissions/{user_id}.json"
        existing_subs = requests.get(submissions_url).json() or {}
        
        is_duplicate = False
        for sub_key, sub_val in existing_subs.items():
            if isinstance(sub_val, dict) and sub_val.get('file_id') == file_id:
                is_duplicate = True
                break

        if is_duplicate:
            current_strikes = int(user_data.get('strike', 0)) + 1
            requests.patch(user_url, json={'strike': current_strikes})
            
            bot.reply_to(message, f"❌ **সতর্কবার্তা!** আপনি এই একই প্রমাণ বা ফাইল ইতিপূর্বেও জমা দিয়েছেন। ডুপ্লিকেট প্রুফ জমা দেওয়ার কারণে আপনাকে একটি **স্ট্রাইক ({current_strikes})** দেওয়া হলো।", parse_mode="Markdown")
            return

        # নতুন সাবমিশন সেভ করা
        new_sub_data = {
            'file_id': file_id,
            'file_type': file_type,
            'status': 'approved'
        }
        requests.post(submissions_url, json=new_sub_data)
        
        # ইউজারের কাজের ব্যালেন্স বাড়িয়ে দেওয়া (প্রতি টাস্কে ৳১০)
        current_task_bal = float(user_data.get('task_balance', 0.0))
        new_task_bal = current_task_bal + 10.0
        requests.patch(user_url, json={'task_balance': new_task_bal})
        
        bot.reply_to(message, f"✅ আপনার {file_type} সফলভাবে জমা হয়েছে! টাস্ক সম্পন্ন হওয়ায় আপনার অ্যাকাউন্টে **৳১০** যোগ করা হয়েছে।", parse_mode="Markdown")

        # ৪. চ্যানেলে প্রুফ ফরোয়ার্ড করা এবং ১-৫ স্টার রেটিং বাটন যুক্ত করা
        try:
            markup = telebot.types.InlineKeyboardMarkup(row_width=5)
            markup.add(
                telebot.types.InlineKeyboardButton("⭐ 1", callback_data="rate_1"),
                telebot.types.InlineKeyboardButton("⭐ 2", callback_data="rate_2"),
                telebot.types.InlineKeyboardButton("⭐ 3", callback_data="rate_3"),
                telebot.types.InlineKeyboardButton("⭐ 4", callback_data="rate_4"),
                telebot.types.InlineKeyboardButton("⭐ 5", callback_data="rate_5")
            )
            
            caption = (
                f"📥 **নতুন টাস্ক প্রুফ ও রেটিং:**\n\n"
                f"👤 নাম: {user_data.get('first_name')}\n"
                f"🆔 আইডি: `{user_id}`\n"
                f"📂 ফাইলের ধরণ: {file_type}\n"
                f"⭐ স্টার রেটিং: এখনো দেওয়া হয়নি"
            )
            
            bot.send_message(ADMIN_CHAT_ID, caption, parse_mode="Markdown", reply_markup=markup)
            bot.forward_message(ADMIN_CHAT_ID, message.chat.id, message.message_id)
        except Exception as e:
            print(f"Channel forward error: {e}")

    # ৫. স্টার রেটিং বাটন হ্যান্ডলার
    @bot.callback_query_handler(func=lambda call: call.data.startswith("rate_"))
    def handle_rating(call):
        try:
            rating_value = int(call.data.split("_")[1])
            message = call.message
            old_text = message.text
            
            bot.answer_callback_query(call.id, f"✅ আপনি সফলভাবে {rating_value} স্টার রেটিং দিয়েছেন!")
            
            new_caption = old_text + f"\n\n✨ রেটিং প্রদান করা হয়েছে: {rating_value} স্টার ⭐"
            
            bot.edit_message_text(
                chat_id=message.chat.id,
                message_id=message.message_id,
                text=new_caption,
                reply_markup=message.reply_markup
            )
        except Exception as e:
            print(f"Rating error: {e}")

    # ৬. সাপ্তাহিক লিডারবোর্ড বা টপ ১০ তালিকা (ডামি ডাটা সহ)
    @bot.message_handler(commands=['top10', 'top_posts'])
    def show_top_creators(message):
        try:
            users_url = f"{FIREBASE_URL}/users.json"
            users_res = requests.get(users_url).json() or {}
            
            user_scores = []
            
            for uid, udata in users_res.items():
                if isinstance(udata, dict):
                    name = udata.get('first_name', 'User')
                    score = float(udata.get('task_balance', 0.0)) + float(udata.get('referral_balance', 0.0))
                    user_scores.append({'name': name, 'score': score})
            
            # আকর্ষণীয় ডামি ইউজার যারা লিস্ট পূর্ণ রাখবে
            dummy_users = [
                {'name': 'Rakibul Islam', 'score': 1250.0},
                {'name': 'Tanvir Ahmed', 'score': 980.0},
                {'name': 'Nazmul Hossain', 'score': 850.0},
                {'name': 'Sumaiya Akter', 'score': 720.0},
                {'name': 'Mehedi Hasan', 'score': 640.0},
                {'name': 'Farhana Yeasmin', 'score': 550.0},
                {'name': 'Imran Khan', 'score': 490.0},
                {'name': 'Sharmin Sultana', 'score': 410.0},
                {'name': 'Al-Amin Hossain', 'score': 350.0},
                {'name': 'Nusrat Jahan', 'score': 300.0}
            ]
            
            for dummy in dummy_users:
                if len(user_scores) < 10:
                    if not any(u['name'] == dummy['name'] for u in user_scores):
                        user_scores.append(dummy)
            
            user_scores = sorted(user_scores, key=lambda x: x['score'], reverse=True)
            
            top_10_text = (
                "🏆 **Task Zone - সাপ্তাহিক সেরা ১০ পারফর্মার লিডারবোর্ড** 🏆\n\n"
                "✨ প্রতি সপ্তাহের সেরা ৩ জন বিজয়ী পাবেন আকর্ষণীয় ক্যাশ প্রাইস ও বোনাস পুরস্কার!\n\n"
            )
            
            for index, user in enumerate(user_scores[:10], start=1):
                medal = "🥇" if index == 1 else "🥈" if index == 2 else "🥉" if index == 3 else f"{index}."
                top_10_text += f"{medal} **{user['name']}** — ৳{user['score']} পয়েন্ট\n"
            
            top_10_text += "\n💡 আপনার নাম এই তালিকায় তুলতে নিয়মিত কাজ করুন এবং বেশি বেশি রেফার করুন!"
            
            bot.reply_to(message, top_10_text, parse_mode="Markdown")
            
        except Exception as e:
            print(f"Top 10 error: {e}")
            bot.reply_to(message, "⚠️ দুঃখಿತ, লিডারবোর্ড লোড করতে সমস্যা হয়েছে।")
