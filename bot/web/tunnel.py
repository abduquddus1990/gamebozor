"""Tekin Cloudflare «Quick Tunnel»: WEBAPP_URL=auto bo'lsa bot o'zi HTTPS manzil oladi.

Talab: `cloudflared` dasturi o'rnatilgan bo'lishi (Windows: `winget install --id Cloudflare.cloudflared`,
Ubuntu: README ga qarang). Akkaunt/domen kerak emas.

Cheklov: manzil har safar bot qayta ishga tushganda o'zgaradi (https://xxxx.trycloudflare.com).
Dashboard va /start dagi tugmalar har doim yangi manzilni oladi; eski pastki menyudagi «📱 Vitrina»
tugmasi foydalanuvchi /start bosganda yangilanadi.
"""
import asyncio
import logging
import os
import re
import shutil
from pathlib import Path

log = logging.getLogger(__name__)
URL_RE = re.compile(r"https://[a-z0-9-]+\.trycloudflare\.com")


def find_cloudflared() -> str | None:
    candidates = [os.getenv("CLOUDFLARED_PATH", ""), shutil.which("cloudflared") or "",
                  str(Path.cwd() / "cloudflared.exe"), str(Path.cwd() / "cloudflared"),
                  r"C:\Program Files (x86)\cloudflared\cloudflared.exe", r"C:\Program Files\cloudflared\cloudflared.exe"]
    return next((c for c in candidates if c and Path(c).is_file()), None)


async def start_quick_tunnel(port: int, timeout: float = 45) -> tuple[asyncio.subprocess.Process, str] | None:
    exe = find_cloudflared()
    if not exe:
        log.error("cloudflared topilmadi — Mini App o'chiq. O'rnating yoki CLOUDFLARED_PATH ni yozing.")
        return None
    proc = await asyncio.create_subprocess_exec(
        exe, "tunnel", "--no-autoupdate", "--url", f"http://localhost:{port}",
        stdout=asyncio.subprocess.DEVNULL, stderr=asyncio.subprocess.PIPE)

    async def read_url() -> str | None:
        while True:
            line = await proc.stderr.readline()
            if not line:
                return None
            m = URL_RE.search(line.decode(errors="ignore"))
            if m:
                return m.group(0)

    try:
        url = await asyncio.wait_for(read_url(), timeout)
    except asyncio.TimeoutError:
        url = None
    if not url:
        log.error("Cloudflare tunnel manzil bermadi — Mini App o'chiq.")
        proc.kill()
        return None

    async def drain() -> None:  # stderr to'lib qolmasin
        while await proc.stderr.readline():
            pass

    asyncio.create_task(drain())
    log.info("Cloudflare tunnel: %s", url)
    return proc, url
