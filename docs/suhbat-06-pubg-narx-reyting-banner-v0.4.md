# Gamebozor — Suhbat №6: git pull, tekin Mini App, PUBG, narx tushishi, reyting, banner (v0.4) (2026-11-10)

> Oldingi bosqich: suhbat-05 (Dashboard, kengaytirilgan qidiruv, v0.3)

---

## 1. Quddusxonning javoblari (asl matn)

> 1. git pull qanday qilinadi?
> 2. vaqtinchalik tekinni yo'lini ko'rsat
> 3. purg ochaver
> 4. keyin uchalasini ham qilaver

---

## 2. Javoblar va qilingan ishlar

### 2.1. `git pull`
README'ga «0. Yangilanishni olish» bo'limi qo'shildi:
- **Kompyuterda:** `cd C:\Users\Surface\gamebozor` → `git pull` → `pip install -r requirements.txt` → botni qayta ishga tushirish (`python -m bot`).
- **Serverda:** `cd ~/gamebozor && git pull && .venv/bin/pip install -r requirements.txt && sudo systemctl restart gamebozor`.
- `.env` va baza (`gamebozor.db`) `git pull` da o'zgarmaydi. Yangi jadval/ustunlar bot ishga tushganda avtomatik qo'shiladi.

### 2.2. Tekin Mini App — `WEBAPP_URL=auto`
- Bot ishga tushganda **Cloudflare Quick Tunnel**ni o'zi ochadi (akkaunt va domen kerak emas), HTTPS manzilni oladi va adminlarga yuboradi.
- Kompyuterda `cloudflared` allaqachon o'rnatilgan. Sinovda haqiqiy tunnel ochildi va vitrina sahifasi internetdan ochildi ✅.
- Cheklovi: bot qayta ishga tushsa, manzil o'zgaradi. Dashboard tugmasi har doim yangi manzilni oladi, pastki menyudagi tugma esa /start bosilganda yangilanadi.

### 2.3. PUBG Mobile bo'limi ochildi
Maydonlar: bog'lanish, Level (≥ filtr), **rank (Bronze…Conqueror tanlovi)**, **X-Suit soni**, mifiklar soni, Glacier/yaxshilangan qurollar (matnli qidiruv), UC qoldig'i.
Bularning hammasi qidiruvda, Dashboard'da, Mini App'da va bannerda avtomatik chiqadi. Standoff 2 hali «🔜 tez kunda».

### 2.4. 📉 Narx tushishi bildirishnomasi
- «📂 Mening e'lonlarim» → e'lon → **«✏️ Narxni o'zgartirish»**.
- Narx tushsa:
  - eski narx chizilgan holda ko'rsatiladi (bot, kanal, banner, Mini App);
  - e'lonni ❤️ saralaganlarga «📉 Narx tushdi» xabari boradi;
  - 🔔 obunasi eski narxda mos kelmagan, yangi narxda mos kelgan foydalanuvchilarga xabar boradi.
- Kanal posti (banner bilan birga) avtomatik yangilanadi.

### 2.5. ⭐️ Sotuvchi reytingi va sharhlar
- Soxta baholardan himoya: baho faqat shu e'londa **«📞 Bog'lanish» ni bosgan** xaridorga ruxsat etiladi. Bitta e'longa bitta baho qo'yiladi, o'ziga baho qo'yib bo'lmaydi.
- Bog'lanish xabarida «⭐️ Sotuvchini baholash» tugmasi bor. Sotuvchi «✅ Sotildi» bosganda, bog'langan xaridorlardan avtomatik baho so'raladi.
- 1–5 ⭐️ va ixtiyoriy izoh. Sotuvchiga bildirishnoma boradi, 1–2 ⭐️ baholar adminlarga ham yuboriladi. Admin `/delreview ID` bilan sharhni o'chiradi.
- Reyting e'lon kartochkasida (⭐️ 4.8 (12 sharh)), /check natijasida (so'nggi sharhlar bilan), profilda, bannerda va Mini App'da ko'rinadi.

### 2.6. 🖼 Kanal uchun avtomatik banner
- 1280×720 rasm:
  - chapda o'yin, sarlavha, 4 ta asosiy ko'rsatkich, yulduz o'yinchilar/qurollar va katta narx;
  - o'ngda sotuvchining skrinshoti.
- Belgilar: TOP, «tasdiqlangan sotuvchi», reyting, «NARX TUSHDI». Sotilganda rasm qorayadi va **«SOTILDI» muhri** bosiladi.
- `CHANNEL_BANNER=0` qilinsa, avvalgidek birinchi skrinshot chiqadi. Banner chizishda xato bo'lsa ham post baribir chiqadi.
- Serverda shrift uchun: `sudo apt install fonts-dejavu-core`.

### Test
`python -m tests.test_flow` — barcha eski tekshiruvlar va yangilari o'tdi ✅. Yangi tekshiruvlar: PUBG tanlovi, narx tushishi xabari, sotildi → baho so'rovi, baho, izoh, takroriy baho rad etilishi, /check'da reyting, kanal posti banner bilan chiqishi.

---

## 3. Keyingi takliflar
1. Doimiy domen (~$10/yil), shunda Mini App manzili o'zgarmaydi.
2. Pro sotuvchi tarifi (Stars): cheksiz e'lon va har 2 kunda avtomatik ko'tarish.
3. Standoff 2 / Free Fire / Mobile Legends bo'limlari.
4. PostgreSQL ga o'tish (foydalanuvchilar 5–10 mingdan oshganda).
