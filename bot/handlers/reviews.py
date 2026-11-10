"""⭐️ Sotuvchi reytingi va sharhlar.

Qoidalar (soxta baholardan himoya):
  • baho faqat shu e'londa «📞 Bog'lanish» ni bosgan xaridor qoldiradi (ContactLog);
  • bitta e'longa — bitta baho; o'ziga baho berib bo'lmaydi;
  • 1–2 ⭐️ baho adminlarga ham yuboriladi (firibgarlikni tez aniqlash uchun);
  • admin noto'g'ri sharhni /delreview ID bilan o'chiradi.
Sotuvchi e'lonni «✅ Sotildi» qilganda, bog'langan xaridorlarga baholash taklifi boradi.
"""
import asyncio
import logging
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import RevCb
from bot.config import config
from bot.db.models import ContactLog, Listing, Review, User
from bot.i18n import MENU_TEXTS, t
from bot.keyboards import rate_kb, review_skip_kb
from bot.services.reputation import stars
from bot.states import ReviewForm

log = logging.getLogger(__name__)
router = Router(name="reviews")


def _seller_name(seller: User | None) -> str:
    if not seller:
        return "?"
    return f"@{seller.username}" if seller.username else escape(seller.full_name or str(seller.id))


async def _check_can_rate(session: AsyncSession, user: User, listing: Listing | None) -> str | None:
    """Baho qo'yish mumkin bo'lmasa — sabab kaliti, mumkin bo'lsa None."""
    if not listing:
        return "listing_not_found"
    if listing.seller_id == user.id:
        return "rate_self"
    contacted = await session.scalar(select(ContactLog.id).where(
        ContactLog.user_id == user.id, ContactLog.listing_id == listing.id))
    if not contacted:
        return "rate_denied"
    done = await session.scalar(select(Review.id).where(Review.listing_id == listing.id, Review.buyer_id == user.id))
    if done:
        return "rate_dup"
    return None


async def ask_buyers_after_sale(bot: Bot, session: AsyncSession, listing: Listing) -> int:
    """E'lon sotildi → bog'langan xaridorlarga (sharh qoldirmaganlarga) baholash taklifi."""
    seller = await session.get(User, listing.seller_id)
    rows = (await session.execute(
        select(ContactLog.user_id, User.lang).join(User, User.id == ContactLog.user_id)
        .where(ContactLog.listing_id == listing.id, ContactLog.user_id != listing.seller_id))).all()
    reviewed = set((await session.execute(
        select(Review.buyer_id).where(Review.listing_id == listing.id))).scalars().all())
    sent = 0
    for uid, lang in rows:
        if uid in reviewed:
            continue
        lang = lang or "uz"
        try:
            await bot.send_message(uid, t(lang, "rate_ask_sold", id=listing.id, seller=_seller_name(seller)),
                                   reply_markup=rate_kb(lang, listing.id))
            sent += 1
        except TelegramAPIError:
            pass
        await asyncio.sleep(0.05)
    return sent


@router.callback_query(RevCb.filter(F.a == "ask"))
async def rate_ask(call: CallbackQuery, callback_data: RevCb, session: AsyncSession, user: User, lang: str) -> None:
    listing = await session.get(Listing, callback_data.id)
    reason = await _check_can_rate(session, user, listing)
    if reason:
        await call.answer(t(lang, reason), show_alert=True)
        return
    seller = await session.get(User, listing.seller_id)
    await call.message.answer(t(lang, "rate_ask", id=listing.id, seller=_seller_name(seller)),
                              reply_markup=rate_kb(lang, listing.id, not_bought=False))
    await call.answer()


@router.callback_query(RevCb.filter(F.a == "no"))
async def rate_not_bought(call: CallbackQuery, lang: str) -> None:
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass
    await call.answer(t(lang, "dismissed"))


@router.callback_query(RevCb.filter(F.a == "r"))
async def rate_set(call: CallbackQuery, callback_data: RevCb, state: FSMContext, session: AsyncSession, bot: Bot,
                   user: User, lang: str) -> None:
    listing = await session.get(Listing, callback_data.id)
    reason = await _check_can_rate(session, user, listing)
    if reason:
        await call.answer(t(lang, reason), show_alert=True)
        return
    n = max(1, min(5, callback_data.v))
    review = Review(listing_id=listing.id, seller_id=listing.seller_id, buyer_id=user.id, rating=n)
    session.add(review)
    await session.commit()
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass
    await state.set_state(ReviewForm.text)
    await state.update_data(review_id=review.id)
    await call.message.answer(t(lang, "rate_saved", stars=stars(n)), reply_markup=review_skip_kb(lang, listing.id))
    await call.answer("⭐️" * n)
    await _notify(bot, session, review, user)


async def _notify(bot: Bot, session: AsyncSession, review: Review, buyer: User, text: str = "") -> None:
    seller = await session.get(User, review.seller_id)
    s_lang = (seller.lang if seller else None) or "uz"
    body = f"💬 {escape(text)}" if text else ""
    try:
        await bot.send_message(review.seller_id, t(s_lang, "new_review", stars=stars(review.rating),
                                                   id=review.listing_id, text=body))
    except TelegramAPIError:
        pass
    if review.rating <= 2:
        who = f"@{buyer.username}" if buyer.username else str(buyer.id)
        for admin_id in config.admin_ids:
            try:
                await bot.send_message(admin_id, f"⚠️ Past baho {review.rating}/5 — e'lon #{review.listing_id}, "
                                                 f"sotuvchi <code>{review.seller_id}</code>, xaridor {escape(who)}\n"
                                                 f"{body}\nO'chirish: <code>/delreview {review.id}</code>")
            except TelegramAPIError:
                pass


@router.message(ReviewForm.text, F.text, ~F.text.in_(MENU_TEXTS), ~F.text.startswith("/"))
async def review_text(message: Message, state: FSMContext, session: AsyncSession, bot: Bot, user: User,
                      lang: str) -> None:
    rid = (await state.get_data()).get("review_id")
    await state.set_state(None)
    review = await session.get(Review, rid) if rid else None
    if review and review.buyer_id == user.id:
        review.text = message.text.strip()[:300]
        await session.commit()
        try:  # sotuvchiga izoh matni ham boradi
            await bot.send_message(review.seller_id, f"💬 #{review.listing_id}: {escape(review.text)}")
        except TelegramAPIError:
            pass
    await message.answer(t(lang, "rate_thanks"))


@router.callback_query(RevCb.filter(F.a == "skip"))
async def review_skip(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.set_state(None)
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except TelegramBadRequest:
        pass
    await call.message.answer(t(lang, "rate_thanks"))
    await call.answer()


async def reviews_block(session: AsyncSession, seller_id: int, lang: str, limit: int = 3) -> str:
    """/check va profil uchun: reyting qatori + so'nggi sharhlar."""
    from bot.services.reputation import seller_info

    info = await seller_info(session, seller_id)
    if not info.count:
        return t(lang, "no_reviews")
    text = t(lang, "rating_line", avg=f"{info.avg:.1f}", n=info.count)
    rows = (await session.execute(select(Review).where(Review.seller_id == seller_id, Review.text != "")
                                  .order_by(Review.id.desc()).limit(limit))).scalars().all()
    if rows:
        text += t(lang, "reviews_title")
        for r in rows:
            text += f"\n{stars(r.rating)} {escape(r.text[:120])}"
    return text
