# 🖥 Gamebozor'ni serverga joylash — to'liq qo'llanma

Maqsad: bot kompyuteringiz o'chiq bo'lsa ham **24/7** ishlashi.
Ikki yo'l bor, ikkalasida ham buyruqlar bir xil:

| Yo'l | Narx | Kimga |
|---|---|---|
| **A. Oracle Cloud Always Free** | Tekin (Visa karta faqat tasdiq uchun) | Sinov va boshlang'ich bosqich |
| **B. Arzon VPS** (Hetzner, Aeza, Timeweb, DigitalOcean …) | $3–5/oy | Foydalanuvchilar ko'payganda |

> ⚠️ **Muhim:** bitta bot bir vaqtda faqat **bitta joyda** ishlashi mumkin. Serverda ishga tushirgandan keyin
> kompyuteringizdagi botni to'xtating (terminalda `Ctrl+C`), aks holda Telegram «Conflict» xatosini beradi.

---

## A. Oracle Cloud Always Free — qadamma-qadam

### A1. Ro'yxatdan o'tish (bir marta, ~15 daqiqa)
1. https://www.oracle.com/cloud/free/ → **Start for free**.
2. Mamlakat: **Uzbekistan**, email, ism-familiya (lotincha, kartadagidek).
3. **Home Region** — eng yaqin va bo'sh mintaqani tanlang: *Germany Central (Frankfurt)*, *Netherlands (Amsterdam)*
   yoki *UK South (London)*. ⚠️ Mintaqani keyin o'zgartirib bo'lmaydi.
4. Visa kartani kiriting (Uzum Visa bo'ladi) — tasdiq uchun ~$1 vaqtincha bloklanib, qaytariladi. Always Free resurslar uchun pul yechilmaydi.
5. Email tasdiqlanadi, akkaunt 5–30 daqiqada tayyor bo'ladi.

### A2. Server (VM) yaratish
1. Oracle konsol → ☰ menyu → **Compute → Instances → Create instance**.
2. **Name:** `gamebozor`.
3. **Image and shape → Edit:**
   - Image: **Canonical Ubuntu 24.04** (Change image → Ubuntu).
   - Shape: **Ampere → VM.Standard.A1.Flex** (1 OCPU, 6 GB RAM — tekin va kuchli).
     Agar «Out of capacity» desa → **Specialty and previous generation → VM.Standard.E2.1.Micro** (1 GB RAM, ham tekin; skript swap qo'shadi).
4. **Networking:** default (yangi VCN, public IP — *Assign a public IPv4 address* belgilangan bo'lsin).
5. **Add SSH keys → Generate a key pair for me → Save private key** (`ssh-key-….key` faylini saqlang, masalan `C:\Users\Surface\.ssh\oracle.key`).
6. **Create** → 1–2 daqiqada holat **RUNNING** bo'ladi. **Public IP address** ni yozib oling (masalan `141.147.10.20`).

> Port ochish **shart emas**: bot Telegram'ga o'zi ulanadi (polling), Mini App esa Cloudflare tunneli orqali ishlaydi.

### A3. Serverga ulanish (Windows)
PowerShell yoki VS Code terminalida:
```powershell
# kalit faylini faqat o'zingiz o'qiy oladigan qilish (bir marta)
icacls "C:\Users\Surface\.ssh\oracle.key" /inheritance:r /grant:r "$($env:USERNAME):(R)"

# ulanish (IP ni o'zingiznikiga almashtiring)
ssh -i "C:\Users\Surface\.ssh\oracle.key" ubuntu@141.147.10.20
```
Birinchi marta `Are you sure you want to continue connecting?` → `yes`.
Ekranda `ubuntu@gamebozor:~$` chiqsa — serverdasiz.

### A4. Bitta buyruq bilan o'rnatish
Serverda (ubuntu@gamebozor:~$) quyidagini nusxalab qo'ying:
```bash
curl -fsSL https://raw.githubusercontent.com/abduquddus1990/gamebozor/main/deploy/setup_server.sh -o setup.sh && bash setup.sh
```
Skript bot tokenini so'raydi — @BotFather bergan tokenni qo'ying va Enter bosing.
Qolgan ishni o'zi qiladi (3–7 daqiqa):
- Python, shriftlar, `cloudflared` o'rnatadi;
- RAM kichik bo'lsa, swap qo'shadi;
- kodni yuklab, kutubxonalarni o'rnatadi;
- `.env` ni to'ldiradi: admin ID'lar, kanal, `WEBAPP_URL=auto`;
- systemd xizmatini yaratadi: server qayta yonsa ham bot o'zi ishga tushadi;
- har kuni bazaning zaxira nusxasini oladi.

Oxirida `✅ Gamebozor ishlayapti!` va loglar ko'rinadi. Adminlarga Telegram'da «📱 Vitrina ishga tushdi» xabari keladi.

### A5. Kompyuterdagi bazani serverga ko'chirish (ixtiyoriy)
Kompyuterda sinov uchun kiritgan e'lonlaringizni saqlab qolmoqchi bo'lsangiz. **Kompyuteringizda** (PowerShell):
```powershell
scp -i "C:\Users\Surface\.ssh\oracle.key" C:\Users\Surface\gamebozor\gamebozor.db ubuntu@141.147.10.20:~/gamebozor/
```
Keyin serverda: `sudo systemctl restart gamebozor`.

---

## B. Pullik VPS ($3–5/oy)
1. Provayderda **Ubuntu 24.04**, 1 vCPU / 1–2 GB RAM server oling.
2. Root paroli yoki SSH kalit bilan kiring: `ssh root@IP`.
3. Oddiy foydalanuvchi yarating (xavfsizroq):
   ```bash
   adduser gb && usermod -aG sudo gb && su - gb
   ```
4. **A4** dagi bitta buyruqni ishga tushiring — xuddi shu tarzda o'rnatiladi.

---

## Kundalik boshqaruv (serverda)

| Vazifa | Buyruq |
|---|---|
| Jonli loglar | `sudo journalctl -u gamebozor -f` (chiqish: `Ctrl+C`) |
| Holat | `systemctl status gamebozor` |
| Qayta ishga tushirish | `sudo systemctl restart gamebozor` |
| To'xtatish / yoqish | `sudo systemctl stop gamebozor` / `sudo systemctl start gamebozor` |
| **Yangilash** (GitHub'dan) | `bash ~/gamebozor/deploy/update.sh` |
| Sozlamalarni o'zgartirish | `nano ~/gamebozor/.env` → `Ctrl+O`, `Enter`, `Ctrl+X` → restart |
| Tokenni almashtirish | `.env` dagi `BOT_TOKEN=` qatorini yangilang → restart |
| Zaxira nusxalar | `ls ~/gamebozor-backups` |
| Vitrina manzili | `sudo journalctl -u gamebozor \| grep trycloudflare \| tail -1` |

## Muammolar va yechimlar

| Belgi | Sabab / yechim |
|---|---|
| `Conflict: terminated by other getUpdates request` | Bot boshqa joyda ham ishlayapti (kompyuterda). U yerdagisini to'xtating. |
| `Unauthorized` | Token noto'g'ri yoki /revoke qilingan → `.env` da yangilang. |
| Kanalga e'lon chiqmayapti | Bot @eakkbozor kanalida **admin** emas → Kanal → Administrators → Add Admin → @Akkbozorbot (Post / Edit / Delete messages). |
| «📱 Vitrina» ochilmayapti | Bot qayta ishga tushganda tunnel manzili o'zgaradi → Telegram'da /start bosing. |
| Server javob bermayapti | Oracle konsol → Instance → **Reboot**. Bot o'zi qayta ishga tushadi. |
| Oracle «idle» deb serverni to'xtatdi | Always Free'da juda kam yuklangan VM vaqti-vaqti bilan to'xtatilishi mumkin → konsoldan **Start**; doimiy ishlash uchun akkauntni *Pay As You Go* ga o'tkazing (Always Free resurslari baribir tekin qoladi). |
