# Gamebozor — Suhbat №3: Coin xizmati, boshqa o'yin valyutalari va O'zbekiston bozori (2026-11-09)

> Oldingi bosqichlar: suhbat-01 (maslahat), suhbat-02 (qarorlar va MVP kodi)

---

## 1. Quddusxonning savoli (asl matn)

> yana savol: bilganim efootball coinlarini sotib olib berish funksiyasini qo'shish (ko'pchilik foydalanuvchilarning visa kartasi yo'qligi sababli coin sotib olishga qiynalishadi). ma'lum komissiya evaziga xizmat ko'rsatish. bunda coin sotib olish uchun komissiyalarni ham hisobga olishing zarur.
> men bilmagan boshqa o'yinlarda ham o'zlarining coin yoki boshqa pul birliklarini sotib olish funksiyalarini o'rgan, taklif ber.
> bozorni o'rgan: o'zbrekiston bozorida akkauntlarni sotishga mo'ljallangan botlar bormi? efootballga oid o'zbek kanallari hajmini o'rgan, bizning botimiz ularning bozoriga ta'sir qilishi qanchalik?
> coin sotib olish xizmatini ko'rsatadigan botlar ko'pmi?

---

## 2. Claude javobi

### 2.1. eFootball coin qanday sotib olinadi (rasmiy yo'llar)

- O'yin ichidagi do'kon (Apple Pay / Google Play) — Visa/Mastercard kerak.
- Rasmiy Web Store (Coda Payments, 2025-noyabrdan, 65+ davlat) — bonus coinlar beradi, lekin **KONAMI ID bilan kirish talab qilinadi**. O'zbekiston ro'yxatda bor-yo'qligini tasdiqlay olmadik — Visa karta bilan kirib tekshirish kerak.
- Narx mo'ljali (AQSh): 130 coin ≈ $1.19, 1040 coin ≈ $9.99; Konami 2026-10-22 dan coin paketlarini o'zgartirdi (100/300/500/1000/2000/3000/5000/10000/15000).
- **Muhim farq:** PUBG UC, Free Fire, Mobile Legends — faqat **o'yinchi ID** bilan to'ldiriladi (parolsiz). eFootball'da esa ID bilan to'ldirish yo'q — **KONAMI ID login/paroli** kerak bo'ladi.

### 2.2. Xavflar (pentester nigohida)

1. **Konami qoidasi:** akkauntni boshqaga berish taqiqlangan; login orqali top-up aniqlansa, coinlar qaytarib olinishi yoki akkaunt bloklanishi mumkin.
2. **Javobgarlik:** mijoz parolini olganingizda, akkaunt yo'qolsa ayb sizga tushadi. Bizning asosiy qoidamiz "login/parol so'ramaymiz" bilan zid.
3. **Telegram qoidasi:** botda raqamli tovar (o'yin valyutasi) sotish — Telegram Stars orqali bo'lishi kerak; Click/Payme bilan aylanib o'tish bot cheklanishiga olib kelishi mumkin. Stars esa Visa'si yo'q auditoriya uchun noqulay.
4. **Soliq:** 2026-yil may oyidan Soliq qo'mitasi shaxsiy kartaga P2P orqali savdo tushumini kuzatmoqda (PF-95 farmon yo'l xaritasi). Ko'p o'tkazma qabul qilsang — "erkin band"/YaTT bo'lib Click/Payme merchant ulash kerak.
5. **Juda arzon raqobatchilar:** PUBG kanalida 660 UC = 114 000 so'm, rasmiy narx esa $9.99 ≈ 120 000 so'm. Ya'ni ayrimlar rasmiy narxdan arzon sotmoqda — bu ulgurji chegirma yoki shubhali manba (o'g'irlangan karta → keyin coin qaytarib olinadi) belgisi.

### 2.3. Komissiya hisob-kitobi (1000 coin ≈ $9.99 misolida, kurs ≈ 12 000 so'm)

Formula: **Mijoz narxi = USD narx × kurs × (1 + karta FX) × (1 + ustama) ÷ (1 − to'lov komissiyasi)**

| Qadam | Taxmin | So'm |
|---|---|---|
| Coin narxi | $9.99 × 12 000 | 119 880 |
| Visa karta konvertatsiya/xalqaro to'lov | ~1.5% (bankingga qarab) | 121 678 |
| Bizning ustama | 10% | 133 846 |
| Click/Payme qabul komissiyasi | ~2% | **136 578 → 137 000** |
| **Sof foyda** | | **~12 000 so'm/buyurtma** |

Oyiga 5 mln so'm sof foyda uchun ~410 ta buyurtma kerak. Ustama 8–15% oralig'ida raqobatga qarab sozlanadi. (Yangilangan hisob — Uzum Visa 2% bilan — suhbat-04 da.)

### 2.4. Bozor: O'zbek eFootball kanallari (TGStat, 2026)

| Kanal | Obunachi |
|---|---|
| EFOOTBALL EFUZTIME | ~53 900 |
| EFOOTBALL MOBILE UZ | ~32 500 |
| EFOOTBALL SHOP UZB (garant 1.5 mln gacha) | ~17 600 |
| UZPES / eFootball | ~15 300 |
| @efootball_mobile_uz | ~13 600 |
| EFOOTBALL ESPORTS 🇺🇿 | ~9 800 |

- Jami ~140 ming obuna (bir odam bir nechta kanalda bo'lgani uchun real auditoriya kamroq — taxminan 50–80 ming faol o'yinchi deb baholayman).
- Deyarli har bir yirik kanalning **o'z "Shop"/"Coins service" kanali** bor, savdo qo'lda, "garant" adminlar orqali. Hatto kanallarning o'zi ham sotiladi.
- **Maxsus akkaunt-bozor boti** topilmadi (bu "yo'q" degani emas, lekin yirik va mashhuri ko'rinmadi). Coin xizmatlari asosan kanal + lichka, bot kam.

### 2.5. Bizning ta'sirimiz

- Kontent kanallari (yangilik, video) — biz uchun **raqobatchi emas, hamkor/reklama joyi**.
- "Shop" kanallari — to'g'ridan-to'g'ri raqobatchi. Ularning zaif tomoni: qidiruv yo'q, filtr yo'q, qora ro'yxat yo'q, hamma narsa lichkada. Bizning ustunligimiz — **qulaylik + ishonch tizimi**.
- Realistik maqsad: 6 oyda faol eFootball auditoriyasining 10–20% i (5–15 ming foydalanuvchi).
- Strategiya: shop kanal egalarini **sotuvchi sifatida** botga jalb qilish (ularga ✅ belgi, TOP), raqobat emas — platforma bo'lish.

### 2.6. Boshqa o'yin valyutalari — O'zbekiston uchun takliflar

| Xizmat | Qanday to'ldiriladi | Parol kerakmi | Tavsiya |
|---|---|---|---|
| **Telegram Stars / Premium** | Fragment orqali username bilan, TON da | Yo'q | ⭐️ 1-o'rin: rasmiy, xavfsiz, auditoriya keng |
| **PUBG Mobile UC** | O'yinchi ID | Yo'q | ⭐️ 2-o'rin: O'zbekistonda eng katta talab |
| Free Fire almaz | O'yinchi ID | Yo'q | 3-o'rin |
| Mobile Legends almaz | ID + Zone | Yo'q | 4-o'rin |
| Steam balans (CS2, Dota 2) | Steam login nomi | Yo'q | MDHda juda mashhur |
| Roblox Robux | Gift card kod | Yo'q | Bolalar auditoriyasi |
| Brawl Stars / Clash (gems) | Supercell ID kodi | Kod kerak | Ehtiyot |
| eFootball coin | KONAMI ID login | **Ha** | ⚠️ Eng xavfli |
| Standoff 2 gold | Turlicha | Aniqlanmadi | Keyin o'rganamiz |

### 2.7. Tavsiya etilgan yo'l (3 bosqich)

**1-bosqich (darhol, xavfsiz):** Botda "🪙 Coin / UC xizmatlari" bo'limi — **tasdiqlangan top-up sotuvchilari e'lonlari** (narxlar jadvali bilan). Biz pulga tegmaymiz. Daromad: oylik joylashtirish to'lovi, TOP, ✅ belgi.

**2-bosqich (erkin band/YaTT + Click merchant ulangandan keyin):** O'zimiz parolsiz xizmatlarni sotamiz: Telegram Stars/Premium (Fragment), PUBG UC, Free Fire, MLBB.

**3-bosqich:** eFootball coin — faqat parolsiz yechim topilsa (rasmiy gift card yo'li yoki rasmiy hamkorlik). Hozircha eFootball coin'ni 1-bosqich modelida (sotuvchilar e'lonlari) beramiz.

---

## 3. Claude savollari

1. Erkin band (o'zini o'zi band qilgan) yoki YaTT sifatida ro'yxatdan o'tishga tayyormisan? (Click/Payme merchant uchun kerak.)
2. Qaysi bosqichdan boshlaymiz: 1-bosqich (sotuvchilar e'lonlari) kodini hozir yozaymi?
3. Visa kartangda xalqaro to'lov komissiyasi qancha (bankdan bilib berasanmi)?
4. TON hamyoning bormi (Fragment orqali Stars/Premium sotish uchun)?

## Manbalar
- konami.com/efootball — Account Sharing Prohibited; coin paketlari o'zgarishi (2026-10-22)
- efootball.codashop.com, evertry.co, gamemarket.gg — rasmiy Web Store
- uz.tgstat.com — O'zbekiston o'yin kanallari reytingi
- t.me/s/pubg_rev — UC narxlari namunasi
- kun.uz, kursiv.media, spot.uz — P2P soliq nazorati (2026)
- docs.tgshop.io — Click/Payme ulash talablari
- core.telegram.org, telegram.org/tos/stars — Stars siyosati
- daryo.uz, anhor.uz — dollar kursi (noyabr 2026)
