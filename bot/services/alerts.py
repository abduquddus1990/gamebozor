"""🔔 Saqlangan qidiruvlar: yangi e'lon tasdiqlanganda mos obunachilarga xabar."""
import asyncio
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Listing, SavedSearch, User
from bot.i18n import t
from bot.keyboards import open_listing_kb
from bot.services.games import GAMES, short_label
from bot.services.render import fmt_price, fmt_short
from bot.services.search import clean, matches

log = logging.getLogger(__name__)


def describe(f: dict, lang: str) -> str:
    """Filtrni bir qatorli matnga aylantiradi: «⚽️ eFootball · 💵 500K–2M · TS ≥3000 · «messi»»."""
    f = clean(f)
    game = GAMES.get(f["g"])
    parts = [f"{game.emoji} {game.name}" if game else ("🎮 " + t(lang, "search_any_game"))]
    lo, hi = f.get("pmin"), f.get("pmax")
    if lo or hi:
        parts.append("💵 " + (f"{fmt_short(lo)}–{fmt_short(hi)}" if lo and hi else
                             f"≥{fmt_short(lo)}" if lo else f"≤{fmt_short(hi)}"))
    if game:
        for fld in game.filter_fields:
            if fld.key in f["min"]:
                parts.append(f"{fld.icon}{short_label(fld, lang)} ≥{fmt_short(int(f['min'][fld.key]))}")
            elif fld.key in f["ch"]:
                parts.append(f"{fld.icon}{str(f['ch'][fld.key]).split(' / ')[0]}")
            elif fld.key in f["tx"]:
                parts.append(f"{fld.icon}«{f['tx'][fld.key]}»")
    if f.get("q"):
        parts.append(f"🔤«{f['q']}»")
    if f.get("ver"):
        parts.append("✅")
    return " · ".join(parts)


def listing_line(listing: Listing, lang: str) -> str:
    game = GAMES.get(listing.game)
    head = f"{game.emoji} {game.name}" if game else listing.game
    som = "сум" if lang == "ru" else "so'm"
    return f"{head} #{listing.id} · <b>{fmt_price(listing.price)} {som}</b>\n{listing.title}"


async def notify_saved_searches(bot: Bot, session: AsyncSession, listing: Listing) -> int:
    seller = await session.get(User, listing.seller_id)
    verified = bool(seller and seller.is_verified)
    rows = (await session.execute(select(SavedSearch, User.lang).join(User, User.id == SavedSearch.user_id)
                                  .where(SavedSearch.user_id != listing.seller_id, User.is_banned == False)  # noqa: E712
                                  )).all()
    notified: set[int] = set()
    for ss, lang in rows:
        if ss.user_id in notified or not matches(listing, clean(ss.filters), verified):
            continue
        notified.add(ss.user_id)
        lang = lang or "uz"
        text = t(lang, "alert_hit", summary=listing_line(listing, lang)) + f"\n\n🔔 {describe(ss.filters, lang)}"
        try:
            await bot.send_message(ss.user_id, text, reply_markup=open_listing_kb(lang, listing.id))
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except TelegramAPIError as e:
            log.info("Obuna xabari yuborilmadi %s: %s", ss.user_id, e)
        await asyncio.sleep(0.05)
    return len(notified)


async def notify_price_drop(bot: Bot, session: AsyncSession, listing: Listing, old_price: int) -> int:
    """📉 Narx tushdi: (1) e'lonni saralaganlarga, (2) eski narxda mos kelmagan, endi mos kelgan obunalarga."""
    from bot.db.models import Favorite

    sent: set[int] = {listing.seller_id}
    fav_rows = (await session.execute(
        select(Favorite.user_id, User.lang).join(User, User.id == Favorite.user_id)
        .where(Favorite.listing_id == listing.id, User.is_banned == False))).all()  # noqa: E712
    for uid, lang in fav_rows:
        if uid in sent:
            continue
        sent.add(uid)
        lang = lang or "uz"
        text = t(lang, "price_drop_hit", summary=listing_line(listing, lang),
                 old=fmt_price(old_price), new=fmt_price(listing.price))
        try:
            await bot.send_message(uid, text, reply_markup=open_listing_kb(lang, listing.id))
        except TelegramAPIError:
            pass
        await asyncio.sleep(0.05)

    # Obunalar: faqat yangi narx tufayli mos kelib qolganlar (avval xabar olmaganlar)
    seller = await session.get(User, listing.seller_id)
    verified = bool(seller and seller.is_verified)
    current = listing.price
    rows = (await session.execute(select(SavedSearch, User.lang).join(User, User.id == SavedSearch.user_id)
                                  .where(User.is_banned == False))).all()  # noqa: E712
    for ss, lang in rows:
        if ss.user_id in sent:
            continue
        f = clean(ss.filters)
        listing.price = old_price
        matched_before = matches(listing, f, verified)
        listing.price = current
        if matched_before or not matches(listing, f, verified):
            continue
        sent.add(ss.user_id)
        lang = lang or "uz"
        text = t(lang, "alert_hit", summary=listing_line(listing, lang)) + f"\n📉 <s>{fmt_price(old_price)}</s>\n\n🔔 {describe(ss.filters, lang)}"
        try:
            await bot.send_message(ss.user_id, text, reply_markup=open_listing_kb(lang, listing.id))
        except TelegramAPIError:
            pass
        await asyncio.sleep(0.05)
    return len(sent) - 1
