"""💎 PRO sotuvchi tarifi.

Imkoniyatlar: ko'proq faol e'lon, har N soatda avtomatik ko'tarish (bumped_at), har xaridga 1 bepul TOP,
«PRO» belgisi, moderatsiyada ustuvorlik. To'lov — Telegram Stars (raqamli xizmat).

Fon jarayoni (pro_worker) har 30 daqiqada:
  • PRO sotuvchilarning faol e'lonlarini ko'taradi;
  • muddat tugashidan 3 kun oldin eslatadi;
  • muddat tugaganda xabar beradi.
"""
import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import config
from bot.db.models import Listing, User
from bot.i18n import t
from bot.services.render import utcnow

log = logging.getLogger(__name__)
TZ_SHIFT = timedelta(hours=5)  # Toshkent vaqti


def is_pro(user: User | None, now: datetime | None = None) -> bool:
    return bool(user and user.pro_until and user.pro_until > (now or utcnow()))


def listing_limit(user: User) -> int:
    return config.pro_listing_limit if is_pro(user) else config.free_listing_limit


def fmt_date(dt: datetime) -> str:
    return (dt + TZ_SHIFT).strftime("%d.%m.%Y")


def status_text(user: User, lang: str) -> str:
    if is_pro(user):
        return t(lang, "pro_status_on", until=fmt_date(user.pro_until), credits=user.pro_top_credits or 0)
    return t(lang, "pro_status_off")


def pro_screen(user: User, lang: str) -> str:
    return t(lang, "pro_screen", status=status_text(user, lang), limit=config.pro_listing_limit,
             free=config.free_listing_limit, hours=config.pro_bump_hours,
             p30=config.pro_30d_stars, p90=config.pro_90d_stars)


def activate(user: User, days: int, top_credits: int = 1) -> None:
    """Muddatni qo'shadi (faol bo'lsa — uzaytiradi) va bepul TOP beradi. Commit chaqiruvchida."""
    now = utcnow()
    base = user.pro_until if is_pro(user, now) else now
    user.pro_until = base + timedelta(days=days)
    user.pro_top_credits = (user.pro_top_credits or 0) + top_credits
    user.pro_reminded = False


async def bump_pro_listings(session: AsyncSession) -> int:
    now = utcnow()
    edge = now - timedelta(hours=config.pro_bump_hours)
    pro_ids = select(User.id).where(User.pro_until > now)
    res = await session.execute(
        update(Listing)
        .where(Listing.status == "active", Listing.seller_id.in_(pro_ids),
               or_(Listing.bumped_at == None, Listing.bumped_at < edge),  # noqa: E711
               Listing.approved_at < edge)
        .values(bumped_at=now))
    await session.commit()
    return res.rowcount or 0


async def _send(bot: Bot, uid: int, text: str) -> None:
    try:
        await bot.send_message(uid, text)
    except TelegramAPIError:
        pass


async def remind_and_expire(bot: Bot, session: AsyncSession) -> None:
    now = utcnow()
    soon = (await session.execute(select(User).where(
        User.pro_until > now, User.pro_until <= now + timedelta(days=3),
        or_(User.pro_reminded == None, User.pro_reminded == False)))).scalars().all()  # noqa: E711,E712
    for u in soon:
        u.pro_reminded = True
        await _send(bot, u.id, t(u.lang, "pro_reminder", until=fmt_date(u.pro_until)))
    expired = (await session.execute(select(User).where(User.pro_until <= now))).scalars().all()
    for u in expired:
        u.pro_until = None
        u.pro_reminded = None
        await _send(bot, u.id, t(u.lang, "pro_expired", free=config.free_listing_limit))
    await session.commit()


async def pro_worker(bot: Bot, interval: int = 1800) -> None:
    from bot.db.base import Session

    while True:
        try:
            async with Session() as session:
                n = await bump_pro_listings(session)
                await remind_and_expire(bot, session)
            if n:
                log.info("PRO: %s ta e'lon ko'tarildi", n)
        except Exception as e:  # noqa: BLE001 — fon jarayoni to'xtab qolmasin
            log.exception("PRO worker xatosi: %s", e)
        await asyncio.sleep(interval)
