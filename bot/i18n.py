"""Ikki tilli matnlar: o'zbek (uz) va rus (ru)."""

TEXTS: dict[str, dict[str, str]] = {
    "uz": {
        "choose_lang": "🌐 Tilni tanlang / Выберите язык:",
        # ---------- Bot haqida / onboarding ----------
        "welcome": (
            "👋 Assalomu alaykum, <b>{name}</b>!\n\n"
            "🎮 <b>Gamebozor</b> — o'yin akkauntlari va xizmatlari e'lonlari bozori.\n\n"
            "Bu yerda siz:\n"
            "🔎 akkauntlarni <b>umumiy ko'rsatkich, o'yinchilar, packlar va narx</b> bo'yicha izlaysiz;\n"
            "➕ o'z akkauntingizni bir necha daqiqada sotuvga qo'yasiz;\n"
            "🛡 sotuvchini firibgarlar ro'yxatidan tekshirasiz;\n"
            "🔔 mos e'lon chiqishi bilan xabar olasiz.\n\n"
            "⚠️ <b>Muhim:</b> Gamebozor — faqat e'lonlar taxtasi. Biz <b>garant (kafil) emasmiz</b>, "
            "to'lovlar va oldi-sotdi uchun javobgar emasmiz.\n\n"
            "Boshlashdan oldin qisqa qo'llanma va qoidalar bilan tanishib chiqing 👇"
        ),
        "btn_guide": "📖 Qo'llanma",
        "btn_rules": "📜 Qoidalar",
        "btn_accept": "✅ Qoidalarni o'qidim va roziman",
        "btn_to_dash": "🏠 Dashboardga o'tish",
        "btn_next": "Keyingi ▶️",
        "btn_prev": "◀️ Oldingi",
        "rules_accepted": "🤝 Rahmat! Qoidalarga rozilik qabul qilindi. Endi botdan to'liq foydalanishingiz mumkin.",
        "need_rules": "📜 Bu amal uchun avval qoidalar bilan tanishib, rozilik bildiring.",
        "guide": [
            "📖 <b>Qo'llanma 1/5 — Dashboard</b>\n\n"
            "🏠 <b>Dashboard</b> — botning boshqaruv paneli. Bitta xabar ichida hamma bo'limlar:\n"
            "• o'yinlar bo'limlari va bozor ko'rsatkichlari\n• qidiruv va filtrlar\n• profilingiz, e'lonlaringiz\n"
            "• qoidalar va yordam\n\nDashboard'ni istalgan payt pastdagi «🏠 Dashboard» tugmasi yoki /menu bilan ochasiz.",
            "📖 <b>Qo'llanma 2/5 — Qidiruv</b>\n\n"
            "🔎 Qidiruvda filtrlarni birlashtirasiz:\n"
            "💵 narx oralig'i (masalan <code>500k-2mln</code>)\n"
            "💪 umumiy ko'rsatkich (Team Strength) — kamida N\n"
            "🟣 Epic / 🟠 Big Time soni\n⭐️ o'yinchi nomi (Messi, Mbappe...)\n📦 pack nomi (POTW, Highlight...)\n"
            "📱 platforma, 🔗 bog'lanish, 🏆 division\n\n"
            "Tez qidiruv: <code>/search messi 3200</code> yoki istalgan chatda <code>@{bot} messi</code>.",
            "📖 <b>Qo'llanma 3/5 — Sotib olish</b>\n\n"
            "1️⃣ E'lonni oching, skrinshotlarni ko'ring.\n2️⃣ «📞 Bog'lanish» — sotuvchi kontakti chiqadi.\n"
            "3️⃣ Sotuvchini 🛡 tekshiring (qora ro'yxat, shikoyatlar, savdo tarixi).\n"
            "4️⃣ Akkauntga kirib, pochta/telefon/bog'lanishni <b>o'zingizga o'tkazmaguncha</b> to'liq pul bermang.\n\n"
            "❤️ yoqqanini saralanganlarga qo'shing, 🔔 qidiruvga obuna bo'ling — mos e'lon chiqsa xabar beramiz.",
            "📖 <b>Qo'llanma 4/5 — Sotish</b>\n\n"
            "1️⃣ «➕ E'lon berish» → o'yin → forma (ko'rsatkichlar, o'yinchilar, packlar).\n"
            "2️⃣ Narx, izoh va 1–10 ta skrinshot.\n3️⃣ Admin tekshiradi (odatda 1–3 soat) → bot va {channel} kanalida chiqadi.\n"
            "4️⃣ Sotilgach «✅ Sotildi» ni bosing.\n\n"
            "🚀 <b>TOP</b> — e'lon ro'yxat boshida turadi va kanalda 🔥 bilan qayta chiqadi (Telegram Stars ⭐️).",
            "📖 <b>Qo'llanma 5/5 — Xavfsizlik</b>\n\n"
            "🚫 Bot va adminlar hech qachon login, parol, SMS-kod so'ramaydi.\n"
            "🚫 «Gamebozor garanti/admini» nomidan pul so'ralsa — bu <b>firibgar</b>. Biz pul qabul qilmaymiz.\n"
            "🚫 Oldindan to'liq to'lov qilmang, avval akkauntni tekshiring.\n"
            "🚩 Shubhali e'lonni shikoyat qiling — adminlar ko'rib chiqadi.\n\n"
            "⌨️ Barcha buyruqlar: pastdagi <b>/</b> menyusi yoki /commands.",
        ],
        "rules": (
            "📜 <b>Gamebozor qoidalari</b>\n\n"
            "<b>1. Platforma maqomi</b>\n"
            "Gamebozor — faqat e'lonlar taxtasi. Biz sotuvchi ham, xaridor ham, vositachi ham emasmiz.\n\n"
            "<b>2. ❗️ Biz garant (kafil) EMASMIZ</b>\n"
            "• Akkauntlar oldi-sotdisi, to'lovlar va ularning oqibatlari uchun <b>hech qanday javobgarlik olmaymiz</b>.\n"
            "• Pul va akkaunt to'g'ridan-to'g'ri sotuvchi va xaridor o'rtasida o'tadi — barcha xavf tomonlarning o'zida.\n"
            "• Firibgarlik, aldov, akkauntni qaytarib olish (recovery) holatlarida yo'qotilgan mablag'ni qoplamaymiz.\n"
            "• Bot hech qachon pul qabul qilmaydi (faqat TOP xizmati — Telegram Stars orqali). "
            "Kim «Gamebozor garanti/admini» nomidan pul so'rasa — firibgar.\n\n"
            "<b>3. Shaxsiy ma'lumotlar</b>\n"
            "Login, parol, SMS-kod, karta ma'lumotlarini botga va hech kimga yubormang — biz ularni so'ramaymiz.\n\n"
            "<b>4. O'yin qoidalari</b>\n"
            "Akkaunt sotish o'yin noshiri (Konami, Krafton va b.) qoidalariga zid bo'lishi va bloklanishga olib "
            "kelishi mumkin. Bu xavfni foydalanuvchi o'zi zimmasiga oladi.\n\n"
            "<b>5. E'lon talablari</b>\n"
            "• Faqat o'zingizga tegishli akkauntni soting.\n• Haqiqiy skrinshotlar va real ma'lumotlar.\n"
            "• Bitta akkaunt — bitta e'lon; takroriy e'lon taqiqlanadi.\n\n"
            "<b>6. Taqiqlanadi</b>\n"
            "O'g'irlangan/buzilgan akkauntlar, yolg'on ma'lumot, firibgarlik, haqorat, spam va boshqa "
            "bozorlar reklamasi.\n\n"
            "<b>7. Choralar</b>\n"
            "Qoida buzilsa: e'lon o'chiriladi, foydalanuvchi bloklanadi va firibgarlar ro'yxatiga kiritiladi. "
            "Adminlar e'lonni rad etish yoki o'chirish huquqiga ega.\n\n"
            "<b>8. TOP xizmati</b>\n"
            "TOP — e'lonni ko'rinarliroq qiladigan raqamli xizmat; sotilishini kafolatlamaydi. "
            "To'lov masalalari: /paysupport.\n\n"
            "<b>9.</b> Botdan foydalanish — ushbu qoidalarga rozilik. Qoidalar yangilanishi mumkin."
        ),
        "safety": (
            "🛡 <b>Xavfsiz savdo bo'yicha maslahatlar</b>\n\n"
            "✅ Sotuvchini 🛡 tekshiring: qora ro'yxat, shikoyatlar, savdolar soni, ✅ belgisi.\n"
            "✅ Videoqo'ng'iroq yoki ekran yozuvida akkauntni ko'rsatishini so'rang.\n"
            "✅ Akkauntga kirgach darhol pochta, telefon, KONAMI ID/Google bog'lanishni o'zingizga o'tkazing.\n"
            "✅ Kattaroq summada bosqichma-bosqich to'lang.\n"
            "✅ Yozishmalar va to'lov cheklarini saqlang.\n\n"
            "❌ Oldindan to'liq pul o'tkazmang.\n❌ «Shoshiling, boshqa xaridor bor» bosimiga uchmang.\n"
            "❌ Begona havolalar orqali «tasdiqlash» qilmang.\n❌ Hech kimga SMS-kod bermang.\n\n"
            "⚠️ Eslatma: biz garant emasmiz — xavfsizlik sizning ehtiyotkorligingizga bog'liq."
        ),
        "commands": (
            "⌨️ <b>Buyruqlar</b>\n\n"
            "/menu — 🏠 Dashboard\n/search <i>so'z</i> — 🔎 qidiruv (masalan: <code>/search messi 3200</code>)\n"
            "/catalog — 🛒 akkauntlar katalogi\n/topup — 🪙 Coin / UC xizmatlari\n/sell — ➕ e'lon berish\n"
            "/pro — 💎 PRO sotuvchi tarifi\n/my — 📂 mening e'lonlarim\n/fav — ❤️ saralanganlar\n/alerts — 🔔 obunalarim\n"
            "/check <i>@username</i> — 🛡 sotuvchini tekshirish\n/rules — 📜 qoidalar\n/safety — 🛡 xavfsizlik\n"
            "/guide — 📖 qo'llanma\n/lang — 🌐 til\n/help — ℹ️ yordam\n/paysupport — 💬 to'lov bo'yicha yordam\n"
            "/l<i>123</i> — e'lonni raqami bo'yicha ochish\n\n"
            "💡 Istalgan chatda: <code>@{bot} messi</code> — e'lonni do'stingizga ulashing."
        ),
        "menu": "Asosiy menyu 👇",
        "btn_dash": "🏠 Dashboard",
        "btn_search": "🔎 Qidiruv",
        "btn_buy": "🛒 Akkauntlar",
        "btn_sell": "➕ E'lon berish",
        "btn_topup": "🪙 Coin / UC",
        "btn_webapp": "📱 Vitrina",
        "choose_type": "Qanday e'lon berasiz?",
        "type_account": "👤 Akkaunt sotish",
        "type_topup": "🪙 Coin / UC xizmati",
        "topup_intro": "🪙 <b>Coin / UC xizmatlari</b>\nTasdiqlangan sotuvchilar e'lonlari. Biz pulga aralashmaymiz — "
                       "faqat ✅ belgili va otzivi bor sotuvchilarni tanlang.\n\n⚠️ Parolingizni hech kimga bermang: "
                       "«ID orqali» usuli eng xavfsiz.",
        "ask_price_topup": "💵 Eng arzon paket narxi (so'mda, masalan: 15000):",
        "from_price": "dan boshlab",
        "login_warn": "⚠️ Bu usulda akkaunt login/paroli so'raladi — o'yin qoidalariga zid, bloklanish xavfi bor!",
        "btn_my": "📂 Mening e'lonlarim",
        "btn_fav": "❤️ Saralanganlar",
        "btn_check": "🛡 Sotuvchini tekshirish",
        "btn_lang": "🌐 Til",
        "btn_help": "ℹ️ Yordam",
        "btn_admin": "🛠 Admin panel",
        "btn_back": "🔙 Orqaga",
        "btn_cancel": "❌ Bekor qilish",
        "btn_skip": "⏭ O'tkazib yuborish",
        "btn_done": "✅ Tayyor",
        "btn_yes": "✅ Ha",
        "btn_no": "❌ Yo'q",
        "cancelled": "❌ Bekor qilindi.",
        "help": (
            "ℹ️ <b>Yordam</b>\n\n"
            "🏠 /menu — Dashboard: o'yinlar, qidiruv, profil, qoidalar.\n"
            "📖 /guide — qisqa qo'llanma.\n⌨️ /commands — barcha buyruqlar.\n\n"
            "🚀 <b>TOP e'lon</b> — e'loningiz ro'yxat boshida turadi va {channel} kanalida qayta chiqadi "
            "(Telegram Stars ⭐️).\n\n"
            "⚠️ Biz garant emasmiz va to'lovlar uchun javobgar emasmiz — /rules, /safety.\n"
            "💬 To'lov bo'yicha: /paysupport"
        ),
        "paysupport": "💬 To'lov bo'yicha savol bo'lsa, adminga yozing: {support}\n"
                      "To'lov ID va e'lon raqamini ko'rsating. Asosli holatda Stars qaytariladi.\n\n"
                      "ℹ️ Bu faqat TOP xizmati (Telegram Stars) uchun. Akkaunt oldi-sotdisidagi to'lovlar "
                      "uchun javobgar emasmiz.",
        "lang_set": "✅ Til o'zgartirildi.",
        # ---------- Dashboard ----------
        "dash_home": (
            "🏠 <b>Gamebozor · Dashboard</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🟢 Faol e'lonlar: <b>{active}</b>   🆕 24 soatda: <b>{new24}</b>\n"
            "✅ Sotilgan: <b>{sold}</b>   👥 Foydalanuvchilar: <b>{users}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 Siz: {my_active} ta faol e'lon · ❤️ {favs} · 🔔 {alerts}\n\n"
            "Bo'limni tanlang 👇"
        ),
        "dash_games": "🎮 <b>O'yinlar bo'limlari</b>\n\nHar bir o'yin — alohida bozor: o'z filtrlari va ko'rsatkichlari bilan.",
        "dash_game": (
            "{emoji} <b>{name}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🟢 Sotuvda: <b>{count}</b>   🆕 24 soatda: <b>{new24}</b>   ✅ Sotilgan: <b>{sold}</b>\n"
            "💵 Narxlar: <b>{min}</b> — <b>{max}</b> so'm\n"
            "📊 O'rtacha: <b>{avg}</b> so'm{best}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Ko'rish usulini tanlang 👇"
        ),
        "dash_game_best": "\n💪 Eng yuqori ko'rsatkich: <b>{best}</b>",
        "dash_game_empty": "{emoji} <b>{name}</b>\n\n😔 Hozircha sotuvda e'lon yo'q.\nBirinchi bo'lib ➕ e'lon bering!",
        "soon": "🔜 {name} — tez kunda! Shablon tayyor, bo'lim yaqinda ochiladi.",
        "dash_profile": (
            "👤 <b>Profil</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            "🆔 <code>{id}</code>  {username}\n{badge}{rating}\n"
            "📂 E'lonlar: 🟢 {active} · ⏳ {pending} · ✅ {sold}\n"
            "👁 Jami ko'rishlar: <b>{views}</b>\n❤️ Saralangan: {favs}   🔔 Obunalar: {alerts}\n"
            "📅 Botda: {since} dan\n━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 Do'stlarni taklif qiling:\n<code>{ref}</code>"
        ),
        "badge_verified": "✅ Tasdiqlangan sotuvchi",
        "badge_none": "▫️ Oddiy foydalanuvchi",
        "dash_info": "ℹ️ <b>Ma'lumot markazi</b>\n\nQoidalar, xavfsizlik, qo'llanma va buyruqlar — hammasi shu yerda.",
        "d_games": "🎮 O'yinlar",
        "d_search": "🔎 Qidiruv",
        "d_topup": "🪙 Coin / UC",
        "d_sell": "➕ E'lon berish",
        "d_my": "📂 E'lonlarim",
        "d_fav": "❤️ Saralangan",
        "d_alerts": "🔔 Obunalar",
        "d_profile": "👤 Profil",
        "d_check": "🛡 Tekshirish",
        "d_info": "ℹ️ Qoidalar va yordam",
        "d_safety": "🛡 Xavfsizlik",
        "d_commands": "⌨️ Buyruqlar",
        "d_home": "🏠 Bosh sahifa",
        "d_refresh": "🔄 Yangilash",
        "d_browse": "🛒 Barchasini ko'rish",
        "d_filter": "🎛 Filtrlab izlash",
        "d_cheap": "💸 Eng arzonlari",
        "d_strong": "💪 Eng kuchlilari",
        "d_newest": "🆕 Eng yangilari",
        "d_webapp": "📱 Vitrina (Mini App)",
        "d_lang": "🌐 Til",
        # ---------- Qidiruv ----------
        "search_title": "🔎 <b>Qidiruv</b>",
        "search_section": "Bo'lim",
        "search_any_game": "barcha o'yinlar",
        "search_no_filters": "Filtrlar tanlanmagan — barcha e'lonlar ko'rsatiladi.",
        "search_found": "📊 Topildi: <b>{n}</b> ta e'lon",
        "search_hint": "Filtrni tanlang yoki shunchaki so'z yozing (masalan: <i>messi 3200</i>).",
        "s_game": "🎮 O'yin",
        "s_price": "💵 Narx",
        "s_text": "🔤 Matn",
        "s_verified": "✅ Faqat tasdiqlangan",
        "s_verified_plain": "Faqat tasdiqlangan sotuvchilar",
        "s_filters": "🎛 Filtrlar",
        "s_sort": "↕️ Saralash",
        "s_reset": "♻️ Tozalash",
        "s_show": "🔎 Ko'rsatish ({n})",
        "s_subscribe": "🔔 Obuna bo'lish",
        "s_any": "Farqi yo'q",
        "s_clear_one": "🗑 Filtrni olib tashlash",
        "sort_top": "🔥 TOP va yangilari",
        "sort_new": "🆕 Eng yangi",
        "sort_cheap": "💸 Arzonroq",
        "sort_exp": "💎 Qimmatroq",
        "sort_strong": "💪 Eng kuchli",
        "ask_price_range": (
            "💵 Narx oralig'ini tanlang yoki yozing:\n"
            "<code>500000-2000000</code>, <code>500k-2mln</code>, <code>1mln gacha</code>, <code>3mln</code> (dan yuqori)"
        ),
        "bad_range": "❗️ Tushunmadim. Masalan: <code>500k-2mln</code> yoki <code>1mln gacha</code>",
        "ask_min": "{icon} <b>{label}</b> — kamida qancha?\nTugmani tanlang yoki raqam yozing:",
        "ask_text_field": "{icon} <b>{label}</b>\nQidiriladigan so'zni yozing (masalan: <i>{example}</i>):",
        "ask_query": "🔤 Qidiruv so'zini yozing (o'yinchi, pack, sarlavha, izoh, #raqam):",
        "ask_choice": "{icon} <b>{label}</b> — tanlang:",
        "search_empty": "😔 Bu filtrlar bo'yicha e'lon topilmadi.\n\n💡 Filtrlarni yumshating yoki 🔔 obuna bo'ling — mos e'lon chiqsa darhol xabar beramiz.",
        "alert_saved": "🔔 Obuna saqlandi! Mos yangi e'lon chiqsa xabar beraman.",
        "alert_limit": "⚠️ Obunalar limiti: {n} ta. /alerts orqali eskisini o'chiring.",
        "alert_dup": "Bu qidiruvga allaqachon obuna bo'lgansiz.",
        "alerts_title": "🔔 <b>Obunalarim</b>\n\nMos yangi e'lon chiqsa xabar olasiz. O'chirish uchun bosing:",
        "alerts_empty": "🔔 Obunalar yo'q.\n\n🔎 Qidiruvda filtrlarni tanlab «🔔 Obuna bo'lish» ni bosing.",
        "alert_deleted": "🗑 Obuna o'chirildi",
        "alert_hit": "🔔 <b>Obunangizga mos yangi e'lon!</b>\n{summary}",
        # catalog
        "choose_game": "🎮 O'yinni tanlang:",
        "choose_price": "💵 Narx oralig'ini tanlang:",
        "price_all": "Hammasi",
        "empty": "😔 Hozircha bu bo'limda e'lon yo'q. Keyinroq qayta kiring yoki o'zingiz ➕ e'lon bering!",
        "listing_not_found": "E'lon topilmadi yoki o'chirilgan.",
        "contact_info": "📞 Sotuvchi bilan bog'lanish: {contact}\n\n"
                        "⚠️ Eslatma: biz garant emasmiz va to'lovlar uchun javobgar emasmiz.\n"
                        "Oldindan to'liq pul o'tkazmang! Avval akkauntni tekshiring — /safety",
        "seller_notified": "👀 E'loningiz #{id} bilan qiziqishdi: {who}",
        "fav_added": "❤️ Saralanganlarga qo'shildi",
        "fav_removed": "💔 Saralanganlardan olindi",
        "fav_empty": "Saralanganlar ro'yxati bo'sh.",
        "fav_title": "❤️ Saralangan e'lonlar:",
        "more_photos": "🖼 Yana {n} ta rasm → /l{id}",
        "btn_contact": "📞 Bog'lanish",
        "btn_share": "📤 Ulashish",
        # sell
        "limit_reached": "⚠️ Sizda {n} ta faol/moderatsiyadagi e'lon bor (tekin limit). "
                         "Birortasini 'Sotildi' qiling yoki o'chiring.",
        "need_username": "ℹ️ Telegram sozlamalarida @username o'rnating — xaridorlar siz bilan oson bog'lanadi.",
        "ask_title": "✏️ E'lon uchun qisqa sarlavha yozing (masalan: <i>TS 3250, 18 Epic, Messi</i>):",
        "ask_field": "{icon} {label}:",
        "bad_int": "❗️ Faqat raqam yuboring.",
        "ask_price": "💵 Narxni so'mda yozing (masalan: 1500000):",
        "bad_price": "❗️ Narx noto'g'ri. 1 000 dan 1 000 000 000 so'mgacha raqam yozing.",
        "ask_negotiable": "🤝 Narxda kelishuv bormi?",
        "ask_desc": "📝 Qo'shimcha izoh (ixtiyoriy, 500 belgigacha):",
        "ask_photos": "🖼 Akkaunt skrinshotlarini yuboring (1–{n} ta). Jamoa, o'yinchilar, coin ko'rinsin.\n"
                      "Tugatgach «✅ Tayyor» ni bosing.",
        "photo_added": "🖼 Qabul qilindi: {n}/{max}. Yana yuboring yoki «✅ Tayyor».",
        "photo_limit": "❗️ Maksimum {n} ta rasm.",
        "need_photo": "❗️ Kamida 1 ta skrinshot yuboring.",
        "ask_contact": "📞 Xaridor qanday bog'lansin? «{username}» ni tanlang yoki boshqa kontakt yozing:",
        "preview": "👇 E'loningiz shunday ko'rinadi. Yuboramizmi?\n\n"
                   "ℹ️ Yuborish orqali siz /rules ga rozilik bildirasiz: akkaunt sizniki, ma'lumotlar haqiqiy.",
        "btn_submit": "✅ Moderatsiyaga yuborish",
        "btn_restart": "🔄 Qaytadan",
        "submitted": "✅ E'lon #{id} moderatsiyaga yuborildi. Tasdiqlangach xabar beramiz (odatda 1–3 soat).",
        "published_admin": "✅ E'lon #{id} darhol chop etildi (admin).",
        # moderation
        "approved": "🎉 E'loningiz #{id} tasdiqlandi va kanalda chiqdi!\n\n🚀 Tezroq sotish uchun TOP qiling: 📂 Mening e'lonlarim",
        "rejected": "❌ E'loningiz #{id} rad etildi.\nSabab: {reason}\n\nTo'g'rilab, qaytadan yuboring.",
        # my listings
        "my_empty": "Sizda hali e'lon yo'q. ➕ E'lon berish tugmasini bosing.",
        "my_title": "📂 Sizning e'lonlaringiz:",
        "btn_top": "🚀 TOP qilish",
        "btn_sold": "✅ Sotildi",
        "btn_delete": "🗑 O'chirish",
        "marked_sold": "✅ #{id} sotildi deb belgilandi. Tabriklaymiz! 🎉",
        "deleted": "🗑 #{id} o'chirildi.",
        "top_choose": "🚀 TOP e'lon:\n• ro'yxatda eng yuqorida turadi\n• kanalda 🔥 belgisi bilan qayta chiqadi\n\n"
                      "ℹ️ TOP ko'rinishni oshiradi, sotilishini kafolatlamaydi.\n\nMuddatni tanlang:",
        "top_3d": "3 kun — {n} ⭐️",
        "top_7d": "7 kun — {n} ⭐️",
        "top_only_active": "TOP faqat faol e'lonlar uchun.",
        "top_done": "🔥 E'lon #{id} {until} gacha TOP da!",
        # report / check
        "ask_report": "🚩 Shikoyat sababini yozing (firibgarlik, yolg'on ma'lumot va h.k.):",
        "report_sent": "✅ Shikoyat yuborildi. Rahmat!",
        "ask_check": "🛡 Sotuvchining @username ini yozing:",
        "check_bad": "⛔️ <b>{t}</b> — FIRIBGARLAR RO'YXATIDA!\nIzoh: {note}\n\nBu odam bilan savdo qilmang!",
        "check_ok": "✅ <b>{t}</b> qora ro'yxatda yo'q.\nShikoyatlar: {reports}\n{extra}\n\n⚠️ Baribir ehtiyot bo'ling — biz garant emasmiz.",
        "check_member": "Botda: {listings} ta e'lon, {sold} ta sotilgan{verified}",
        "verified": ", ✅ tasdiqlangan sotuvchi",
        "banned": "⛔️ Siz bloklangansiz.",
        # 💎 PRO tarif
        "d_pro": "💎 PRO tarif",
        "pro_screen": (
            "💎 <b>PRO sotuvchi</b>\n━━━━━━━━━━━━━━━━━━━━\n{status}\n━━━━━━━━━━━━━━━━━━━━\n"
            "<b>PRO imkoniyatlari:</b>\n"
            "📂 <b>{limit}</b> tagacha faol e'lon (tekin tarifda: {free})\n"
            "🔄 E'lonlaringiz har <b>{hours} soatda</b> avtomatik ro'yxat boshiga ko'tariladi\n"
            "🎁 Har bir xaridga <b>1 ta bepul TOP</b> (3 kun, kanalda 🔥 bilan qayta chiqadi)\n"
            "💎 E'lonlarda va kanal bannerida «PRO» belgisi — xaridor ishonchi oshadi\n"
            "⚡️ Moderatsiyada ustuvorlik\n━━━━━━━━━━━━━━━━━━━━\n"
            "<b>Narxlar (Telegram Stars):</b>\n• 30 kun — {p30} ⭐️\n• 90 kun — {p90} ⭐️ (tejamkor)\n\n"
            "ℹ️ PRO — e'lonlarni ko'rinarliroq qiladigan raqamli xizmat, sotilishini kafolatlamaydi. "
            "Biz garant emasmiz. To'lov bo'yicha: /paysupport"
        ),
        "pro_status_on": "✅ Faol: <b>{until}</b> gacha · 🎁 bepul TOP: {credits}",
        "pro_status_off": "▫️ Hozir: tekin tarif",
        "pro_buy_30": "💎 30 kun — {n} ⭐️",
        "pro_buy_90": "💎 90 kun — {n} ⭐️",
        "pro_extend_note": "Muddat qo'shiladi (uzaytiriladi).",
        "pro_done": "🎉 <b>PRO faollashtirildi</b> — {until} gacha!\n🎁 Bepul TOP: {credits} ta → 📂 Mening e'lonlarim → 🚀 TOP qilish",
        "pro_badge": "💎 PRO sotuvchi",
        "pro_reminder": "⏳ PRO tarifingiz <b>{until}</b> da tugaydi. Uzaytirish: /pro",
        "pro_expired": "▫️ PRO muddati tugadi. E'lonlaringiz saqlandi, lekin yangi e'lonlar limiti — {free} ta. Qayta yoqish: /pro",
        "pro_hint": "\n\n💎 PRO tarifda {n} tagacha e'lon: /pro",
        "top_free": "🎁 Bepul TOP — 3 kun (PRO)",
        "top_free_done": "🔥 Bepul TOP ishlatildi: #{id} {until} gacha TOP da! Qolgan bepul TOP: {left}",
        "top_free_none": "Bepul TOP qolmagan.",
        # narx o'zgartirish / narx tushishi
        "btn_price_edit": "✏️ Narxni o'zgartirish",
        "ask_new_price": "💵 #{id} uchun yangi narxni yozing (hozirgi: {price} so'm):",
        "price_updated": "✅ #{id} narxi yangilandi: {old} → <b>{new}</b> so'm",
        "price_same": "Narx o'zgarmadi.",
        "price_drop_hit": "📉 <b>Narx tushdi!</b> Saralangan e'loningiz:\n{summary}\n<s>{old}</s> → <b>{new}</b> so'm",
        # reyting / sharhlar
        "btn_rate": "⭐️ Sotuvchini baholash",
        "rate_ask": "⭐️ <b>#{id}</b> e'loni bo'yicha sotuvchini ({seller}) baholang.\nSavdo qanday o'tdi?",
        "rate_ask_sold": "🤝 Siz qiziqqan <b>#{id}</b> e'lon sotildi.\nShu sotuvchidan ({seller}) xarid qildingizmi? "
                         "Baholang — bu boshqa xaridorlarni firibgarlardan himoya qiladi:",
        "btn_not_bought": "🙅 Men sotib olmadim",
        "rate_saved": "✅ Bahoyingiz qabul qilindi: {stars}\n📝 Qisqa izoh yozing (300 belgigacha) yoki o'tkazib yuboring:",
        "rate_thanks": "🙏 Rahmat! Sharhingiz sotuvchi profiliga qo'shildi.",
        "rate_denied": "Baho faqat shu e'lon bo'yicha «📞 Bog'lanish» ni bosgan xaridorlar uchun.",
        "rate_dup": "Bu e'lon bo'yicha allaqachon baho bergansiz.",
        "rate_self": "O'zingizga baho bera olmaysiz 🙂",
        "new_review": "⭐️ Sizga yangi baho: {stars} — e'lon #{id}\n{text}",
        "rating_line": "\n⭐️ Reyting: <b>{avg}</b> / 5 ({n} ta sharh)",
        "reviews_title": "\n\n💬 So'nggi sharhlar:",
        "no_reviews": "\n⭐️ Hali sharh yo'q",
        "dismissed": "👌 Tushunarli.",
        "unknown": "🤔 Tushunmadim. 🏠 /menu — Dashboard, 🔎 /search — qidiruv, ⌨️ /commands — buyruqlar.",
    },
    "ru": {
        "choose_lang": "🌐 Tilni tanlang / Выберите язык:",
        "welcome": (
            "👋 Здравствуйте, <b>{name}</b>!\n\n"
            "🎮 <b>Gamebozor</b> — площадка объявлений игровых аккаунтов и услуг.\n\n"
            "Здесь вы:\n"
            "🔎 ищете аккаунты по <b>общему показателю, игрокам, пакам и цене</b>;\n"
            "➕ выставляете свой аккаунт за пару минут;\n"
            "🛡 проверяете продавца по списку мошенников;\n"
            "🔔 получаете уведомление о подходящих объявлениях.\n\n"
            "⚠️ <b>Важно:</b> Gamebozor — только доска объявлений. Мы <b>не гарант</b> и не несём "
            "ответственности за платежи и сделки.\n\n"
            "Перед началом ознакомьтесь с коротким руководством и правилами 👇"
        ),
        "btn_guide": "📖 Руководство",
        "btn_rules": "📜 Правила",
        "btn_accept": "✅ Я прочитал(а) правила и согласен(на)",
        "btn_to_dash": "🏠 Перейти в Dashboard",
        "btn_next": "Далее ▶️",
        "btn_prev": "◀️ Назад",
        "rules_accepted": "🤝 Спасибо! Согласие с правилами принято. Теперь вам доступны все функции.",
        "need_rules": "📜 Для этого действия сначала ознакомьтесь с правилами и примите их.",
        "guide": [
            "📖 <b>Руководство 1/5 — Dashboard</b>\n\n"
            "🏠 <b>Dashboard</b> — панель управления ботом. Всё в одном сообщении:\n"
            "• разделы игр и показатели рынка\n• поиск и фильтры\n• ваш профиль и объявления\n"
            "• правила и помощь\n\nОткрывается кнопкой «🏠 Dashboard» внизу или командой /menu.",
            "📖 <b>Руководство 2/5 — Поиск</b>\n\n"
            "🔎 В поиске фильтры комбинируются:\n"
            "💵 диапазон цен (например <code>500k-2mln</code>)\n"
            "💪 общий показатель (Team Strength) — не меньше N\n"
            "🟣 кол-во Epic / 🟠 Big Time\n⭐️ имя игрока (Messi, Mbappe...)\n📦 название пака (POTW, Highlight...)\n"
            "📱 платформа, 🔗 привязка, 🏆 дивизион\n\n"
            "Быстрый поиск: <code>/search messi 3200</code> или в любом чате <code>@{bot} messi</code>.",
            "📖 <b>Руководство 3/5 — Покупка</b>\n\n"
            "1️⃣ Откройте объявление, посмотрите скриншоты.\n2️⃣ «📞 Связаться» — появится контакт продавца.\n"
            "3️⃣ Проверьте продавца 🛡 (чёрный список, жалобы, история).\n"
            "4️⃣ Не платите всю сумму, пока <b>не перепривязали</b> почту/телефон/привязку на себя.\n\n"
            "❤️ добавляйте в избранное, 🔔 подписывайтесь на поиск — сообщим о новых подходящих объявлениях.",
            "📖 <b>Руководство 4/5 — Продажа</b>\n\n"
            "1️⃣ «➕ Подать объявление» → игра → форма (показатели, игроки, паки).\n"
            "2️⃣ Цена, описание и 1–10 скриншотов.\n3️⃣ Админ проверит (обычно 1–3 часа) → публикация в боте и канале {channel}.\n"
            "4️⃣ После продажи нажмите «✅ Продано».\n\n"
            "🚀 <b>TOP</b> — объявление первое в списке и повторно публикуется в канале с 🔥 (Telegram Stars ⭐️).",
            "📖 <b>Руководство 5/5 — Безопасность</b>\n\n"
            "🚫 Бот и админы никогда не просят логин, пароль, SMS-код.\n"
            "🚫 Если «гарант/админ Gamebozor» просит деньги — это <b>мошенник</b>. Мы не принимаем деньги.\n"
            "🚫 Не платите всю сумму заранее, сначала проверьте аккаунт.\n"
            "🚩 Сообщайте о подозрительных объявлениях — админы проверят.\n\n"
            "⌨️ Все команды: меню <b>/</b> внизу или /commands.",
        ],
        "rules": (
            "📜 <b>Правила Gamebozor</b>\n\n"
            "<b>1. Статус платформы</b>\n"
            "Gamebozor — только доска объявлений. Мы не продавец, не покупатель и не посредник.\n\n"
            "<b>2. ❗️ Мы НЕ гарант</b>\n"
            "• Мы <b>не несём никакой ответственности</b> за сделки купли-продажи аккаунтов, платежи и их последствия.\n"
            "• Деньги и аккаунт передаются напрямую между продавцом и покупателем — все риски на сторонах сделки.\n"
            "• Мы не возмещаем потери при мошенничестве, обмане или возврате аккаунта (recovery).\n"
            "• Бот никогда не принимает деньги (кроме услуги TOP — через Telegram Stars). "
            "Кто просит деньги от имени «гаранта/админа Gamebozor» — мошенник.\n\n"
            "<b>3. Личные данные</b>\n"
            "Не отправляйте боту и никому логины, пароли, SMS-коды, данные карт — мы их не запрашиваем.\n\n"
            "<b>4. Правила игр</b>\n"
            "Продажа аккаунтов может нарушать правила издателя (Konami, Krafton и др.) и привести к блокировке. "
            "Этот риск пользователь берёт на себя.\n\n"
            "<b>5. Требования к объявлениям</b>\n"
            "• Продавайте только свой аккаунт.\n• Реальные скриншоты и данные.\n"
            "• Один аккаунт — одно объявление; дубликаты запрещены.\n\n"
            "<b>6. Запрещено</b>\n"
            "Украденные/взломанные аккаунты, ложные данные, мошенничество, оскорбления, спам и реклама "
            "других площадок.\n\n"
            "<b>7. Меры</b>\n"
            "При нарушении: удаление объявления, блокировка и внесение в список мошенников. "
            "Админы вправе отклонить или удалить объявление.\n\n"
            "<b>8. Услуга TOP</b>\n"
            "TOP — цифровая услуга, повышающая видимость; продажу не гарантирует. Вопросы по оплате: /paysupport.\n\n"
            "<b>9.</b> Использование бота означает согласие с правилами. Правила могут обновляться."
        ),
        "safety": (
            "🛡 <b>Советы по безопасной сделке</b>\n\n"
            "✅ Проверьте продавца 🛡: чёрный список, жалобы, кол-во сделок, значок ✅.\n"
            "✅ Попросите показать аккаунт по видеосвязи или записью экрана.\n"
            "✅ Сразу после входа перепривяжите почту, телефон, KONAMI ID/Google на себя.\n"
            "✅ Крупные суммы — поэтапно.\n✅ Сохраняйте переписку и чеки.\n\n"
            "❌ Не переводите всю сумму заранее.\n❌ Не поддавайтесь давлению «быстрее, есть другой покупатель».\n"
            "❌ Не «подтверждайте» ничего по чужим ссылкам.\n❌ Никому не сообщайте SMS-коды.\n\n"
            "⚠️ Напоминаем: мы не гарант — безопасность зависит от вашей осторожности."
        ),
        "commands": (
            "⌨️ <b>Команды</b>\n\n"
            "/menu — 🏠 Dashboard\n/search <i>слово</i> — 🔎 поиск (например: <code>/search messi 3200</code>)\n"
            "/catalog — 🛒 каталог аккаунтов\n/topup — 🪙 услуги Coin / UC\n/sell — ➕ подать объявление\n"
            "/pro — 💎 тариф PRO\n/my — 📂 мои объявления\n/fav — ❤️ избранное\n/alerts — 🔔 мои подписки\n"
            "/check <i>@username</i> — 🛡 проверить продавца\n/rules — 📜 правила\n/safety — 🛡 безопасность\n"
            "/guide — 📖 руководство\n/lang — 🌐 язык\n/help — ℹ️ помощь\n/paysupport — 💬 поддержка по оплатам\n"
            "/l<i>123</i> — открыть объявление по номеру\n\n"
            "💡 В любом чате: <code>@{bot} messi</code> — поделитесь объявлением с другом."
        ),
        "menu": "Главное меню 👇",
        "btn_dash": "🏠 Dashboard",
        "btn_search": "🔎 Поиск",
        "btn_buy": "🛒 Аккаунты",
        "btn_sell": "➕ Подать объявление",
        "btn_topup": "🪙 Coin / UC",
        "btn_webapp": "📱 Витрина",
        "choose_type": "Какое объявление подаёте?",
        "type_account": "👤 Продать аккаунт",
        "type_topup": "🪙 Услуга Coin / UC",
        "topup_intro": "🪙 <b>Услуги Coin / UC</b>\nОбъявления продавцов. Мы не участвуем в расчётах — "
                       "выбирайте продавцов с ✅ и отзывами.\n\n⚠️ Никому не давайте пароль: способ «По ID» самый безопасный.",
        "ask_price_topup": "💵 Цена самого дешёвого пакета (в сумах, например: 15000):",
        "from_price": "от",
        "login_warn": "⚠️ Здесь запрашивают логин/пароль аккаунта — это нарушает правила игры, есть риск блокировки!",
        "btn_my": "📂 Мои объявления",
        "btn_fav": "❤️ Избранное",
        "btn_check": "🛡 Проверить продавца",
        "btn_lang": "🌐 Язык",
        "btn_help": "ℹ️ Помощь",
        "btn_admin": "🛠 Админ панель",
        "btn_back": "🔙 Назад",
        "btn_cancel": "❌ Отмена",
        "btn_skip": "⏭ Пропустить",
        "btn_done": "✅ Готово",
        "btn_yes": "✅ Да",
        "btn_no": "❌ Нет",
        "cancelled": "❌ Отменено.",
        "help": (
            "ℹ️ <b>Помощь</b>\n\n"
            "🏠 /menu — Dashboard: игры, поиск, профиль, правила.\n"
            "📖 /guide — краткое руководство.\n⌨️ /commands — все команды.\n\n"
            "🚀 <b>TOP</b> — объявление первое в списке и повторно публикуется в канале {channel} "
            "(Telegram Stars ⭐️).\n\n"
            "⚠️ Мы не гарант и не отвечаем за платежи — /rules, /safety.\n"
            "💬 По оплате: /paysupport"
        ),
        "paysupport": "💬 Вопросы по оплате — пишите админу: {support}\nУкажите ID платежа и номер объявления. "
                      "В обоснованных случаях Stars возвращаются.\n\n"
                      "ℹ️ Только для услуги TOP (Telegram Stars). За платежи в сделках с аккаунтами мы не отвечаем.",
        "lang_set": "✅ Язык изменён.",
        "dash_home": (
            "🏠 <b>Gamebozor · Dashboard</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🟢 Активных: <b>{active}</b>   🆕 За 24 ч: <b>{new24}</b>\n"
            "✅ Продано: <b>{sold}</b>   👥 Пользователей: <b>{users}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "👤 Вы: {my_active} активн. · ❤️ {favs} · 🔔 {alerts}\n\n"
            "Выберите раздел 👇"
        ),
        "dash_games": "🎮 <b>Разделы игр</b>\n\nКаждая игра — отдельный рынок со своими фильтрами и показателями.",
        "dash_game": (
            "{emoji} <b>{name}</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "🟢 В продаже: <b>{count}</b>   🆕 За 24 ч: <b>{new24}</b>   ✅ Продано: <b>{sold}</b>\n"
            "💵 Цены: <b>{min}</b> — <b>{max}</b> сум\n"
            "📊 Средняя: <b>{avg}</b> сум{best}\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "Как смотреть? 👇"
        ),
        "dash_game_best": "\n💪 Лучший показатель: <b>{best}</b>",
        "dash_game_empty": "{emoji} <b>{name}</b>\n\n😔 Пока нет объявлений.\nБудьте первым — ➕ подайте объявление!",
        "soon": "🔜 {name} — скоро! Шаблон готов, раздел скоро откроется.",
        "dash_profile": (
            "👤 <b>Профиль</b>\n━━━━━━━━━━━━━━━━━━━━\n"
            "🆔 <code>{id}</code>  {username}\n{badge}{rating}\n"
            "📂 Объявления: 🟢 {active} · ⏳ {pending} · ✅ {sold}\n"
            "👁 Всего просмотров: <b>{views}</b>\n❤️ Избранное: {favs}   🔔 Подписки: {alerts}\n"
            "📅 В боте с {since}\n━━━━━━━━━━━━━━━━━━━━\n"
            "🎁 Приглашайте друзей:\n<code>{ref}</code>"
        ),
        "badge_verified": "✅ Проверенный продавец",
        "badge_none": "▫️ Обычный пользователь",
        "dash_info": "ℹ️ <b>Информационный центр</b>\n\nПравила, безопасность, руководство и команды — всё здесь.",
        "d_games": "🎮 Игры",
        "d_search": "🔎 Поиск",
        "d_topup": "🪙 Coin / UC",
        "d_sell": "➕ Подать",
        "d_my": "📂 Мои",
        "d_fav": "❤️ Избранное",
        "d_alerts": "🔔 Подписки",
        "d_profile": "👤 Профиль",
        "d_check": "🛡 Проверка",
        "d_info": "ℹ️ Правила и помощь",
        "d_safety": "🛡 Безопасность",
        "d_commands": "⌨️ Команды",
        "d_home": "🏠 Главная",
        "d_refresh": "🔄 Обновить",
        "d_browse": "🛒 Смотреть все",
        "d_filter": "🎛 Поиск с фильтрами",
        "d_cheap": "💸 Самые дешёвые",
        "d_strong": "💪 Самые сильные",
        "d_newest": "🆕 Самые новые",
        "d_webapp": "📱 Витрина (Mini App)",
        "d_lang": "🌐 Язык",
        "search_title": "🔎 <b>Поиск</b>",
        "search_section": "Раздел",
        "search_any_game": "все игры",
        "search_no_filters": "Фильтры не выбраны — показываются все объявления.",
        "search_found": "📊 Найдено: <b>{n}</b>",
        "search_hint": "Выберите фильтр или просто напишите слово (например: <i>messi 3200</i>).",
        "s_game": "🎮 Игра",
        "s_price": "💵 Цена",
        "s_text": "🔤 Текст",
        "s_verified": "✅ Только проверенные",
        "s_verified_plain": "Только проверенные продавцы",
        "s_filters": "🎛 Фильтры",
        "s_sort": "↕️ Сортировка",
        "s_reset": "♻️ Сбросить",
        "s_show": "🔎 Показать ({n})",
        "s_subscribe": "🔔 Подписаться",
        "s_any": "Не важно",
        "s_clear_one": "🗑 Убрать фильтр",
        "sort_top": "🔥 TOP и новые",
        "sort_new": "🆕 Новые",
        "sort_cheap": "💸 Дешевле",
        "sort_exp": "💎 Дороже",
        "sort_strong": "💪 Сильнее",
        "ask_price_range": (
            "💵 Выберите или напишите диапазон цен:\n"
            "<code>500000-2000000</code>, <code>500k-2mln</code>, <code>до 1mln</code>, <code>3mln</code> (от)"
        ),
        "bad_range": "❗️ Не понял. Например: <code>500k-2mln</code> или <code>до 1mln</code>",
        "ask_min": "{icon} <b>{label}</b> — не меньше?\nВыберите кнопку или напишите число:",
        "ask_text_field": "{icon} <b>{label}</b>\nНапишите, что искать (например: <i>{example}</i>):",
        "ask_query": "🔤 Напишите запрос (игрок, пак, заголовок, описание, #номер):",
        "ask_choice": "{icon} <b>{label}</b> — выберите:",
        "search_empty": "😔 По этим фильтрам ничего не найдено.\n\n💡 Ослабьте фильтры или 🔔 подпишитесь — сообщим, как только появится подходящее.",
        "alert_saved": "🔔 Подписка сохранена! Сообщу о новых подходящих объявлениях.",
        "alert_limit": "⚠️ Лимит подписок: {n}. Удалите старую через /alerts.",
        "alert_dup": "Вы уже подписаны на этот поиск.",
        "alerts_title": "🔔 <b>Мои подписки</b>\n\nПолучаете уведомления о новых подходящих объявлениях. Нажмите, чтобы удалить:",
        "alerts_empty": "🔔 Подписок нет.\n\n🔎 Выберите фильтры в поиске и нажмите «🔔 Подписаться».",
        "alert_deleted": "🗑 Подписка удалена",
        "alert_hit": "🔔 <b>Новое объявление по вашей подписке!</b>\n{summary}",
        "choose_game": "🎮 Выберите игру:",
        "choose_price": "💵 Выберите диапазон цен:",
        "price_all": "Все",
        "empty": "😔 Пока здесь нет объявлений. Загляните позже или ➕ подайте своё!",
        "listing_not_found": "Объявление не найдено или удалено.",
        "contact_info": "📞 Связь с продавцом: {contact}\n\n"
                        "⚠️ Напоминаем: мы не гарант и не отвечаем за платежи.\n"
                        "Не переводите всю сумму заранее! Сначала проверьте аккаунт — /safety",
        "seller_notified": "👀 Вашим объявлением #{id} заинтересовались: {who}",
        "fav_added": "❤️ Добавлено в избранное",
        "fav_removed": "💔 Удалено из избранного",
        "fav_empty": "Избранное пусто.",
        "fav_title": "❤️ Избранные объявления:",
        "more_photos": "🖼 Ещё {n} фото → /l{id}",
        "btn_contact": "📞 Связаться",
        "btn_share": "📤 Поделиться",
        "limit_reached": "⚠️ У вас {n} активных/на модерации объявлений (бесплатный лимит). "
                         "Отметьте одно как «Продано» или удалите.",
        "need_username": "ℹ️ Установите @username в настройках Telegram — покупателям будет проще связаться.",
        "ask_title": "✏️ Короткий заголовок объявления (например: <i>TS 3250, 18 Epic, Messi</i>):",
        "ask_field": "{icon} {label}:",
        "bad_int": "❗️ Отправьте только число.",
        "ask_price": "💵 Цена в сумах (например: 1500000):",
        "bad_price": "❗️ Неверная цена. Число от 1 000 до 1 000 000 000 сум.",
        "ask_negotiable": "🤝 Торг уместен?",
        "ask_desc": "📝 Дополнительное описание (необязательно, до 500 символов):",
        "ask_photos": "🖼 Отправьте скриншоты аккаунта (1–{n}). Команда, игроки, монеты.\nЗатем нажмите «✅ Готово».",
        "photo_added": "🖼 Принято: {n}/{max}. Отправьте ещё или «✅ Готово».",
        "photo_limit": "❗️ Максимум {n} фото.",
        "need_photo": "❗️ Нужен хотя бы 1 скриншот.",
        "ask_contact": "📞 Как с вами связаться? Выберите «{username}» или напишите другой контакт:",
        "preview": "👇 Так будет выглядеть объявление. Отправляем?\n\n"
                   "ℹ️ Отправляя, вы соглашаетесь с /rules: аккаунт ваш, данные достоверны.",
        "btn_submit": "✅ Отправить на модерацию",
        "btn_restart": "🔄 Заново",
        "submitted": "✅ Объявление #{id} отправлено на модерацию. Сообщим после проверки (обычно 1–3 часа).",
        "published_admin": "✅ Объявление #{id} опубликовано сразу (админ).",
        "approved": "🎉 Объявление #{id} одобрено и опубликовано в канале!\n\n🚀 Продайте быстрее с TOP: 📂 Мои объявления",
        "rejected": "❌ Объявление #{id} отклонено.\nПричина: {reason}\n\nИсправьте и отправьте снова.",
        "my_empty": "У вас ещё нет объявлений. Нажмите ➕ Подать объявление.",
        "my_title": "📂 Ваши объявления:",
        "btn_top": "🚀 Поднять в TOP",
        "btn_sold": "✅ Продано",
        "btn_delete": "🗑 Удалить",
        "marked_sold": "✅ #{id} отмечено как проданное. Поздравляем! 🎉",
        "deleted": "🗑 #{id} удалено.",
        "top_choose": "🚀 TOP объявление:\n• первое в списке\n• повторная публикация в канале с 🔥\n\n"
                      "ℹ️ TOP повышает видимость, но не гарантирует продажу.\n\nВыберите срок:",
        "top_3d": "3 дня — {n} ⭐️",
        "top_7d": "7 дней — {n} ⭐️",
        "top_only_active": "TOP доступен только для активных объявлений.",
        "top_done": "🔥 Объявление #{id} в TOP до {until}!",
        "ask_report": "🚩 Опишите причину жалобы (мошенничество, ложные данные и т.д.):",
        "report_sent": "✅ Жалоба отправлена. Спасибо!",
        "ask_check": "🛡 Введите @username продавца:",
        "check_bad": "⛔️ <b>{t}</b> — В ЧЁРНОМ СПИСКЕ МОШЕННИКОВ!\nПримечание: {note}\n\nНе совершайте сделок!",
        "check_ok": "✅ <b>{t}</b> нет в чёрном списке.\nЖалоб: {reports}\n{extra}\n\n⚠️ Всё равно будьте осторожны — мы не гарант.",
        "check_member": "В боте: {listings} объявл., продано {sold}{verified}",
        "verified": ", ✅ проверенный продавец",
        "banned": "⛔️ Вы заблокированы.",
        "d_pro": "💎 Тариф PRO",
        "pro_screen": (
            "💎 <b>PRO продавец</b>\n━━━━━━━━━━━━━━━━━━━━\n{status}\n━━━━━━━━━━━━━━━━━━━━\n"
            "<b>Возможности PRO:</b>\n"
            "📂 До <b>{limit}</b> активных объявлений (бесплатно: {free})\n"
            "🔄 Объявления автоматически поднимаются в начало списка каждые <b>{hours} ч</b>\n"
            "🎁 <b>1 бесплатный TOP</b> за каждую покупку (3 дня, повторная публикация в канале с 🔥)\n"
            "💎 Значок «PRO» в объявлениях и на баннере канала — больше доверия покупателей\n"
            "⚡️ Приоритет на модерации\n━━━━━━━━━━━━━━━━━━━━\n"
            "<b>Цены (Telegram Stars):</b>\n• 30 дней — {p30} ⭐️\n• 90 дней — {p90} ⭐️ (выгодно)\n\n"
            "ℹ️ PRO — цифровая услуга для повышения видимости, продажу не гарантирует. "
            "Мы не гарант. Вопросы по оплате: /paysupport"
        ),
        "pro_status_on": "✅ Активен до <b>{until}</b> · 🎁 бесплатных TOP: {credits}",
        "pro_status_off": "▫️ Сейчас: бесплатный тариф",
        "pro_buy_30": "💎 30 дней — {n} ⭐️",
        "pro_buy_90": "💎 90 дней — {n} ⭐️",
        "pro_extend_note": "Срок будет добавлен (продлён).",
        "pro_done": "🎉 <b>PRO активирован</b> — до {until}!\n🎁 Бесплатных TOP: {credits} → 📂 Мои объявления → 🚀 Поднять в TOP",
        "pro_badge": "💎 PRO продавец",
        "pro_reminder": "⏳ Ваш PRO заканчивается <b>{until}</b>. Продлить: /pro",
        "pro_expired": "▫️ Срок PRO истёк. Объявления сохранены, но лимит новых — {free}. Включить снова: /pro",
        "pro_hint": "\n\n💎 В тарифе PRO — до {n} объявлений: /pro",
        "top_free": "🎁 Бесплатный TOP — 3 дня (PRO)",
        "top_free_done": "🔥 Бесплатный TOP использован: #{id} в TOP до {until}! Осталось бесплатных TOP: {left}",
        "top_free_none": "Бесплатных TOP не осталось.",
        "btn_price_edit": "✏️ Изменить цену",
        "ask_new_price": "💵 Новая цена для #{id} (сейчас: {price} сум):",
        "price_updated": "✅ Цена #{id} обновлена: {old} → <b>{new}</b> сум",
        "price_same": "Цена не изменилась.",
        "price_drop_hit": "📉 <b>Цена снижена!</b> Объявление из избранного:\n{summary}\n<s>{old}</s> → <b>{new}</b> сум",
        "btn_rate": "⭐️ Оценить продавца",
        "rate_ask": "⭐️ Оцените продавца ({seller}) по объявлению <b>#{id}</b>.\nКак прошла сделка?",
        "rate_ask_sold": "🤝 Объявление <b>#{id}</b>, которым вы интересовались, продано.\nВы купили у этого продавца ({seller})? "
                         "Оцените — это защищает других покупателей от мошенников:",
        "btn_not_bought": "🙅 Я не покупал(а)",
        "rate_saved": "✅ Оценка принята: {stars}\n📝 Напишите короткий отзыв (до 300 символов) или пропустите:",
        "rate_thanks": "🙏 Спасибо! Отзыв добавлен в профиль продавца.",
        "rate_denied": "Оценивать могут только покупатели, нажавшие «📞 Связаться» в этом объявлении.",
        "rate_dup": "Вы уже оценили это объявление.",
        "rate_self": "Нельзя оценить самого себя 🙂",
        "new_review": "⭐️ Новая оценка: {stars} — объявление #{id}\n{text}",
        "rating_line": "\n⭐️ Рейтинг: <b>{avg}</b> / 5 ({n} отз.)",
        "reviews_title": "\n\n💬 Последние отзывы:",
        "no_reviews": "\n⭐️ Отзывов пока нет",
        "dismissed": "👌 Понятно.",
        "unknown": "🤔 Не понял. 🏠 /menu — Dashboard, 🔎 /search — поиск, ⌨️ /commands — команды.",
    },
}

# Narx oraliqlari (so'm): kod -> (min, max)
PRICE_RANGES: dict[str, tuple[int, int | None]] = {
    "all": (0, None),
    "p1": (0, 300_000),
    "p2": (300_000, 1_000_000),
    "p3": (1_000_000, 3_000_000),
    "p4": (3_000_000, None),
}
PRICE_LABELS = {"p1": "≤ 300 000", "p2": "300 000 – 1 mln", "p3": "1 – 3 mln", "p4": "3 mln +"}

REJECT_REASONS = {
    "photo": ("Skrinshotlar sifatsiz yoki yetarli emas", "Скриншоты плохого качества или их мало"),
    "price": ("Narx real emas", "Нереальная цена"),
    "info": ("Ma'lumotlar to'liq/to'g'ri emas", "Неполные или неверные данные"),
    "dup": ("Takroriy e'lon", "Дубликат объявления"),
    "rules": ("Qoidalarga zid", "Нарушение правил"),
}


def t(lang: str | None, key: str, **kw):
    lang = lang if lang in TEXTS else "uz"
    text = TEXTS[lang].get(key) or TEXTS["uz"].get(key, key)
    if isinstance(text, list):
        return text
    return text.format(**kw) if kw else text


def all_variants(key: str) -> set[str]:
    """Reply-tugma matnlari ikkala tilda — handler filtrlari uchun."""
    return {TEXTS[l][key] for l in TEXTS}


MENU_KEYS = ("btn_dash", "btn_search", "btn_buy", "btn_topup", "btn_sell", "btn_my", "btn_fav", "btn_check",
             "btn_lang", "btn_help", "btn_rules", "btn_admin", "btn_webapp")
MENU_TEXTS: set[str] = set().union(*(all_variants(k) for k in MENU_KEYS))
