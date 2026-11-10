"""E'lonlar bilan ishlash: so'rovlar, kanalga chiqarish, adminlarga yuborish."""
import logging

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.types import InputMediaPhoto
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import config
from bot.db.models import Listing, User
from bot.keyboards import channel_post_kb, mod_kb
from bot.services.render import render_listing, utcnow

log = logging.getLogger(__name__)


async def user_open_count(session: AsyncSession, user_id: int) -> int:
    stmt = select(func.count(Listing.id)).where(
        Listing.seller_id == user_id, Listing.status.in_(("pending", "active"))
    )
    return await session.scalar(stmt) or 0


async def send_to_moderation(bot: Bot, listing: Listing) -> None:
    text = render_listing(listing, "uz") + f"\n\n👤 Sotuvchi: <a href='tg://user?id={listing.seller_id}'>{listing.seller_id}</a>"
    for admin_id in config.admin_ids:
        try:
            if len(listing.photos) > 1:
                await bot.send_media_group(admin_id, [InputMediaPhoto(media=p) for p in listing.photos])
            await bot.send_photo(admin_id, listing.photos[0], caption=text, reply_markup=mod_kb(listing.id))
        except TelegramAPIError as e:
            log.warning("Admin %s ga yuborilmadi: %s", admin_id, e)


async def publish_to_channel(bot: Bot, session: AsyncSession, listing: Listing) -> None:
    """E'lonni kanalga chiqaradi. Albom bo'lsa — avval rasmlar, keyin tugmali asosiy post."""
    seller = await session.get(User, listing.seller_id)
    caption = render_listing(listing, "uz", for_channel=True, verified=bool(seller and seller.is_verified))
    try:
        msg = await bot.send_photo(config.channel, listing.photos[0], caption=caption,
                                   reply_markup=channel_post_kb(listing.id))
        listing.channel_msg_id = msg.message_id
        await session.commit()
    except TelegramAPIError as e:
        log.error("Kanalga chiqarib bo'lmadi (bot kanalda adminmi?): %s", e)


async def update_channel_post(bot: Bot, session: AsyncSession, listing: Listing) -> None:
    """Sotildi/o'chirildi holatini kanal postida yangilash."""
    if not listing.channel_msg_id:
        return
    try:
        if listing.status == "deleted":
            await bot.delete_message(config.channel, listing.channel_msg_id)
        else:
            caption = render_listing(listing, "uz", for_channel=listing.status == "active")
            await bot.edit_message_caption(chat_id=config.channel, message_id=listing.channel_msg_id,
                                           caption=caption,
                                           reply_markup=channel_post_kb(listing.id) if listing.status == "active" else None)
    except TelegramAPIError as e:
        log.warning("Kanal postini yangilab bo'lmadi: %s", e)


async def approve(bot: Bot, session: AsyncSession, listing: Listing) -> None:
    listing.status = "active"
    listing.approved_at = utcnow()
    await session.commit()
    await publish_to_channel(bot, session, listing)
    from bot.services.alerts import notify_saved_searches  # aylanma importdan qochish
    try:
        await notify_saved_searches(bot, session, listing)
    except Exception as e:  # noqa: BLE001 — bildirishnoma xatosi tasdiqlashni buzmasin
        log.exception("Obunalarga yuborishda xato: %s", e)
