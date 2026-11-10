"""Mening e'lonlarim + TOP (Telegram Stars to'lovi)."""
from datetime import timedelta

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, LabeledPrice, Message, PreCheckoutQuery
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import ItemCb, TopCb
from bot.config import config
from bot.db.models import Listing, Payment, User
from bot.i18n import all_variants, t
from bot.keyboards import my_list_kb, owner_kb, top_kb
from bot.services.listings import publish_to_channel, update_channel_post
from bot.services.render import fmt_price, render_listing, utcnow

router = Router(name="my_listings")

STATUS_ICON = {"pending": "⏳", "active": "🟢", "rejected": "🔴", "sold": "✅"}


@router.message(Command("my"))
@router.message(F.text.in_(all_variants("btn_my")))
async def my_listings(message: Message, state: FSMContext, session: AsyncSession, user: User, lang: str) -> None:
    await state.clear()
    rows = (await session.execute(
        select(Listing).where(Listing.seller_id == user.id, Listing.status != "deleted")
        .order_by(Listing.id.desc()).limit(30)
    )).scalars().all()
    if not rows:
        await message.answer(t(lang, "my_empty"))
        return
    items = [(l.id, f"{STATUS_ICON.get(l.status, '')} #{l.id} · {l.title[:28]} · {fmt_price(l.price)}") for l in rows]
    await message.answer(t(lang, "my_title"), reply_markup=my_list_kb(items, "open"))


async def _own(session: AsyncSession, listing_id: int, user_id: int) -> Listing | None:
    listing = await session.get(Listing, listing_id)
    return listing if listing and listing.seller_id == user_id and listing.status != "deleted" else None


@router.callback_query(ItemCb.filter(F.a == "open"))
async def open_own(call: CallbackQuery, callback_data: ItemCb, session: AsyncSession, user: User, lang: str) -> None:
    listing = await _own(session, callback_data.id, user.id)
    if not listing:
        await call.answer(t(lang, "listing_not_found"), show_alert=True)
        return
    caption = render_listing(listing, lang) + f"\n\n👁 {listing.views}  |  {STATUS_ICON.get(listing.status, '')} {listing.status}"
    if listing.status == "rejected" and listing.reject_reason:
        caption += f"\n❗️ {listing.reject_reason}"
    await call.message.answer_photo(listing.photos[0], caption=caption[:1024],
                                    reply_markup=owner_kb(lang, listing.id, listing.status))
    await call.answer()


@router.callback_query(ItemCb.filter(F.a.in_({"sold", "del"})))
async def sold_or_delete(call: CallbackQuery, callback_data: ItemCb, session: AsyncSession, bot: Bot,
                         user: User, lang: str) -> None:
    listing = await _own(session, callback_data.id, user.id)
    if not listing:
        await call.answer(t(lang, "listing_not_found"), show_alert=True)
        return
    listing.status = "sold" if callback_data.a == "sold" else "deleted"
    await session.commit()
    await update_channel_post(bot, session, listing)
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t(lang, "marked_sold" if callback_data.a == "sold" else "deleted", id=listing.id))
    await call.answer()


# ---------- TOP: Telegram Stars ----------
@router.callback_query(ItemCb.filter(F.a == "top"))
async def top_menu(call: CallbackQuery, callback_data: ItemCb, session: AsyncSession, user: User, lang: str) -> None:
    listing = await _own(session, callback_data.id, user.id)
    if not listing or listing.status != "active":
        await call.answer(t(lang, "top_only_active"), show_alert=True)
        return
    await call.message.answer(t(lang, "top_choose"), reply_markup=top_kb(lang, listing.id))
    await call.answer()


@router.callback_query(TopCb.filter())
async def top_invoice(call: CallbackQuery, callback_data: TopCb, session: AsyncSession, user: User, lang: str) -> None:
    listing = await _own(session, callback_data.id, user.id)
    if not listing or listing.status != "active":
        await call.answer(t(lang, "top_only_active"), show_alert=True)
        return
    stars = config.top_3d_stars if callback_data.days == 3 else config.top_7d_stars
    title = f"TOP #{listing.id} — {callback_data.days} " + ("дн." if lang == "ru" else "kun")
    await call.message.answer_invoice(
        title=title,
        description=listing.title[:255] or "TOP",
        payload=f"top{callback_data.days}:{listing.id}",
        currency="XTR",  # Telegram Stars — raqamli xizmatlar uchun majburiy
        prices=[LabeledPrice(label=title, amount=stars)],
        provider_token="",
    )
    await call.answer()


@router.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery, session: AsyncSession) -> None:
    try:
        kind, lid = query.invoice_payload.split(":")
        listing = await session.get(Listing, int(lid))
        ok = kind in ("top3", "top7") and listing and listing.status == "active" \
            and listing.seller_id == query.from_user.id
    except (ValueError, AttributeError):
        ok = False
    if ok:
        await query.answer(ok=True)
    else:
        await query.answer(ok=False, error_message="E'lon faol emas / Объявление неактивно")


@router.message(F.successful_payment)
async def paid(message: Message, session: AsyncSession, bot: Bot, user: User, lang: str) -> None:
    sp = message.successful_payment
    kind, lid = sp.invoice_payload.split(":")
    days = 3 if kind == "top3" else 7
    session.add(Payment(user_id=user.id, listing_id=int(lid), product=kind, amount=sp.total_amount,
                        charge_id=sp.telegram_payment_charge_id))
    listing = await session.get(Listing, int(lid))
    now = utcnow()
    base = listing.top_until if listing.top_until and listing.top_until > now else now
    listing.top_until = base + timedelta(days=days)
    await session.commit()

    # Kanalda 🔥 TOP sifatida qayta chiqaramiz (bump)
    await publish_to_channel(bot, session, listing)
    until = (listing.top_until + timedelta(hours=5)).strftime("%d.%m %H:%M")  # Toshkent vaqti
    await message.answer(t(lang, "top_done", id=listing.id, until=until))
    for admin_id in config.admin_ids:
        try:
            await bot.send_message(admin_id, f"💰 +{sp.total_amount} ⭐️ | TOP{days} #{listing.id} | user {user.id}\n"
                                             f"charge: <code>{sp.telegram_payment_charge_id}</code>")
        except Exception:  # noqa: BLE001
            pass
