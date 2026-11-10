# 🎮 Gamebozor — o'yin akkauntlari e'lonlari boti

Bot: [@akkbozorbot](https://t.me/akkbozorbot) · Kanal: [@eakkbozor](https://t.me/eakkbozor)
Stack: **Python 3.11+ · aiogram 3 · SQLAlchemy 2 (async) · SQLite → PostgreSQL**

## Imkoniyatlar (v0.3)

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
| ➕ E'lon berish, 📂 Mening e'lonlarim, 🚀 TOP (Stars), ❤️, 🛡 sotuvchini tekshirish, 🇺🇿/🇷🇺 | |

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

## 2. 24/7 tekin: Oracle Cloud Always Free

1. oracle.com/cloud/free → ro'yxatdan o'tish (Visa karta tasdiq uchun, pul yechilmaydi).
2. Compute → Create instance → Ubuntu 22.04/24.04, shape **VM.Standard.E2.1.Micro** (Always Free).
3. SSH bilan kirib:
```bash
sudo apt update && sudo apt install -y python3-venv git
git clone <repo> ~/gamebozor && cd ~/gamebozor
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env && nano .env
```
4. Avtomatik ishga tushish (systemd):
```bash
sudo tee /etc/systemd/system/gamebozor.service <<EOF
[Unit]
Description=Gamebozor bot
After=network-online.target
[Service]
WorkingDirectory=/home/ubuntu/gamebozor
ExecStart=/home/ubuntu/gamebozor/.venv/bin/python -m bot
Restart=always
RestartSec=5
[Install]
WantedBy=multi-user.target
EOF
sudo systemctl enable --now gamebozor
journalctl -u gamebozor -f     # loglar
```
Yangilash: `git pull && sudo systemctl restart gamebozor`. Xuddi shu yo'riqnoma $3–5 lik VPS uchun ham ishlaydi.

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

Eng oson tekin yo'l — **Cloudflare Tunnel**:
```bash
# serverda (Ubuntu): cloudflared o'rnatish
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
./cloudflared tunnel --url http://localhost:8080      # → https://xxxx.trycloudflare.com
```
`.env` da `WEBAPP_URL=https://xxxx.trycloudflare.com` yozing va botni qayta ishga tushiring — pastki menyuda
«📱 Vitrina» va Dashboard'da «📱 Vitrina (Mini App)» tugmalari paydo bo'ladi.
Doimiy manzil uchun: Cloudflare'da bepul akkaunt + o'z domeningiz (named tunnel) yoki VPS'da nginx + Let's Encrypt.

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
  db/models.py         User, Listing, Favorite, Report, Blacklist, Payment, SavedSearch
  db/base.py           jadvallar + yengil migratsiya (yangi ustunlar avtomatik qo'shiladi)
  services/games.py    o'yin shablonlari (forma + qidiruv filtrlari)
  services/search.py   qidiruv dvigateli, narx oralig'ini o'qish, bozor ko'rsatkichlari
  services/alerts.py   🔔 obunalar bildirishnomasi
  services/render.py   e'lon kartochkasi matni
  services/listings.py moderatsiya, kanal
  handlers/            start (onboarding), dashboard, search, sell, my_listings, catalog, inline, admin
  web/server.py        Mini App API (initData tekshiruvi)
  web/static/index.html Mini App interfeysi
docs/                  suhbatlar jurnali (qarorlar tarixi)
tests/test_flow.py     oflayn end-to-end test (bot + Mini App API)
```

## Xavfsizlik
- `.env` hech qachon GitHub'ga yuklanmaydi (`.gitignore` da). Token oshkor bo'lsa — @BotFather → /revoke.
- Bot login/parol so'ramaydi va saqlamaydi.
- Mini App API faqat imzosi to'g'ri Telegram `initData` bilan ishlaydi.
- HTML injection'dan himoya: foydalanuvchi matnlari `escape` qilinadi.
