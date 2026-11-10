"""Admin: moderatsiya, statistika, reklama manbalari, xabar tarqatish, bloklash, qora ro'yxat."""
import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError, TelegramRetryAfter
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import AdminCb, ModCb
from bot.config import config
from bot.db.models import Blacklist, Listing, Payment, User
from bot.i18n import MENU_TEXTS, REJECT_REASONS, all_variants, t
from bot.keyboards import admin_kb, reject_reasons_kb
from bot.services.listings import approve, send_to_moderation
from bot.services.render import utcnow
from bot.states import BroadcastForm

log = logging.getLogger(__name__)
router = Router(name="admin")
router.message.filter(F.from_user.id.in_(config.admin_ids))
router.callback_query.filter(F.from_user.id.in_(config.admin_ids))


@router.message(F.text.in_(all_variants("btn_admin")))
@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(
        "🛠 <b>Admin panel</b>\n\n"
        "Buyruqlar:\n"
        "<code>/ban ID</code>, <code>/unban ID</code>\n"
        "<code>/verify ID</code> — ✅ tasdiqlangan sotuvchi\n"
        "<code>/blacklist @user izoh</code>, <code>/unblacklist @user</code>\n"
        "<code>/refund CHARGE_ID</code> — Stars qaytarish",
        reply_markup=admin_kb(),
    )


# ---------- Moderatsiya ----------
async def _get_pending(call: CallbackQuery, session: AsyncSession, lid: int) -> Listing | None:
    listing = await session.get(Listing, lid)
    if not listing or listing.status != "pending":
        await call.answer("Bu e'lon allaqachon ko'rib chiqilgan.", show_alert=True)
        await call.message.edit_reply_markup(reply_markup=None)
        return None
    return listing


@router.callback_query(ModCb.filter(F.a == "ok"))
async def mod_ok(call: CallbackQuery, callback_data: ModCb, session: AsyncSession, bot: Bot) -> None:
    listing = await _get_pending(call, session, callback_data.id)
    if not listing:
        return
    await approve(bot, session, listing)
    await call.message.edit_caption(caption=f"{call.message.html_text}\n\n✅ Tasdiqladi: {call.from_user.full_name}"[:1024])
    seller = await session.get(User, listing.seller_id)
    try:
        await bot.send_message(listing.seller_id, t(seller.lang if seller else "uz", "approved", id=listing.id))
    except TelegramAPIError:
        pass
    await call.answer("✅")


@router.callback_query(ModCb.filter(F.a == "rej"))
async def mod_reject(call: CallbackQuery, callback_data: ModCb, session: AsyncSession) -> None:
    if await _get_pending(call, session, callback_data.id):
        await call.message.edit_reply_markup(reply_markup=reject_reasons_kb(callback_data.id))
        await call.answer()


@router.callback_query(ModCb.filter(F.a == "reason"))
async def mod_reason(call: CallbackQuery, callback_data: ModCb, session: AsyncSession, bot: Bot) -> None:
    listing = await _get_pending(call, session, callback_data.id)
    if not listing:
        return
    seller = await session.get(User, listing.seller_id)
    s_lang = seller.lang if seller and seller.lang else "uz"
    uz, ru = REJECT_REASONS[callback_data.r]
    listing.status = "rejected"
    listing.reject_reason = ru if s_lang == "ru" else uz
    await session.commit()
    await call.message.edit_caption(caption=f"{call.message.html_text}\n\n❌ Rad etdi: {call.from_user.full_name} ({uz})"[:1024])
    try:
        await bot.send_message(listing.seller_id, t(s_lang, "rejected", id=listing.id, reason=listing.reject_reason))
    except TelegramAPIError:
        pass
    await call.answer("❌")


# ---------- Statistika ----------
@router.callback_query(AdminCb.filter(F.a == "stats"))
async def stats(call: CallbackQuery, session: AsyncSession) -> None:
    day_ago = utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    users = await session.scalar(select(func.count(User.id)))
    users_today = await session.scalar(select(func.count(User.id)).where(User.created_at >= day_ago))
    by_status = dict((await session.execute(
        select(Listing.status, func.count(Listing.id)).group_by(Listing.status))).all())
    stars = await session.scalar(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.refunded == False))  # noqa: E712
    await call.message.answer(
        "📊 <b>Statistika</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{users}</b> (bugun +{users_today})\n\n"
        f"🟢 Faol: {by_status.get('active', 0)}\n⏳ Moderatsiyada: {by_status.get('pending', 0)}\n"
        f"✅ Sotilgan: {by_status.get('sold', 0)}\n🔴 Rad etilgan: {by_status.get('rejected', 0)}\n\n"
        f"⭐️ Stars daromad: <b>{stars}</b> (~${stars * 0.013:.2f})"
    )
    await call.answer()


@router.callback_query(AdminCb.filter(F.a == "sources"))
async def sources(call: CallbackQuery, session: AsyncSession) -> None:
    rows = (await session.execute(
        select(User.source, func.count(User.id)).group_by(User.source).order_by(func.count(User.id).desc()).limit(30)
    )).all()
    text = "\n".join(f"• <code>{s or 'organik'}</code> — {n}" for s, n in rows) or "—"
    await call.message.answer(
        "📈 <b>Foydalanuvchilar manbasi</b>\n"
        f"Reklama havolasi: <code>https://t.me/{config.bot_username}?start=ads_NOM</code>\n\n{text}")
    await call.answer()


@router.callback_query(AdminCb.filter(F.a == "pending"))
async def pending(call: CallbackQuery, session: AsyncSession, bot: Bot) -> None:
    rows = (await session.execute(select(Listing).where(Listing.status == "pending").order_by(Listing.id).limit(10))).scalars().all()
    if not rows:
        await call.answer("Moderatsiyada e'lon yo'q 👍", show_alert=True)
        return
    for listing in rows:
        await send_to_moderation(bot, listing)
    await call.answer()


# ---------- Xabar tarqatish ----------
@router.callback_query(AdminCb.filter(F.a == "broadcast"))
async def broadcast_start(call: CallbackQuery, state: FSMContext) -> None:
    await state.set_state(BroadcastForm.message)
    await call.message.answer("📣 Hammaga yuboriladigan xabarni yuboring (matn, rasm, video — istalgan).\n/cancel — bekor.")
    await call.answer()


@router.message(BroadcastForm.message, Command("cancel"))
async def broadcast_cancel(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer("❌ Bekor qilindi.")


@router.message(BroadcastForm.message, ~F.text.in_(MENU_TEXTS))
async def broadcast_send(message: Message, state: FSMContext, session: AsyncSession, bot: Bot) -> None:
    await state.clear()
    ids = (await session.execute(select(User.id).where(User.is_banned == False))).scalars().all()  # noqa: E712
    await message.answer(f"⏳ {len(ids)} ta foydalanuvchiga yuborilmoqda...")
    asyncio.create_task(_broadcast(bot, message, ids))


async def _broadcast(bot: Bot, src: Message, ids: list[int]) -> None:
    ok = fail = 0
    for uid in ids:
        try:
            await src.copy_to(uid)
            ok += 1
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after)
            try:
                await src.copy_to(uid)
                ok += 1
            except TelegramAPIError:
                fail += 1
        except TelegramAPIError:
            fail += 1
        await asyncio.sleep(0.05)  # ~20 xabar/soniya — Telegram limitidan past
    await bot.send_message(src.chat.id, f"✅ Yuborildi: {ok}\n❌ Xato: {fail}")


# ---------- Buyruqlar ----------
async def _set_user_flag(message: Message, command: CommandObject, session: AsyncSession, attr: str, value: bool) -> None:
    if not command.args or not command.args.strip().isdigit():
        await message.answer("ID raqam kiriting.")
        return
    u = await session.get(User, int(command.args.strip()))
    if not u:
        await message.answer("Foydalanuvchi topilmadi.")
        return
    setattr(u, attr, value)
    await session.commit()
    await message.answer(f"✅ {u.id}: {attr} = {value}")


@router.message(Command("ban"))
async def ban(message: Message, command: CommandObject, session: AsyncSession) -> None:
    await _set_user_flag(message, command, session, "is_banned", True)


@router.message(Command("unban"))
async def unban(message: Message, command: CommandObject, session: AsyncSession) -> None:
    await _set_user_flag(message, command, session, "is_banned", False)


@router.message(Command("verify"))
async def verify(message: Message, command: CommandObject, session: AsyncSession) -> None:
    await _set_user_flag(message, command, session, "is_verified", True)


@router.message(Command("blacklist"))
async def blacklist(message: Message, command: CommandObject, session: AsyncSession) -> None:
    if not command.args:
        await message.answer("Format: /blacklist @username izoh")
        return
    target, _, note = command.args.partition(" ")
    target = target.lstrip("@").lower()[:64]
    if await session.scalar(select(Blacklist).where(Blacklist.target == target)):
        await message.answer("Allaqachon ro'yxatda.")
        return
    session.add(Blacklist(target=target, note=note[:255]))
    await session.commit()
    await message.answer(f"⛔️ @{target} qora ro'yxatga qo'shildi.")


@router.message(Command("unblacklist"))
async def unblacklist(message: Message, command: CommandObject, session: AsyncSession) -> None:
    target = (command.args or "").strip().lstrip("@").lower()
    row = await session.scalar(select(Blacklist).where(Blacklist.target == target))
    if not row:
        await message.answer("Topilmadi.")
        return
    await session.delete(row)
    await session.commit()
    await message.answer(f"✅ @{target} ro'yxatdan olindi.")


@router.message(Command("refund"))
async def refund(message: Message, command: CommandObject, session: AsyncSession, bot: Bot) -> None:
    charge = (command.args or "").strip()
    p = await session.scalar(select(Payment).where(Payment.charge_id == charge))
    if not p or p.refunded:
        await message.answer("To'lov topilmadi yoki allaqachon qaytarilgan.")
        return
    try:
        await bot.refund_star_payment(user_id=p.user_id, telegram_payment_charge_id=charge)
    except TelegramAPIError as e:
        await message.answer(f"Xato: {e}")
        return
    p.refunded = True
    listing = await session.get(Listing, p.listing_id)
    if listing:
        listing.top_until = None
    await session.commit()
    await message.answer(f"↩️ {p.amount} ⭐️ qaytarildi.")


@router.message(Command("delreview"))
async def delreview(message: Message, command: CommandObject, session: AsyncSession) -> None:
    """Noto'g'ri/soxta sharhni o'chirish: /delreview ID"""
    from bot.db.models import Review

    arg = (command.args or "").strip()
    review = await session.get(Review, int(arg)) if arg.isdigit() else None
    if not review:
        await message.answer("Sharh topilmadi. Format: /delreview ID")
        return
    await session.delete(review)
    await session.commit()
    await message.answer(f"🗑 Sharh #{arg} o'chirildi ({review.rating}⭐️, sotuvchi {review.seller_id}).")


@router.message(Command("givepro"))
async def givepro(message: Message, command: CommandObject, session: AsyncSession, bot: Bot) -> None:
    """PRO ni qo'lda berish (sinov, hamkorlar, shop kanal egalari): /givepro ID KUN"""
    from bot.services.pro import activate, fmt_date

    parts = (command.args or "").split()
    if len(parts) != 2 or not all(p.isdigit() for p in parts):
        await message.answer("Format: /givepro ID KUN   (masalan: /givepro 123456789 30)")
        return
    u = await session.get(User, int(parts[0]))
    if not u:
        await message.answer("Foydalanuvchi topilmadi (botga /start bosganmi?).")
        return
    activate(u, int(parts[1]), top_credits=0)
    await session.commit()
    await message.answer(f"💎 {u.id}: PRO {fmt_date(u.pro_until)} gacha.")
    try:
        await bot.send_message(u.id, t(u.lang, "pro_done", until=fmt_date(u.pro_until), credits=u.pro_top_credits or 0))
    except TelegramAPIError:
        pass
