"""Kengaytirilgan qidiruv.

Filtrlar — oddiy dict (JSON), foydalanuvchi bazasida (User.search) saqlanadi, shuning uchun
bot qayta ishga tushsa ham yo'qolmaydi. Saqlangan qidiruvlar (🔔) ham xuddi shu formatda.

    {
      "k":    "account" | "topup",      # bo'lim
      "g":    "efootball" | "",          # o'yin ("" — bo'limdagi barcha o'yinlar)
      "q":    "messi 103",               # erkin matn: sarlavha, izoh, o'yinchilar, packlar...
      "pmin": 500000, "pmax": 2000000,   # narx oralig'i (so'm)
      "min":  {"team_strength": 3000},   # "kamida" filtrlari
      "ch":   {"platform": "Android"},   # tanlov filtrlari
      "tx":   {"top_players": "mbappe"}, # maydon ichidan matn
      "ver":  true,                      # faqat ✅ tasdiqlangan sotuvchilar
      "sort": "top" | "new" | "cheap" | "exp" | "strong"
    }

SQL faqat oddiy shartlarni (holat, o'yin, narx, tasdiq) bajaradi; JSON maydonlar Python'da
filtrlanadi — SQLite va PostgreSQL'da bir xil ishlaydi. Minglab e'longacha bemalol yetadi;
undan oshsa PostgreSQL JSONB indekslariga o'tkaziladi.
"""
from __future__ import annotations

import re
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Listing, User
from bot.services.games import GAMES, Game, active_games
from bot.services.render import utcnow

SORTS = ("top", "new", "cheap", "exp", "strong")
MAX_RESULTS = 2000

_APOS = re.compile(r"[ʻʼ’‘`´]")


def norm(s: str) -> str:
    return _APOS.sub("'", str(s)).lower().strip()


def empty_filters(kind: str = "account", game: str = "") -> dict:
    if not game:
        games = active_games(kind)
        game = games[0].code if len(games) == 1 else ""
    return {"k": kind, "g": game, "q": "", "pmin": None, "pmax": None,
            "min": {}, "ch": {}, "tx": {}, "ver": False, "sort": "top"}


def clean(f: dict | None) -> dict:
    """Bazadan kelgan (yoki eski) filtrni to'liq shaklga keltiradi."""
    base = empty_filters((f or {}).get("k", "account"), (f or {}).get("g", ""))
    if f:
        base.update({k: v for k, v in f.items() if k in base})
    for k in ("min", "ch", "tx"):
        if not isinstance(base[k], dict):
            base[k] = {}
    if base["sort"] not in SORTS:
        base["sort"] = "top"
    # O'yin almashtirilsa — o'sha o'yinda yo'q maydonlar filtrini tashlaymiz
    game = GAMES.get(base["g"])
    keys = {fl.key for fl in game.filter_fields} if game else set()
    for k in ("min", "ch", "tx"):
        base[k] = {key: v for key, v in base[k].items() if key in keys and v not in (None, "", 0)}
    return base


def active_count(f: dict) -> int:
    """Nechta filtr qo'llanilgan (badge uchun)."""
    n = sum(1 for k in ("q",) if f.get(k))
    n += 1 if f.get("pmin") or f.get("pmax") else 0
    n += len(f.get("min", {})) + len(f.get("ch", {})) + len(f.get("tx", {}))
    n += 1 if f.get("ver") else 0
    return n


# ---------- Narx oralig'ini matndan o'qish ----------
_NUM = re.compile(r"(\d+(?:[.,]\d+)?)\s*(mlrd|млрд|mln|млн|ming|минг|тыс|m|м|k|к)?", re.I)
_MULT = {"mlrd": 10**9, "млрд": 10**9, "mln": 10**6, "млн": 10**6, "m": 10**6, "м": 10**6,
         "ming": 1000, "минг": 1000, "тыс": 1000, "k": 1000, "к": 1000}


def _parse_amount(num: str, unit: str | None) -> int:
    value = float(num.replace(",", "."))
    return int(value * _MULT.get((unit or "").lower(), 1))


def parse_price_range(text: str) -> tuple[int | None, int | None] | None:
    """'500000-2000000', '500k - 2mln', '1.5 mln gacha', 'от 300 тыс', '>1mln' ...

    Bitta son bo'lsa: 'gacha/до/<' → maksimum, aks holda minimum.
    """
    raw = norm(text).replace(" ", "")
    found = _NUM.findall(raw)
    if not found:
        return None
    nums = [_parse_amount(n, u) for n, u in found]
    if len(nums) >= 2:
        lo, hi = sorted(nums[:2])
        return lo, hi
    n = nums[0]
    if any(w in raw for w in ("gacha", "до", "<", "max", "макс")):
        return None, n
    return n, None


# ---------- Moslik ----------
def _choice_ok(value, wanted: str) -> bool:
    if value in (None, ""):
        return False
    v = norm(value)
    w = norm(wanted)
    if v == w:
        return True
    # "Android + iOS" e'loni "Android" filtriga ham mos; "Ha / Да" → "ha"
    parts = {p.strip() for p in re.split(r"\s*[+/]\s*", v)}
    return w in parts or any(p == w for p in re.split(r"\s*[+/]\s*", w) if p and p in parts)


def haystack(listing: Listing) -> str:
    data = listing.data or {}
    vals = [listing.title or "", listing.description or "", f"#{listing.id}"]
    vals += [str(v) for v in data.values() if v not in (None, "")]
    game = GAMES.get(listing.game)
    if game:
        vals.append(game.name)
    return norm(" | ".join(vals))


def matches(listing: Listing, f: dict, seller_verified: bool = False) -> bool:
    if listing.status != "active":
        return False
    if f.get("g"):
        if listing.game != f["g"]:
            return False
    else:
        game = GAMES.get(listing.game)
        if not game or game.kind != f.get("k", "account"):
            return False
    if f.get("pmin") and listing.price < f["pmin"]:
        return False
    if f.get("pmax") and listing.price > f["pmax"]:
        return False
    if f.get("ver") and not seller_verified:
        return False
    data = listing.data or {}
    for key, n in (f.get("min") or {}).items():
        v = data.get(key)
        if not isinstance(v, int) or v < int(n):
            return False
    for key, wanted in (f.get("ch") or {}).items():
        if not _choice_ok(data.get(key), wanted):
            return False
    for key, sub in (f.get("tx") or {}).items():
        tokens = norm(sub).split()
        val = norm(data.get(key, ""))
        if not all(tok in val for tok in tokens):
            return False
    if f.get("q"):
        hay = haystack(listing)
        if not all(tok in hay for tok in norm(f["q"]).lstrip("#").split()):
            return False
    return True


def _strength_key(game: Game | None):
    """'Eng kuchli' saralash uchun asosiy ko'rsatkich: o'yinning birinchi "min" maydoni."""
    fld = next((x for x in game.filter_fields if x.filter == "min"), None) if game else None
    return fld.key if fld else None


async def search(session: AsyncSession, f: dict) -> list[Listing]:
    f = clean(f)
    stmt = select(Listing, User.is_verified).join(User, User.id == Listing.seller_id).where(Listing.status == "active")
    if f["g"]:
        stmt = stmt.where(Listing.game == f["g"])
    else:
        codes = [g.code for g in GAMES.values() if g.kind == f["k"]]
        stmt = stmt.where(Listing.game.in_(codes))
    if f.get("pmin"):
        stmt = stmt.where(Listing.price >= f["pmin"])
    if f.get("pmax"):
        stmt = stmt.where(Listing.price <= f["pmax"])
    if f.get("ver"):
        stmt = stmt.where(User.is_verified == True)  # noqa: E712
    stmt = stmt.order_by(Listing.id.desc()).limit(MAX_RESULTS)
    rows = (await session.execute(stmt)).all()
    result = [l for l, ver in rows if matches(l, f, bool(ver))]
    return sort_listings(result, f)


def sort_listings(items: list[Listing], f: dict) -> list[Listing]:
    now = utcnow()

    def is_top(l: Listing) -> int:
        return 0 if (l.top_until and l.top_until > now) else 1

    def newest(l: Listing):
        # PRO avto-ko'tarilgan e'lon «yangi» kabi yuqoriga chiqadi
        seen = max(d for d in (l.approved_at, l.bumped_at, l.created_at, datetime.min) if d)
        return (seen, l.id)

    sort = f.get("sort", "top")
    if sort == "cheap":
        return sorted(items, key=lambda l: (l.price, -l.id))
    if sort == "exp":
        return sorted(items, key=lambda l: (-l.price, -l.id))
    if sort == "new":
        return sorted(items, key=newest, reverse=True)
    if sort == "strong":
        key = _strength_key(GAMES.get(f.get("g", "")))
        if key:
            return sorted(items, key=lambda l: -int((l.data or {}).get(key) or 0))
    # top: TOP e'lonlar birinchi, keyin eng yangilari
    items = sorted(items, key=newest, reverse=True)
    return sorted(items, key=is_top)


async def market_stats(session: AsyncSession, game_code: str) -> dict:
    """O'yin bo'limi uchun bozor ko'rsatkichlari: soni, narx min/o'rta/max, eng kuchli."""
    rows = (await session.execute(
        select(Listing).where(Listing.status == "active", Listing.game == game_code))).scalars().all()
    sold = (await session.execute(
        select(Listing.id).where(Listing.status == "sold", Listing.game == game_code))).all()
    stats = {"count": len(rows), "sold": len(sold), "min": 0, "avg": 0, "max": 0, "best": None, "new24": 0}
    if rows:
        prices = sorted(l.price for l in rows)
        stats.update(min=prices[0], max=prices[-1], avg=int(sum(prices) / len(prices)),
                     median=prices[len(prices) // 2])
        key = _strength_key(GAMES.get(game_code))
        if key:
            vals = [(l.data or {}).get(key) for l in rows]
            vals = [v for v in vals if isinstance(v, int)]
            stats["best"] = max(vals) if vals else None
        now = utcnow()
        stats["new24"] = sum(1 for l in rows if l.approved_at and (now - l.approved_at).total_seconds() < 86400)
    return stats
