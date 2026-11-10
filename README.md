# 🎮 Gamebozor — o'yin akkauntlari e'lonlari boti

Bot: [@akkbozorbot](https://t.me/akkbozorbot) · Kanal: [@eakkbozor](https://t.me/eakkbozor)
Stack: **Python 3.11+ · aiogram 3 · SQLAlchemy 2 (async) · SQLite → PostgreSQL**

## Imkoniyatlar (v0.5)

| Foydalanuvchi | Admin |
|---|---|
| 🏠 **Dashboard** — bitta xabar ichida ishlaydigan panel: bozor ko'rsatkichlari, o'yinlar bo'limlari, profil, qoidalar | ✅/❌ premoderatsiya (sabab tugmalari bilan) |
| 🎮 Har o'yin — alohida bo'lim: soni, narx min/o'rta/max, eng yuqori TS, tez saralash; 🔜 «tez kunda» o'yinlar | Admin e'loni darhol chiqadi |
| 🔎 **Kengaytirilgan qidiruv**: narx oralig'i (`500k-2mln`), umumiy ko'rsatkich (TS ≥), Epic/Big Time, o'yinchi, pack, platforma, bog'lanish, division, faqat ✅ sotuvchilar, 5 xil saralash | 📊 Statistika, ⭐️ Stars daromad |
| ✍️ Shunchaki so'z yozish = qidiruv (`messi 3200`), `/search` | 📈 Reklama manbalari (`?start=ads_xxx`) |
| 🔔 Qidiruvga obuna — mos yangi e'lon tasdiqlanganda xabar | 📣 Hammaga xabar |
| 📤 Inline rejim: istalgan chatda `@akkbozorbot messi` yoki `#12` | `/ban` `/unban` `/verify` `/blacklist` `/unblacklist` `/refund` (faqat adminlarga ko'rinadigan `/` menyu) |
| 📱 **Mini App vitrina** (ixtiyoriy): kartochkalar to'ri, filtrlar paneli, galereya, Telegram mavzusi | 🚩 Shikoyatlar adminlarga keladi |
| 👋 Onboarding: START tugmasi → til → bot haqida → 📖 5 sahifali qo'llanma → 📜 qoidalar → ✅ rozilik | Sotildi → kanal posti avtomatik «SOTILDI» |
| 📜 Qoidalar (garant emasmiz, to'lovlar uchun javobgar emasmiz) — /start da, Dashboard'da, /rules | |
| ⌨️ `/` menyusida 17 ta buyruq (uz/ru) | |
| 💎 **PRO sotuvchi** (Stars): 20 ta e'lon, har 48 soatda avto-ko'tarish, bepul TOP, PRO belgisi, ustuvor moderatsiya — /pro | `/givepro ID KUN` — PRO berish |
| 🎮 eFootball + **PUBG Mobile** (rank, X-Suit, mifiklar, Glacier qurollar, UC) | `/delreview ID` — soxta sharhni o'chirish |
| 📉 **Narx tushishi**: sotuvchi narxni o'zgartiradi → saralaganlar va mos obunachilarga xabar, eski narx chizilgan | ⚠️ 1–2⭐️ baholar adminlarga keladi |
| ⭐️ **Reyting va sharhlar**: faqat «Bog'lanish» bosgan xaridor baholaydi; sotildi → baho so'raladi | |
| 🖼 **Kanal uchun avtomatik banner**: ko'rsatkichlar, narx, skrinshot, TOP/✅/⭐️, «SOTILDI» muhri | |
| ➕ E'lon berish, 📂 Mening e'lonlarim, 🚀 TOP (Stars), ❤️, 🛡 sotuvchini tekshirish, 🇺🇿/🇷🇺 | |

## 0. Yangilanishni olish (`git pull`)

Kod GitHub'da yangilanganda, bot ishlayotgan joyda eng so'nggi versiyani tortib olish:

**Kompyuterda (Windows, VS Code terminali):**
```powershell
cd C:\Users\Surface\gamebozor
git pull
pip install -r requirements.txt      # yangi kutubxona qo'shilgan bo'lsa
# botni to'xtating (Ctrl+C) va qayta ishga tushiring:
python -m bot
```

**Serverda (Oracle / VPS):**
```bash
cd ~/gamebozor
git pull
.venv/bin/pip install -r requirements.txt
sudo systemctl restart gamebozor
journalctl -u gamebozor -f            # loglarni ko'rish (chiqish: Ctrl+C)
```

`.env` va `gamebozor.db` `git pull` dan ta'sirlanmaydi — sozlamalar va e'lonlar saqlanib qoladi.
Bazaga yangi ustun/jadval kerak bo'lsa, bot ishga tushganda o'zi qo'shadi.

## 1. Kompyuterda ishga tushirish (VS Code, tekin)

```bash
git clone <repo> gamebozor && cd gamebozor
python -m venv .venv
# Windows: .venv\Scripts\activate    Linux/Mac: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env      # Linux/Mac: cp .env.example .env
# .env ichida BOT_TOKEN ni yozing
python -m bot
```

**Muhim:** botni @eakkbozor kanaliga **admin** qilib qo'shing («Post messages» va «Edit messages of others» huquqlari bilan), aks holda e'lonlar kanalga chiqmaydi.

Test (Telegramsiz, butun oqim):
```bash
python -m tests.test_flow
```

## 2. 24/7 serverda (Oracle Cloud Always Free yoki VPS)

📖 To'liq qadamma-qadam qo'llanma: **[docs/SERVER.md](docs/SERVER.md)** (Oracle ro'yxatdan o'tish, VM yaratish, SSH, muammolar).

Qisqasi — serverda (Ubuntu 24.04) bitta buyruq:
```bash
curl -fsSL https://raw.githubusercontent.com/abduquddus1990/gamebozor/main/deploy/setup_server.sh -o setup.sh && bash setup.sh
```
Bot tokenini so'raydi, qolganini o'zi qiladi: paketlar, cloudflared, swap, kod, `.env`, systemd (24/7), kunlik zaxira.
Yangilash: `bash ~/gamebozor/deploy/update.sh`. Loglar: `sudo journalctl -u gamebozor -f`.

Windows kompyuterda tez ishga tushirish: `start_bot.bat` ni ikki marta bosing.

## 3. Yangi o'yin qo'shish

`bot/services/games.py` da shablon bor (PUBG Mobile, Standoff 2 tayyor). Yoqish uchun `enabled=False` → `True`.
Dashboard bo'limi, qidiruv filtrlari (`filter="min" | "choice" | "text"`) va Mini App filtrlari avtomatik paydo bo'ladi.
O'chirilgan o'yinlar Dashboard'da «🔜 tez kunda» bo'lib turadi.

Coin/UC xizmati turini qo'shish: `kind="topup"` bilan yangi `Game` yozing (masalan Free Fire almaz) — u «🪙 Coin / UC» bo'limida chiqadi.

## 4. @BotFather sozlamalari (bir marta)

- **Inline rejim**: `/setinline` → @akkbozorbot → placeholder: `messi, TS 3200, #raqam`. (`/setinlinefeedback` shart emas.)
- Bot tavsifi, buyruqlar menyusi (`/`) va «START» tugmasi bot ishga tushganda **avtomatik** o'rnatiladi
  (`set_my_description` — bo'sh chatda smaylik/stiker taklifi o'rniga «START» tugmasi chiqadi).
- Avatar (640×640) — @BotFather → `/setuserpic`.

## 5. 📱 Mini App (vitrina) — ixtiyoriy

Vitrina bot bilan bitta jarayonda ishlaydi (aiohttp, port `WEB_PORT`). Telegram faqat **HTTPS** manzilni ochadi.

### Eng oson tekin yo'l — `WEBAPP_URL=auto` (Cloudflare Quick Tunnel)

Akkaunt ham, domen ham kerak emas. Bot ishga tushganda tunnelni **o'zi** ochadi va adminlarga manzilni yuboradi.

1. `cloudflared` ni o'rnating (bir marta):
   - **Windows:** `winget install --id Cloudflare.cloudflared` (sizning kompyuteringizda allaqachon bor)
   - **Ubuntu (server):**
     ```bash
     curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb -o cf.deb
     sudo dpkg -i cf.deb
     ```
2. `.env` da: `WEBAPP_URL=auto`
3. Botni qayta ishga tushiring → adminga «📱 Vitrina ishga tushdi: https://….trycloudflare.com» xabari keladi.
   Telegram'da /start bosing — pastki menyuda «📱 Vitrina» tugmasi paydo bo'ladi.

⚠️ Cheklov: tekin manzil har safar bot qayta ishga tushganda **o'zgaradi**. Dashboard'dagi tugma doim yangi manzilni oladi;
foydalanuvchilarning pastki menyusidagi tugma ular /start bosganda yangilanadi. Doimiy manzil kerak bo'lsa —
o'z domeningiz (~$10/yil) + Cloudflare named tunnel, keyin `WEBAPP_URL=https://shop.domeningiz.uz`.

Xavfsizlik: har bir API so'rovda Telegram `initData` imzosi tekshiriladi; rasmlar faqat faol e'lonlar uchun beriladi.

## 6. Telegram Ads uchun havolalar

Har bir kampaniyaga alohida havola bering, admin panel → «📈 Reklama manbalari» da qaysi biri qancha odam olib kelganini ko'rasiz:
```
https://t.me/akkbozorbot?start=ads_efootball_uz1
https://t.me/akkbozorbot?start=ads_efootball_ru1
```

## Tuzilma
```
bot/
  __main__.py          ishga tushirish, routerlar, «/» buyruqlar, bot tavsifi, Mini App serveri
  config.py            .env sozlamalari
  i18n.py              uz/ru matnlar (qo'llanma, qoidalar, dashboard, qidiruv)
  keyboards.py         tugmalar (dashboard, qidiruv paneli, karusel)
  callbacks.py         callback_data turlari
  states.py            FSM holatlari
  middlewares.py       DB sessiya, foydalanuvchi, til, ban, antiflood
  db/models.py         User, Listing, Favorite, Report, Blacklist, Payment, SavedSearch, ContactLog, Review
  db/base.py           jadvallar + yengil migratsiya (yangi ustunlar avtomatik qo'shiladi)
  services/games.py    o'yin shablonlari (forma + qidiruv filtrlari)
  services/search.py   qidiruv dvigateli, narx oralig'ini o'qish, bozor ko'rsatkichlari
  services/alerts.py   🔔 obunalar bildirishnomasi
  services/render.py   e'lon kartochkasi matni
  services/banner.py   kanal uchun rasmli banner (Pillow)
  services/reputation.py sotuvchi reytingi
  services/pro.py      💎 PRO tarif, avto-ko'tarish, eslatmalar
  services/listings.py moderatsiya, kanal
  handlers/            start (onboarding), dashboard, search, sell, my_listings, reviews, catalog, inline, admin
  web/server.py        Mini App API (initData tekshiruvi)
  web/tunnel.py        WEBAPP_URL=auto — tekin Cloudflare tunnel
  web/static/index.html Mini App interfeysi
deploy/                setup_server.sh (bir buyruqli o'rnatish), update.sh
docs/                  suhbatlar jurnali, SERVER.md (server qo'llanmasi)
tests/test_flow.py     oflayn end-to-end test (bot + Mini App API)
```

## Xavfsizlik
- `.env` hech qachon GitHub'ga yuklanmaydi (`.gitignore` da). Token oshkor bo'lsa — @BotFather → /revoke.
- Bot login/parol so'ramaydi va saqlamaydi.
- Mini App API faqat imzosi to'g'ri Telegram `initData` bilan ishlaydi.
- HTML injection'dan himoya: foydalanuvchi matnlari `escape` qilinadi.
