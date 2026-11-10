# Gamebozor — Suhbat №2: Qarorlar va MVP kodi (2026-11-09)

> Oldingi bosqich: `suhbat-01-boshlangich-maslahat.md`

---

## 1. Quddusxonning javoblari (asl matn)

> 1. python
> 2. o'zbek, rus
> 3. hozircha o'zim sinashim uchun bepul variantni ko'r, visa kartam bor. ishga tushirganda 3-5 lik vps olaman.
> 4. 20 gram
> 5. kanal: eakkbozor, bot: akkbozorbot
> 6. hozircha 2ta admin: ID 768121418, 8987694079
> 7. kelajakda ko'ramiz
> 8. roziman.

## 2. Qabul qilingan qarorlar

| # | Mavzu | Qaror |
|---|---|---|
| 1 | Til | Python 3.11+, aiogram 3.31, SQLAlchemy 2 async |
| 2 | Interfeys tillari | O'zbek + rus (birinchi /start da tanlanadi) |
| 3 | Server | Test: o'z kompyuteri yoki Oracle Cloud Always Free (Visa bor). Ishga tushirishda: $3–5 VPS |
| 4 | Reklama | Telegram Ads, 20 Gram; har kampaniyaga `?start=ads_...` havola |
| 5 | Kanal / bot | @eakkbozor / @akkbozorbot |
| 6 | Adminlar | 768121418, 8987694079 |
| 7 | Garant | Kelajakda ko'rib chiqiladi (hozir yo'q) |
| 8 | TOP to'lovi | Telegram Stars (XTR): 3 kun — 50 ⭐️, 7 kun — 100 ⭐️ (.env da o'zgartiriladi) |
| — | Foydalanuvchi e'lonlari | Hozirdan, premoderatsiya bilan; tekin limit — 3 ta faol e'lon |

## 3. MVP v0.1 — tayyor funksiyalar

- /start + til tanlash, deep-link: `l_ID` (kanaldan e'lon), `r_ID` (referal), `ads_...` (reklama manbai)
- Katalog: narx oralig'i filtri, bitta xabarda karusel (◀️ ▶️), TOP e'lonlar birinchi
- E'lon berish: eFootball shabloni (platforma, bog'lanish, Team Strength, Epic, Big Time, top o'yinchilar, Coin, GP, Division, donat), narx, kelishuv, izoh, 10 tagacha rasm (albom), kontakt, ko'rib chiqish
- Moderatsiya: ikkala adminga albom + ✅/❌; rad etish sabablari tugmalarda; sotuvchiga ikki tilda xabar
- Kanal: tasdiqlangan e'lon «Batafsil» tugmasi bilan chiqadi; «Sotildi» → post avtomatik yangilanadi; «O'chirish» → post o'chadi
- Mening e'lonlarim: holat, ko'rishlar soni, TOP, Sotildi, O'chirish
- TOP: Stars invoice → pre_checkout tekshiruvi → muddat uzaytiriladi → kanalda 🔥 bilan qayta chiqadi; `/refund` bilan qaytarish
- Xavfsizlik: ❤️ saralanganlar, 📞 aloqa (sotuvchiga «qiziqishdi» bildirishnomasi), 🚩 shikoyat, 🔎 sotuvchini tekshirish (qora ro'yxat + shikoyatlar + tarix), ✅ tasdiqlangan sotuvchi
- Admin panel: statistika, Stars daromad, reklama manbalari, moderatsiyadagilar, hammaga xabar; `/ban /unban /verify /blacklist /unblacklist /refund`
- /help, /terms (foydalanish shartlari), /paysupport (Stars uchun majburiy)
- Antiflood, ban middleware, HTML escape
- PUBG Mobile va Standoff 2 shablonlari tayyor (o'chirilgan holda)
- Oflayn end-to-end test: `python -m tests.test_flow` — o'tdi ✅

## 4. Keyingi qadamlar (v0.2 rejasi)

1. Quddusxon: botni @eakkbozor ga admin qilish, `.env` to'ldirish, kompyuterda sinash.
2. Admin sifatida 10–20 ta boshlang'ich e'lon kiritish.
3. GitHub private repo → Oracle Cloud ga joylash.
4. v0.2: saqlangan qidiruv bildirishnomalari, referal mukofoti (tekin TOP), e'lon rasmli kartochkasi (Pillow), Redis FSM, PostgreSQL.
5. Telegram Ads: 2 ta kampaniya (uz/ru), har biriga ~10 Gram, 7 kundan keyin natijani solishtirish.
