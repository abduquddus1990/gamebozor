"""E'lon kartochkasi matnini yasash (bot va kanal uchun)."""
from datetime import datetime, timezone
from html import escape

from bot.db.models import Listing
from bot.i18n import t
from bot.services.games import GAMES

CAPTION_LIMIT = 1024  # Telegram rasm izohi limiti


def fmt_price(n: int) -> str:
    return f"{n:,}".replace(",", " ")


def fmt_short(n: int) -> str:
    """Tugmalar uchun ixcham son: 1500000 → 1.5M, 300000 → 300K, 3250 → 3250."""
    if n >= 1_000_000:
        v = n / 1_000_000
        return (f"{v:.1f}".rstrip("0").rstrip(".")) + "M"
    if n >= 100_000:
        return f"{n // 1000}K"
    return str(n)


def utcnow() -> datetime:
    """UTC vaqt (naive) — bazada shunday saqlanadi."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def is_top(listing: Listing) -> bool:
    return bool(listing.top_until and listing.top_until > utcnow())


def render_listing(listing: Listing, lang: str = "uz", for_channel: bool = False, verified: bool = False,
                   rating: tuple[float, int] | None = None, pro: bool = False) -> str:
    game = GAMES.get(listing.game)
    ru = lang == "ru"
    lines: list[str] = []

    if listing.status == "sold":
        lines.append("✅ <b>SOTILDI / ПРОДАНО</b>\n")
    elif is_top(listing):
        lines.append("🔥 <b>TOP</b>")

    head = f"{game.emoji} {game.name}" if game else listing.game
    lines.append(f"{head} | <b>#{listing.id}</b>")
    lines.append(f"<b>{escape(listing.title, quote=False)}</b>\n")

    if game:
        for f in game.fields:
            val = (listing.data or {}).get(f.key)
            if val in (None, ""):
                continue
            label = f.label(lang).split(" (")[0].rstrip("?")
            shown = fmt_price(val) if isinstance(val, int) else escape(str(val), quote=False)
            sep = ":\n" if "\n" in shown else ": "
            lines.append(f"{f.icon} {label}{sep}<b>{shown}</b>")

    price = fmt_price(listing.price)
    som = "сум" if ru else "so'm"
    if game and game.kind == "topup":
        price_line = f"{t(lang, 'from_price')} {price} {som}" if ru else f"{price} {som} {t(lang, 'from_price')}"
        lines.append(f"\n💵 <b>{price_line}</b>")
        if "Login" in str((listing.data or {}).get("method", "")):
            lines.append(t(lang, "login_warn"))
    else:
        old = ""
        if listing.old_price and listing.old_price > listing.price and listing.status == "active":
            old = f"  <s>{fmt_price(listing.old_price)}</s> 📉"
        lines.append(f"\n💵 <b>{price} {som}</b>" + (" 🤝" if listing.negotiable else "") + old)

    if listing.description:
        lines.append(f"\n📝 {escape(listing.description, quote=False)}")

    seller_bits = []
    if pro:
        seller_bits.append("💎 PRO")
    if verified:
        seller_bits.append("✅ " + ("Проверенный продавец" if ru else "Tasdiqlangan sotuvchi"))
    if rating:
        avg, cnt = rating
        seller_bits.append(f"⭐️ {avg:.1f} ({cnt} " + ("отз." if ru else "sharh") + ")")
    if seller_bits:
        lines.append("\n" + " · ".join(seller_bits))

    if for_channel:
        lines.append("\n👇 Batafsil va sotuvchi bilan aloqa — botda / Подробнее — в боте")

    text = "\n".join(lines)
    if len(text) > CAPTION_LIMIT:
        # izohni qisqartiramiz, qolgani sig'ishi kerak
        overflow = len(text) - CAPTION_LIMIT + 3
        desc = escape(listing.description, quote=False)
        if listing.description and len(desc) > overflow:
            text = text.replace(f"📝 {desc}", f"📝 {desc[:-overflow]}…")
        text = text[:CAPTION_LIMIT]
    return text
