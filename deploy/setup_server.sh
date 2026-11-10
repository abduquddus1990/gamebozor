#!/usr/bin/env bash
# =====================================================================
#  Gamebozor — serverga bir buyruq bilan o'rnatish (Ubuntu 22.04 / 24.04)
#  Oracle Cloud Always Free yoki istalgan VPS uchun.
#
#  Ishlatish (serverda):
#    curl -fsSL https://raw.githubusercontent.com/abduquddus1990/gamebozor/main/deploy/setup_server.sh -o setup.sh
#    bash setup.sh
#
#  Skript nima qiladi:
#    1) kerakli dasturlar: git, python3-venv, shriftlar, cloudflared (Mini App tunneli)
#    2) RAM kichik bo'lsa (1 GB) — 2 GB swap
#    3) kodni GitHub'dan yuklaydi (~/gamebozor), virtual muhit, kutubxonalar
#    4) .env ni so'rab to'ldiradi (bot tokeni) — faqat birinchi marta
#    5) systemd xizmati: server qayta yonsa ham bot o'zi ishga tushadi
#    6) har kuni 04:00 da bazaning zaxira nusxasi (~/gamebozor-backups, 14 kun)
#  Qayta ishga tushirish xavfsiz — mavjud .env va bazaga tegmaydi.
# =====================================================================
set -euo pipefail

REPO="https://github.com/abduquddus1990/gamebozor.git"
APP_DIR="$HOME/gamebozor"
SERVICE="gamebozor"
G='\033[1;32m'; Y='\033[1;33m'; R='\033[1;31m'; N='\033[0m'
step() { echo -e "\n${G}==> $*${N}"; }
warn() { echo -e "${Y}!! $*${N}"; }

if [ "$(id -u)" -eq 0 ]; then
  warn "root sifatida emas, oddiy foydalanuvchi (masalan ubuntu) bilan ishga tushiring."
fi

step "1/7 Tizim paketlari"
sudo apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y git curl python3 python3-venv python3-pip fonts-dejavu-core sqlite3

PYV=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)' \
  || { echo -e "${R}Python $PYV juda eski (3.10+ kerak). Ubuntu 24.04 tanlang.${N}"; exit 1; }
echo "Python $PYV ✓"

step "2/7 Swap (kichik RAM uchun)"
MEM_MB=$(awk '/MemTotal/ {print int($2/1024)}' /proc/meminfo)
if [ "$MEM_MB" -lt 2000 ] && ! swapon --show | grep -q .; then
  sudo fallocate -l 2G /swapfile || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
  sudo chmod 600 /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
  echo "2 GB swap qo'shildi ✓"
else
  echo "RAM ${MEM_MB} MB — swap kerak emas yoki allaqachon bor ✓"
fi

step "3/7 cloudflared (tekin HTTPS tunnel — Mini App uchun)"
if ! command -v cloudflared >/dev/null; then
  ARCH=$(dpkg --print-architecture)   # amd64 (E2.1.Micro) yoki arm64 (Ampere A1)
  curl -fsSL "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-${ARCH}.deb" -o /tmp/cloudflared.deb
  sudo dpkg -i /tmp/cloudflared.deb
fi
cloudflared --version

step "4/7 Kod (GitHub)"
if [ -d "$APP_DIR/.git" ]; then
  git -C "$APP_DIR" pull --ff-only
else
  git clone "$REPO" "$APP_DIR"
fi
cd "$APP_DIR"
python3 -m venv .venv
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt -q
echo "Kutubxonalar o'rnatildi ✓"

step "5/7 Sozlamalar (.env)"
if [ -f .env ]; then
  echo ".env mavjud — o'zgartirilmadi ✓  (tahrirlash: nano $APP_DIR/.env)"
else
  TOKEN="${BOT_TOKEN:-}"
  while [ -z "$TOKEN" ]; do
    read -rp "Bot tokenini kiriting (@BotFather): " TOKEN </dev/tty
  done
  cp .env.example .env
  sed -i "s|^BOT_TOKEN=.*|BOT_TOKEN=${TOKEN}|" .env
  sed -i "s|^BOT_USERNAME=.*|BOT_USERNAME=Akkbozorbot|" .env
  sed -i "s|^SUPPORT=.*|SUPPORT=<a href=\"tg://user?id=768121418\">Admin</a>|" .env
  sed -i "s|^WEBAPP_URL=.*|WEBAPP_URL=auto|" .env
  sed -i "s|^WEB_HOST=.*|WEB_HOST=127.0.0.1|" .env
  chmod 600 .env
  echo ".env yaratildi ✓"
fi

step "6/7 systemd xizmati (24/7, avtomatik qayta ishga tushish)"
sudo tee /etc/systemd/system/${SERVICE}.service >/dev/null <<EOF
[Unit]
Description=Gamebozor Telegram bot
After=network-online.target
Wants=network-online.target

[Service]
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/.venv/bin/python -m bot
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE} >/dev/null
sudo systemctl restart ${SERVICE}

step "7/7 Kunlik zaxira nusxa (04:00)"
mkdir -p "$HOME/gamebozor-backups"
CRON="0 4 * * * sqlite3 $APP_DIR/gamebozor.db \".backup '$HOME/gamebozor-backups/gb-\$(date +\\%F).db'\" && find $HOME/gamebozor-backups -name 'gb-*.db' -mtime +14 -delete"
( crontab -l 2>/dev/null | grep -v 'gamebozor-backups' ; echo "$CRON" ) | crontab -
echo "Zaxira: $HOME/gamebozor-backups ✓"

sleep 6
echo
if systemctl is-active --quiet ${SERVICE}; then
  echo -e "${G}✅ Gamebozor ishlayapti!${N}"
else
  echo -e "${R}❌ Bot ishga tushmadi — loglarga qarang:${N}"
fi
sudo journalctl -u ${SERVICE} -n 20 --no-pager
cat <<TXT

Foydali buyruqlar:
  Loglar (jonli):      sudo journalctl -u ${SERVICE} -f
  Qayta ishga tushir:  sudo systemctl restart ${SERVICE}
  To'xtatish:          sudo systemctl stop ${SERVICE}
  Yangilash:           bash $APP_DIR/deploy/update.sh
  Sozlamalar:          nano $APP_DIR/.env   (keyin restart)
TXT
