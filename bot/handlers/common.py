"""Handlerlar uchun umumiy yordamchilar."""
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InputMediaPhoto, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Favorite, Listing, User
from bot.i18n import t
from bot.keyboards import card_kb, rules_kb


async def show_screen(event: Message | CallbackQuery, text: str, kb: InlineKeyboardMarkup | None) -> Message | None:
    """Dashboard ekrani: callback bo'lsa — o'sha xabarni tahrirlaymiz (chat toza qoladi),
    rasmli xabar bo'lsa yoki xabar bo'lsa — yangisini yuboramiz."""
    if isinstance(event, CallbackQuery):
        msg = event.message
        if msg and msg.text is not None:
            try:
                return await msg.edit_text(text, reply_markup=kb, disable_web_page_preview=True)
            except TelegramBadRequest as e:
                if "not modified" in str(e):
                    return msg
        if msg:
            try:
                await msg.delete()
            except TelegramBadRequest:
                pass
            return await msg.answer(text, reply_markup=kb, disable_web_page_preview=True)
        return None
    return await event.answer(text, reply_markup=kb, disable_web_page_preview=True)


async def require_rules(event: Message | CallbackQuery, user: User, lang: str) -> bool:
    """Qoidalarga rozilik bo'lmasa — qoidalarni rozilik tugmasi bilan ko'rsatadi va False qaytaradi."""
    if user.rules_accepted_at:
        return True
    target = event.message if isinstance(event, CallbackQuery) else event
    if isinstance(event, CallbackQuery):
        await event.answer(t(lang, "need_rules"), show_alert=True)
    else:
        await target.answer(t(lang, "need_rules"))
    await target.answer(t(lang, "rules"), reply_markup=rules_kb(lang, False, back="home"))
    return False


async def is_fav(session: AsyncSession, user_id: int, listing_id: int) -> bool:
    return bool(await session.scalar(
        select(Favorite.id).where(Favorite.user_id == user_id, Favorite.listing_id == listing_id)))


async def seller_verified(session: AsyncSession, listing: Listing) -> bool:
    seller = await session.get(User, listing.seller_id)
    return bool(seller and seller.is_verified)


async def show_single(bot: Bot, chat_id: int, session: AsyncSession, listing_id: int, lang: str,
                      user_id: int) -> bool:
    """Bitta e'lonni albom + kartochka bilan ko'rsatish (deep-link, saralangan, obuna, Mini App)."""
    from bot.services.render import render_listing

    listing = await session.get(Listing, listing_id)
    if not listing or listing.status not in ("active", "sold"):
        await bot.send_message(chat_id, t(lang, "listing_not_found"))
        return False
    listing.views += 1
    await session.commit()
    if len(listing.photos) > 1:
        await bot.send_media_group(chat_id, [InputMediaPhoto(media=p) for p in listing.photos[1:]])
    await bot.send_photo(
        chat_id, listing.photos[0],
        caption=render_listing(listing, lang, verified=await seller_verified(session, listing)),
        reply_markup=card_kb(lang, listing.id, is_fav=await is_fav(session, user_id, listing.id))
        if listing.status == "active" else None,
    )
    return True
