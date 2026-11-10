#!/usr/bin/env bash
# Gamebozor — serverda yangilash: kodni tortib olish, kutubxonalar, qayta ishga tushirish.
#   bash ~/gamebozor/deploy/update.sh
set -euo pipefail
APP_DIR="$HOME/gamebozor"
cd "$APP_DIR"

echo "==> Zaxira nusxa (yangilashdan oldin)"
mkdir -p "$HOME/gamebozor-backups"
[ -f gamebozor.db ] && sqlite3 gamebozor.db ".backup '$HOME/gamebozor-backups/gb-before-update-$(date +%F-%H%M).db'"

echo "==> git pull"
git pull --ff-only

echo "==> Kutubxonalar"
.venv/bin/pip install -r requirements.txt -q

echo "==> Qayta ishga tushirish"
sudo systemctl restart gamebozor
sleep 5
systemctl is-active --quiet gamebozor && echo "✅ Ishlayapti" || echo "❌ Ishlamayapti — loglarga qarang"
sudo journalctl -u gamebozor -n 15 --no-pager
