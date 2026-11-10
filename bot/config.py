"""Loyiha sozlamalari (.env fayldan o'qiladi)."""
import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()


def _ids(raw: str) -> list[int]:
    return [int(x) for x in raw.replace(" ", "").split(",") if x]


@dataclass(frozen=True)
class Config:
    bot_token: str = os.getenv("BOT_TOKEN", "")
    bot_username: str = os.getenv("BOT_USERNAME", "akkbozorbot")
    channel: str = os.getenv("CHANNEL", "@eakkbozor")
    admin_ids: list[int] = field(default_factory=lambda: _ids(os.getenv("ADMIN_IDS", "")))
    support: str = os.getenv("SUPPORT", "@admin")  # to'lov/yordam uchun admin username
    database_url: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///gamebozor.db")

    # Tekin tarif: bir vaqtda nechta faol/moderatsiyadagi e'lon
    free_listing_limit: int = int(os.getenv("FREE_LISTING_LIMIT", "3"))

    # TOP e'lon narxlari (Telegram Stars, XTR)
    top_3d_stars: int = int(os.getenv("TOP_3D_STARS", "50"))
    top_7d_stars: int = int(os.getenv("TOP_7D_STARS", "100"))

    max_photos: int = 10

    # Mini App (vitrina). Bo'sh bo'lsa — o'chiq. HTTPS manzil kerak (masalan Cloudflare Tunnel).
    webapp_url: str = os.getenv("WEBAPP_URL", "").rstrip("/")
    web_host: str = os.getenv("WEB_HOST", "0.0.0.0")
    web_port: int = int(os.getenv("WEB_PORT", "8080"))

    # Saqlangan qidiruvlar (bildirishnoma) — bitta foydalanuvchiga nechta
    max_alerts: int = int(os.getenv("MAX_ALERTS", "5"))


config = Config()
