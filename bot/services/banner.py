"""🖼 Kanal posti uchun avtomatik banner (1280×720, JPEG).

Chapda: o'yin, sarlavha, asosiy ko'rsatkichlar (TS, Epic ...), yulduz o'yinchilar, narx.
O'ngda: sotuvchining birinchi skrinshoti. Holatlar: 🔥 TOP, ✅ tasdiqlangan, ⭐️ reyting, 📉 eski narx, SOTILDI muhri.

Shrift: BANNER_FONT / BANNER_FONT_BOLD (.env) yoki tizim shriftlari (DejaVu — Linux, Segoe/Arial — Windows).
Ubuntu serverda: `sudo apt install fonts-dejavu-core`.
"""
from __future__ import annotations

import asyncio
import io
import logging
import os
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from bot.db.models import Listing
from bot.services.games import GAMES, short_label
from bot.services.render import fmt_price, is_top

log = logging.getLogger(__name__)

W, H = 1280, 720
BG_TOP, BG_BOTTOM = (16, 18, 28), (38, 24, 74)
ACCENT, HOT, OK, MUTED, WHITE = (124, 92, 255), (255, 106, 54), (34, 197, 94), (160, 168, 190), (244, 246, 252)

_REGULAR = [os.getenv("BANNER_FONT", ""), "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf", "DejaVuSans.ttf", "arial.ttf"]
_BOLD = [os.getenv("BANNER_FONT_BOLD", ""), "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
         "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf", "DejaVuSans-Bold.ttf", "arialbd.ttf"]


@lru_cache(maxsize=64)
def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    for path in (_BOLD if bold else _REGULAR):
        if not path:
            continue
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default(size=size)


def _gradient() -> Image.Image:
    img = Image.new("RGB", (W, H), BG_TOP)
    px = ImageDraw.Draw(img)
    for y in range(H):
        k = y / (H - 1)
        px.line([(0, y), (W, y)], fill=tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * k) for i in range(3)))
    # yumshoq rangli dog'lar
    glow = Image.new("RGB", (W, H), (0, 0, 0))
    g = ImageDraw.Draw(glow)
    g.ellipse((-200, -260, 520, 380), fill=(90, 60, 220))
    g.ellipse((900, 420, 1500, 1000), fill=(200, 70, 40))
    glow = glow.filter(ImageFilter.GaussianBlur(140))
    return Image.blend(img, Image.composite(glow, img, Image.new("L", (W, H), 255)), 0.35)


def _text_w(draw: ImageDraw.ImageDraw, text: str, f) -> int:
    return int(draw.textlength(text, font=f))


def _wrap(draw: ImageDraw.ImageDraw, text: str, f, max_w: int, max_lines: int) -> list[str]:
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = f"{cur} {w}".strip()
        if _text_w(draw, test, f) <= max_w:
            cur = test
            continue
        if cur:
            lines.append(cur)
        cur = w
        if len(lines) == max_lines:
            break
    if cur and len(lines) < max_lines:
        lines.append(cur)
    if len(lines) == max_lines and " ".join(lines) != text.strip():
        last = lines[-1]
        while last and _text_w(draw, last + "…", f) > max_w:
            last = last[:-1]
        lines[-1] = last.rstrip() + "…"
    return lines


def _pill(draw, xy, text, f, fill, color=WHITE, pad=(16, 8)):
    x, y = xy
    tw = _text_w(draw, text, f)
    h = f.size + pad[1] * 2
    draw.rounded_rectangle((x, y, x + tw + pad[0] * 2, y + h), radius=h // 2, fill=fill)
    draw.text((x + pad[0], y + pad[1] - 2), text, font=f, fill=color)
    return x + tw + pad[0] * 2


def _thumb(photo: bytes | None, size: tuple[int, int]) -> Image.Image | None:
    if not photo:
        return None
    try:
        im = Image.open(io.BytesIO(photo)).convert("RGB")
    except Exception:  # noqa: BLE001 — buzuq rasm bo'lsa bannerni rasmsiz chizamiz
        return None
    im = ImageOps.fit(im, size, Image.LANCZOS, centering=(0.5, 0.4))
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, *size), radius=28, fill=255)
    im.putalpha(mask)
    return im


def render_banner(listing: Listing, photo: bytes | None = None, verified: bool = False,
                  rating: tuple[float, int] | None = None, pro: bool = False) -> bytes:
    game = GAMES.get(listing.game)
    img = _gradient()  # RGB: Draw(img, "RGBA") shaffof ranglarni aralashtiradi
    d = ImageDraw.Draw(img, "RGBA")
    left, right_x = 64, 700
    max_w = right_x - left - 40

    # --- O'ng: skrinshot ---
    thumb = _thumb(photo, (520, 600))
    tx, ty = right_x + 4, 60
    if thumb:
        shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(shadow).rounded_rectangle((tx + 10, ty + 18, tx + 530, ty + 618), radius=28, fill=(0, 0, 0, 140))
        img = Image.alpha_composite(img.convert("RGBA"), shadow.filter(ImageFilter.GaussianBlur(18))).convert("RGB")
        img.paste(thumb, (tx, ty), thumb)
        d = ImageDraw.Draw(img, "RGBA")
    else:
        d.rounded_rectangle((tx, ty, tx + 520, ty + 600), radius=28, outline=(255, 255, 255, 60), width=3)
        name = game.name if game else listing.game
        f = font(54, True)
        d.text((tx + 260 - _text_w(d, name, f) // 2, ty + 270), name, font=f, fill=(255, 255, 255, 120))

    # --- Chap: brend va o'yin ---
    d.text((left, 52), "GAMEBOZOR", font=font(26, True), fill=ACCENT)
    x = _pill(d, (left, 96), (game.name if game else listing.game).upper(), font(22, True), (255, 255, 255, 38))
    x = _pill(d, (x + 10, 96), f"#{listing.id}", font(22, True), (255, 255, 255, 38))
    if is_top(listing) and listing.status == "active":
        _pill(d, (x + 10, 96), "TOP", font(22, True), HOT)

    # --- Sarlavha ---
    y = 160
    for line in _wrap(d, listing.title, font(46, True), max_w, 2):
        d.text((left, y), line, font=font(46, True), fill=WHITE)
        y += 58
    y += 16

    # --- Ko'rsatkichlar (2×2 kartochka) ---
    data = listing.data or {}
    stats = []
    if game:
        for fld in game.fields:
            v = data.get(fld.key)
            if isinstance(v, int) and fld.type == "int":
                stats.append((short_label(fld, "uz"), fmt_price(v)))
            elif fld.filter == "choice" and fld.key in ("rank", "division") and v:
                stats.append((short_label(fld, "uz"), str(v).split(" / ")[0]))
    stats = stats[:4]
    bw, bh, gap = (max_w - 16) // 2, 92, 16
    for i, (label, value) in enumerate(stats):
        bx, by = left + (i % 2) * (bw + gap), y + (i // 2) * (bh + gap)
        d.rounded_rectangle((bx, by, bx + bw, by + bh), radius=18, fill=(255, 255, 255, 26))
        d.text((bx + 18, by + 12), label.upper(), font=font(18, True), fill=MUTED)
        vf = font(36, True)
        while _text_w(d, value, vf) > bw - 36 and vf.size > 20:
            vf = font(vf.size - 2, True)
        d.text((bx + 18, by + 40), value, font=vf, fill=WHITE)
    y += ((len(stats) + 1) // 2) * (bh + gap) + (6 if stats else 0)

    # --- Narx joyi (pastdan) ---
    pf = font(72, True)
    price = fmt_price(listing.price)
    is_topup = bool(game and game.kind == "topup")
    py = H - 150
    dropped = bool(listing.old_price and listing.old_price > listing.price and listing.status == "active")
    limit = py - (58 if dropped else 12)  # matn shu chiziqdan pastga tushmasin

    # --- Yulduz o'yinchilar / qurollar ---
    star_key = next((k for k in ("top_players", "upgr_guns", "knives", "packs") if data.get(k)), None)
    if star_key:
        n = max(0, min(2, (limit - y) // 32))
        for line in (_wrap(d, str(data[star_key]), font(24), max_w, n) if n else []):
            d.text((left, y), line, font=font(24), fill=(220, 224, 240))
            y += 32

    if dropped:
        of = font(30, True)
        old = fmt_price(listing.old_price)
        d.text((left, py - 40), old, font=of, fill=MUTED)
        ow = _text_w(d, old, of)
        d.line((left, py - 22, left + ow, py - 22), fill=HOT, width=3)
        _pill(d, (left + ow + 14, py - 44), "NARX TUSHDI", font(18, True), HOT)
    d.text((left, py), price, font=pf, fill=WHITE)
    tail = "so'mdan" if is_topup else "so'm" + ("  · kelishiladi" if listing.negotiable else "")
    d.text((left + _text_w(d, price, pf) + 16, py + 34), tail, font=font(28, True), fill=ACCENT)

    # --- Sotuvchi belgilari ---
    bx = left
    by = H - 56
    if pro:
        bx = _pill(d, (bx, by), "PRO", font(18, True), ACCENT) + 10
    if verified:
        bx = _pill(d, (bx, by), "TASDIQLANGAN SOTUVCHI", font(18, True), OK) + 10
    if rating:
        _pill(d, (bx, by), f"REYTING {rating[0]:.1f} / 5  ({rating[1]})", font(18, True), (255, 255, 255, 38))

    # --- SOTILDI muhri ---
    if listing.status == "sold":
        overlay = Image.new("RGBA", (W, H), (10, 10, 14, 150))
        img = Image.alpha_composite(img.convert("RGBA"), overlay)
        stamp = Image.new("RGBA", (760, 180), (0, 0, 0, 0))
        sd = ImageDraw.Draw(stamp)
        sd.rounded_rectangle((6, 6, 754, 174), radius=26, outline=(255, 70, 70, 255), width=10)
        sf = font(96, True)
        txt = "SOTILDI"
        sd.text((380 - _text_w(sd, txt, sf) // 2, 30), txt, font=sf, fill=(255, 70, 70, 255))
        stamp = stamp.rotate(12, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(stamp, ((W - stamp.width) // 2, (H - stamp.height) // 2))

    out = io.BytesIO()
    img.convert("RGB").save(out, "JPEG", quality=90, optimize=True)
    return out.getvalue()


async def make_banner(bot, session, listing: Listing) -> bytes | None:
    """Skrinshotni Telegram'dan yuklab, bannerni alohida oqimda chizadi. Xato bo'lsa None."""
    from bot.services.reputation import seller_info

    try:
        info = await seller_info(session, listing.seller_id)
        photo = None
        if listing.photos:
            try:
                buf = await bot.download(listing.photos[0])
                photo = buf.read() if buf else None
            except Exception as e:  # noqa: BLE001
                log.info("Skrinshotni yuklab bo'lmadi: %s", e)
        return await asyncio.to_thread(render_banner, listing, photo, info.verified, info.rating, info.pro)
    except Exception as e:  # noqa: BLE001 — banner ixtiyoriy, kanal posti baribir chiqishi kerak
        log.exception("Banner chizilmadi: %s", e)
        return None
