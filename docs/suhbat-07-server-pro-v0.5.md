# Gamebozor — Suhbat №7: Token, server, PRO tarif (v0.5) (2026-11-10)

> Oldingi bosqich: suhbat-06 (PUBG, narx tushishi, reyting, banner)

---

## 1. Quddusxonning so'rovi (asl matn, token yashirilgan)

> 9183337212:AAH… — bot tokeni zarur joyga to'ldir, keyinchalik yangilab qo'yaman.
> server (oracle/vps) da qanday yo'l tutishni batafsil o'rgat.
> env faylidagi o'zgarishlarni o'zing qil. umuman barcha narsani maksimal ravishda o'zing avtomatik to'ldir, bajar.
> serverdagi buyruqlarni ham o'zing ber
> PRO sotuvchi tarifini qil. hozircha pulli domen ololmayman. loyiha ishlashini ko'ray avval

> 🔐 Token faqat `.env` faylida (GitHub'ga yuklanmaydi). Bu jurnalda to'liq yozilmadi.

---

## 2. Qilingan ishlar

### 2.1. Token va `.env`
- Token tekshirildi: bot **@Akkbozorbot** (id 9183337212), inline rejim yoqilgan.
- Kompyuterdagi `.env` to'liq to'ldirildi: token, kanal, adminlar, PRO narxlari, `WEBAPP_URL=auto` (tekin vitrina). `SUPPORT` — 1-admin profiliga havola.
- Bot kompyuterda ishga tushirildi va Cloudflare tunneli ochildi.

### 2.2. Aniqlangan muammolar (Quddusxon hal qilishi kerak)
1. **@eakkbozor kanalida bot admin emas** — e'lonlar kanalga chiqmaydi. Kanal nomi «Sport xabarlar» ekan; to'g'ri kanal ekanini tekshiring.
2. **Ikkala admin ham botga hali /start bosmagan** — moderatsiya xabarlari kelishi uchun ikkalasi ham @Akkbozorbot ga /start bosishi kerak.

### 2.3. Server
- `deploy/setup_server.sh` — Ubuntu'da bitta buyruq bilan to'liq o'rnatish: paketlar, cloudflared, swap, kod, `.env` (tokenni so'raydi), systemd (24/7), kunlik zaxira nusxa.
- `deploy/update.sh` — zaxira nusxa → `git pull` → kutubxonalar → qayta ishga tushirish.
- `docs/SERVER.md` — Oracle Cloud'da ro'yxatdan o'tish, VM yaratish (A1.Flex / E2.1.Micro), Windows'dan SSH, muammolar jadvali.
- `start_bot.bat` — Windows'da ikki marta bosib ishga tushirish.

### 2.4. 💎 PRO sotuvchi tarifi
| Imkoniyat | Tekin | PRO |
|---|---|---|
| Faol e'lonlar | 3 | 20 |
| Avtomatik ko'tarish | — | har 48 soatda ro'yxat boshiga |
| Bepul TOP (3 kun) | — | har bir xaridga 1 ta |
| Belgi | — | 💎 PRO (bot, kanal, banner) |
| Moderatsiya | oddiy | ustuvor |

- Narx: **30 kun — 250 ⭐️**, **90 kun — 600 ⭐️** (`.env` da o'zgartiriladi).
- Muddat uzaytiriladi (qo'shiladi). Tugashidan 3 kun oldin eslatma, tugaganda xabar.
- Admin: `/givepro ID KUN` — sinov yoki hamkorlar (shop kanal egalari) uchun bepul PRO.
- Kirish: /pro, Dashboard → «💎 PRO tarif».
- Testlar o'tdi ✅: xarid, begona to'lovni rad etish, bepul TOP, PRO belgisi, avto-ko'tarish, /givepro.

---

## 3. Keyingi qadamlar
1. Botni @eakkbozor ga admin qilish, ikkala admin /start bosishi.
2. Telegram'da sinash: /start → qo'llanma → qoidalar → e'lon berish → moderatsiya → kanal.
3. Oracle akkaunt ochib, `docs/SERVER.md` bo'yicha serverga ko'chirish (kompyuterdagi botni to'xtatib).
4. Token keyinroq @BotFather → /revoke bilan yangilanadi va `.env` ga yoziladi.
