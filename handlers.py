import json
import telebot
import requests

ADMIN_CHAT_ID = "@taskzones" 

def register_handlers(bot, FIREBASE_URL):

    # ১. স্টার্ট কমান্ড ও বাধ্যতামূলক থ্রি-লেভেল রেফারেল চেক (মোট ৫০ টাকা কমিশন)
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
                bot.reply_to(message, "⚠️ দুঃখিত! সিস্টেমে রেজিস্ট্রেশন সম্পন্ন করতে হলে অবশ্যই কোনো একটি বৈধ রেফারেল লিংক ব্যবহার করতে হবে। সঠিক রেফারেল লিংক দিয়ে পুনরায় চেষ্টা করুন।")
                return
            
            user_data = {
                'username': username,
                'first_name': first_name,
                'balance': 0.0,
                'task_balance': 0.0,
                'referral_balance': 0.0,
                'referred_by': referred_by,
                'team_members': [],
                'strike': 0,
                'selected_category': None,
                'daily_tasks': {
                    'video_count': 0,
                    'photo_count': 0,
                    'voice_count': 0,
                    'share_count': 0
                }
            }
            requests.put(user_url, json=user_data)
            
            # থ্রি-লেভেল রেফারেল কমিশন ডিস্ট্রিবিউশন (Level A: 35৳, Level B: 10৳, Level C: 5৳)
            if str(referred_by) != str(user_id):
                ref_a_url = f"{FIREBASE_URL}/users/{referred_by}.json"
                ref_a_res = requests.get(ref_a_url)
                ref_a_data = ref_a_res.json()
                
                if ref_a_data:
                    team_a = ref_a_data.get('team_members', [])
                    team_a.append({'user_id': user_id, 'name': first_name})
                    current_ref_bal_a = float(ref_a_data.get('referral_balance', 0.0))
                    new_ref_bal_a = current_ref_bal_a + 35.0
                    requests.patch(ref_a_url, json={'team_members': team_a, 'referral_balance': new_ref_bal_a})
                    
                    level_b_ref = ref_a_data.get('referred_by')
                    if level_b_ref:
                        ref_b_url = f"{FIREBASE_URL}/users/{level_b_ref}.json"
                        ref_b_res = requests.get(ref_b_url)
                        ref_b_data = ref_b_res.json()
                        if ref_b_data:
                            current_ref_bal_b = float(ref_b_data.get('referral_balance', 0.0))
                            new_ref_bal_b = current_ref_bal_b + 10.0
                            requests.patch(ref_b_url, json={'referral_balance': new_ref_bal_b})
                            
                            level_c_ref = ref_b_data.get('referred_by')
                            if level_c_ref:
                                ref_c_url = f"{FIREBASE_URL}/users/{level_c_ref}.json"
                                ref_c_res = requests.get(ref_c_url)
                                ref_c_data = ref_c_res.json()
                                if ref_c_data:
                                    current_ref_bal_c = float(ref_c_data.get('referral_balance', 0.0))
                                    new_ref_bal_c = current_ref_bal_c + 5.0
                                    requests.patch(ref_c_url, json={'referral_balance': new_ref_bal_c})
            
            bot.reply_to(message, f"🎉 অভিনন্দন, {first_name}! সফলভাবে রেফারেল যাচাইপূর্বক আপনার রেজিস্ট্রেশন সম্পন্ন হয়েছে।")
        else:
            bot.reply_to(message, f"স্বাগতম ব্যাক, {first_name}! আপনি ইতিমধ্যেই আমাদের সিস্টেমে রেজিস্টার্ড আছেন।")

        show_main_menu(bot, message.chat.id)

    def show_main_menu(bot, chat_id):
        markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
        markup.add(
            telebot.types.KeyboardButton("💼 চলমান প্রজেক্টসমূহ"),
            telebot.types.KeyboardButton("🚀 প্রুফ সাবমিট করুন"),
            telebot.types.KeyboardButton("💰 আমার আর্নিংস"),
            telebot.types.KeyboardButton("👤 পারসোনাল ড্যাশবোর্ড"),
            telebot.types.KeyboardButton("🔗 ইনভাইট লিংক")
        )
        bot.send_message(chat_id, "✨ নিচের প্রিমিয়াম অপশনগুলো থেকে আপনার কাঙ্ক্ষিত সেবাটি বেছে নিন:", reply_markup=markup)

    # ২. মেনু অপশন হ্যান্ডলার (ফায়ারবেস থেকে ডাইনামিক টাস্ক কনফিগ ও স্ক্রিপ্ট ফেচ করা)
    @bot.message_handler(func=lambda message: message.text in ["💼 চলমান প্রজেক্টসমূহ", "🚀 প্রুফ সাবমিট করুন", "💰 আমার আর্নিংস", "👤 পারসোনাল ড্যাশবোর্ড", "🔗 ইনভাইট লিংক"])
    def handle_menu_options(message):
        user_id = message.from_user.id
        text = message.text
        
        user_url = f"{FIREBASE_URL}/users/{user_id}.json"
        user_data = requests.get(user_url).json()
        
        if not user_data:
            bot.reply_to(message, "⚠️ অনুগ্রহ করে প্রথমে /start কমান্ড টাইপ করে রেজিস্ট্রেশন প্রক্রিয়া সম্পন্ন করুন!")
            return

        # ফায়ারবেস থেকে ডাইনামিক টাস্ক কনফিগ বা স্ক্রিপ্ট রিড করা
        config_url = f"{FIREBASE_URL}/tasks_config.json"
        config_data = requests.get(config_url).json() or {}

        video_script = config_data.get('video', {}).get('script', 'নমুনা ভিডিও বা স্ক্রিপ্ট শীঘ্রই আপডেট করা হবে।')
        photo_script = config_data.get('photo', {}).get('script', 'ছবি বা লোগোর রিকোয়ারমেন্ট শীঘ্রই আপডেট করা হবে।')
        voice_script = config_data.get('voice', {}).get('script', 'ভয়েস ওভারের জন্য নির্ধারিত স্ক্রিপ্ট এখানে থাকবে।')
        share_link = config_data.get('share', {}).get('link', 'শেয়ার করার জন্য নির্ধারিত লিংকটি এখানে থাকবে।')

        if text == "💼 চলমান প্রজেক্টসমূহ":
            task_text = (
                "🎯 **সক্রিয় প্রজেক্ট, স্ক্রিপ্ট ও কাজের বিবরণসমূহ:**\n\n"
                f"🎥 **১. ভিডিও এডিটিং (রেট: ৳৪০ | দৈনিক সর্বোচ্চ: ২টি)**\n"
                f"   • *নির্দেশনা/স্ক্রিপ্ট:* {video_script}\n\n"
                f"📸 **২. ছবি এডিটিং (রেট: ৳২০ | দৈনিক সর্বোচ্চ: ৩টি)**\n"
                f"   • *নির্দেশনা:* {photo_script}\n\n"
                f"🎙️ **৩. ভয়েস ওভার / অডিও (রেট: ৳১৫ | দৈনিক সর্বোচ্চ: ৩টি)**\n"
                f"   • *স্ক্রিপ্ট:* {voice_script}\n\n"
                f"🔗 **৪. লিংক বা ভিডিও শেয়ারিং (রেট: ৳১০ | দৈনিক সর্বোচ্চ: ৫টি)**\n"
                f"   • *শেয়ার লিংক:* {share_link}\n\n"
                "⭐ **বিশেষ দ্রষ্টব্য:** কাজের কোয়ালিটি বা মান চমৎকার ও নিখুঁত হলে অ্যাডমিন প্যানেল থেকে বিশেষ বোনাস দেওয়া হবে!\n\n"
                "💡 কাজ সম্পন্ন করার পর প্রুফ জমা দিতে নিচের **'🚀 প্রুফ সাবমিট করুন'** অপশনে ক্লিক করুন।"
            )
            bot.reply_to(message, task_text, parse_mode="Markdown")
            
        elif text == "🚀 প্রুফ সাবমিট করুন":
            markup = telebot.types.InlineKeyboardMarkup(row_width=2)
            markup.add(
                telebot.types.InlineKeyboardButton("🎥 ভিডিও এডিটিং (৳৪০)", callback_data="cat_video"),
                telebot.types.InlineKeyboardButton("📸 ছবি এডিটিং (৳২০)", callback_data="cat_photo"),
                telebot.types.InlineKeyboardButton("🎙️ ভয়েস ওভার (৳১৫)", callback_data="cat_voice"),
                telebot.types.InlineKeyboardButton("🔗 শেয়ারিং প্রুফ (৳১০)", callback_data="cat_share")
            )
            bot.reply_to(message, "📂 আপনি কোন ক্যাটাগরির কাজ জমা দিতে চান? নিচের বাটন থেকে যথাযথ ক্যাটাগরি সিলেক্ট করুন:", reply_markup=markup)
            
        elif text == "💰 আমার আর্নিংস":
            t_bal = float(user_data.get('task_balance', 0.0))
            r_bal = float(user_data.get('referral_balance', 0.0))
            total_bal = t_bal + r_bal
            strike_count = user_data.get('strike', 0)
            
            bal_text = (
                f"💳 **আপনার অ্যাকাউন্ট আর্নিংস সামারি:**\n\n"
                f"🛠️ প্রজেক্ট ব্যালেন্স: ৳{t_bal}\n"
                f"🎁 রেফারেল বোনাস: ৳{r_bal}\n"
                f"💵 **মোট ব্যালেন্স:** ৳{total_bal}\n"
                f"⚠️ **সতর্কতা / স্ট্রাইক:** {strike_count} টি"
            )
            bot.reply_to(message, bal_text, parse_mode="Markdown")
                
        elif text == "👤 পারসোনাল ড্যাশবোর্ড":
            name = user_data.get('first_name', 'User')
            t_bal = float(user_data.get('task_balance', 0.0))
            r_bal = float(user_data.get('referral_balance', 0.0))
            team = user_data.get('team_members', [])
            strike_count = user_data.get('strike', 0)
            
            profile_text = (
                f"👤 **ইউজার পারসোনাল ড্যাশবোর্ড**\n\n"
                f"🏷️ নাম: {name}\n"
                f"🆔 আইডি: `{user_id}`\n"
                f"🛠️ প্রজেক্ট ব্যালেন্স: ৳{t_bal}\n"
                f"🎁 রেফারেল ব্যালেন্স: ৳{r_bal}\n"
                f"👥 মোট টিম মেম্বার: {len(team)} জন\n"
                f"⚠️ স্ট্রাইক স্ট্যাটাস: {strike_count} টি"
            )
            bot.reply_to(message, profile_text, parse_mode="Markdown")
                
        elif text == "🔗 ইনভাইট লিংক":
            ref_link = f"https://t.me/{bot.get_me().username}?start={user_id}"
            ref_msg = (
                f"🔗 **আপনার ইউনিক রেফারেল লিংক:**\n`{ref_link}`\n\n"
                "এই লিংকটি আপনার বন্ধুদের সাথে শেয়ার করুন। নতুন মেম্বার যুক্ত হলে থ্রি-লেভেল সিস্টেমে মোট **৳৫০** পর্যন্ত রেফারেল কমিশন আপনার অ্যাকাউন্টে যোগ হবে!"
            )
            bot.reply_to(message, ref_msg, parse_mode="Markdown")

    # ৩. কাজের ক্যাটাগরি সিলেকশন হ্যান্ডলার (ডেইলি লিমিট চেকসহ)
    @bot.callback_query_handler(func=lambda call: call.data.startswith("cat_"))
    def handle_category_selection(call):
        user_id = call.from_user.id
        category_map = {
            "cat_video": "🎥 ভিডিও এডিটিং",
            "cat_photo": "📸 ছবি এডিটিং",
            "cat_voice": "🎙️ ভয়েস ওভার",
            "cat_share": "🔗 শেয়ারিং প্রুফ"
        }
        cat_key = call.data.replace("cat_", "")
        selected_cat = category_map.get(call.data, "সাধারণ প্রুফ")
        
        user_url = f"{FIREBASE_URL}/users/{user_id}.json"
        user_data = requests.get(user_url).json() or {}
        daily_tasks = user_data.get('daily_tasks', {'video_count': 0, 'photo_count': 0, 'voice_count': 0, 'share_count': 0})
        
        limits = {
            "video": (2, "ভিডিও এডিটিং দৈনিক সর্বোচ্চ ২টি করা যাবে।"),
            "photo": (3, "ছবি এডিটিং দৈনিক সর্বোচ্চ ৩টি করা যাবে।"),
            "voice": (3, "ভয়েস ওভার দৈনিক সর্বোচ্চ ৩টি করা যাবে।"),
            "share": (5, "শেয়ারিং দৈনিক সর্বোচ্চ ৫টি করা যাবে।")
        }
        
        max_limit, limit_msg = limits.get(cat_key, (10, ""))
        current_count = daily_tasks.get(f"{cat_key}_count", 0)
        
        if current_count >= max_limit:
            bot.answer_callback_query(call.id, f"⚠️ দুঃখিত! আজকের জন্য আপনার এই টাস্কের লিমিট শেষ।", show_alert=True)
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"⚠️ **দৈনিক লিমিট পূর্ণ!**\n\n{limit_msg}",
                parse_mode="Markdown"
            )
            return
            
        requests.patch(user_url, json={'selected_category': selected_cat})
        
        bot.answer_callback_query(call.id, f"✅ সফলভাবে নির্বাচিত হয়েছে: {selected_cat}")
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"✅ আপনি নির্বাচিত করেছেন: **{selected_cat}**\n\nএখন আপনার প্রুফ বা মিডিয়া ফাইলটি সরাসরি এই চ্যাটে পাঠিয়ে দিন।",
            parse_mode="Markdown"
        )

    # ৪. কাজ বা মিডিয়া সাবমিট হ্যান্ডলার
    @bot.message_handler(content_types=['photo', 'voice', 'audio', 'document'])
    def handle_media(message):
        user_id = message.from_user.id
        user_url = f"{FIREBASE_URL}/users/{user_id}.json"
        user_data = requests.get(user_url).json()
        
        if not user_data:
            bot.reply_to(message, "⚠️ প্রুফ জমা দেওয়ার পূর্বে অনুগ্রহ করে /start লিখে রেজিস্ট্রেশন সম্পন্ন করুন।")
            return

        selected_category = user_data.get('selected_category')
        if not selected_category:
            bot.reply_to
