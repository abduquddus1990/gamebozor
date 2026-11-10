"""E'lonni ochish, sevimlilar, aloqa, shikoyat, sotuvchini tekshirish.

Katalog ko'rish endi qidiruv dvigateli orqali ishlaydi (handlers/search.py, handlers/dashboard.py).
"""
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import ItemCb
from bot.config import config
from bot.db.models import Blacklist, Favorite, Listing, Report, User
from bot.handlers.common import is_fav, require_rules, show_single
from bot.i18n import MENU_TEXTS, all_variants, t
from bot.keyboards import my_list_kb
from bot.services.render import fmt_price
from bot.states import CheckForm, ReportForm

router = Router(name="catalog")


@router.message(F.text.regexp(r"^/l(\d+)(@\w+)?$").as_("m"))
async def open_by_command(message: Message, m, session: AsyncSession, bot: Bot, lang: str, user: User) -> None:
    await show_single(bot, message.chat.id, session, int(m.group(1)), lang, user.id)


# ---------- E'lon ustidagi amallar ----------
@router.callback_query(ItemCb.filter(F.a == "fav"))
async def toggle_fav(call: CallbackQuery, callback_data: ItemCb, session: AsyncSession, user: User, lang: str) -> None:
    if await is_fav(session, user.id, callback_data.id):
        await session.execute(delete(Favorite).where(Favorite.user_id == user.id,
                                                     Favorite.listing_id == callback_data.id))
        added = False
    else:
        if not await session.get(Listing, callback_data.id):
            await call.answer(t(lang, "listing_not_found"), show_alert=True)
            return
        session.add(Favorite(user_id=user.id, listing_id=callback_data.id))
        added = True
    await session.commit()
    # Yurak belgisini yangilaymiz
    kb = call.message.reply_markup if call.message else None
    if kb:
        for row in kb.inline_keyboard:
            for btn in row:
                if btn.callback_data == callback_data.pack():
                    btn.text = "💔" if added else "❤️"
        try:
            await call.message.edit_reply_markup(reply_markup=kb)
        except TelegramBadRequest:
            pass
    await call.answer(t(lang, "fav_added" if added else "fav_removed"))


@router.callback_query(ItemCb.filter(F.a == "contact"))
async def contact(call: CallbackQuery, callback_data: ItemCb, session: AsyncSession, bot: Bot,
                  user: User, lang: str) -> None:
    listing = await session.get(Listing, callback_data.id)
    if not listing or listing.status != "active":
        await call.answer(t(lang, "listing_not_found"), show_alert=True)
        return
    if not await require_rules(call, user, lang):
        return
    await call.message.answer(t(lang, "contact_info", contact=escape(listing.contact)))
    await call.answer()
    if user.id != listing.seller_id:
        seller = await session.get(User, listing.seller_id)
        who = f"@{user.username}" if user.username else escape(user.full_name)
        try:
            await bot.send_message(listing.seller_id, t(seller.lang if seller else "uz", "seller_notified",
                                                         id=listing.id, who=who))
        except TelegramAPIError:
            pass


@router.callback_query(ItemCb.filter(F.a == "report"))
async def report_start(call: CallbackQuery, callback_data: ItemCb, state: FSMContext, lang: str) -> None:
    await state.set_state(ReportForm.reason)
    await state.update_data(report_listing=callback_data.id)
    await call.message.answer(t(lang, "ask_report"))
    await call.answer()


@router.message(ReportForm.reason, F.text, ~F.text.in_(MENU_TEXTS), ~F.text.startswith("/"))
async def report_save(message: Message, state: FSMContext, session: AsyncSession, bot: Bot,
                      user: User, lang: str) -> None:
    lid = (await state.get_data()).get("report_listing")
    listing = await session.get(Listing, lid) if lid else None
    target = listing.contact if listing else "?"
    session.add(Report(reporter_id=user.id, listing_id=lid, target=target.lstrip("@").lower()[:64],
                       reason=message.text[:255]))
    await session.commit()
    await state.set_state(None)
    await message.answer(t(lang, "report_sent"))
    for admin_id in config.admin_ids:
        try:
            await bot.send_message(admin_id, f"🚩 Shikoyat: e'lon #{lid} ({escape(target)})\n"
                                             f"Kimdan: {user.id}\nSabab: {escape(message.text[:500])}\n\n"
                                             f"Qora ro'yxatga: <code>/blacklist {escape(target)} izoh</code>")
        except TelegramAPIError:
            pass


# ---------- Sevimlilar ----------
@router.message(Command("fav"))
@router.message(F.text.in_(all_variants("btn_fav")))
async def favorites(message: Message, state: FSMContext, session: AsyncSession, user: User, lang: str) -> None:
    await state.set_state(None)
    rows = (await session.execute(
        select(Listing).join(Favorite, Favorite.listing_id == Listing.id)
        .where(Favorite.user_id == user.id, Listing.status.in_(("active", "sold")))
        .order_by(Favorite.id.desc()).limit(30)
    )).scalars().all()
    if not rows:
        await message.answer(t(lang, "fav_empty"))
        return
    items = [(l.id, f"{'✅ ' if l.status == 'sold' else ''}#{l.id} · {l.title[:30]} · {fmt_price(l.price)}")
             for l in rows]
    await message.answer(t(lang, "fav_title"), reply_markup=my_list_kb(items, "view"))


@router.callback_query(ItemCb.filter(F.a == "view"))
async def view_from_list(call: CallbackQuery, callback_data: ItemCb, session: AsyncSession, bot: Bot,
                         user: User, lang: str) -> None:
    await call.answer()
    await show_single(bot, call.message.chat.id, session, callback_data.id, lang, user.id)


# ---------- Sotuvchini tekshirish ----------
async def check_start(message: Message, state: FSMContext, lang: str) -> None:
    await state.set_state(CheckForm.target)
    await message.answer(t(lang, "ask_check"))


@router.message(F.text.in_(all_variants("btn_check")))
async def check_btn(message: Message, state: FSMContext, lang: str) -> None:
    await check_start(message, state, lang)


@router.message(Command("check"))
async def check_cmd(message: Message, command: CommandObject, state: FSMContext, session: AsyncSession,
                    lang: str) -> None:
    if command.args:
        await state.set_state(None)
        await _check(message, session, lang, command.args)
    else:
        await check_start(message, state, lang)


@router.message(CheckForm.target, F.text, ~F.text.in_(MENU_TEXTS), ~F.text.startswith("/"))
async def check_do(message: Message, state: FSMContext, session: AsyncSession, lang: str) -> None:
    await state.set_state(None)
    await _check(message, session, lang, message.text)


async def _check(message: Message, session: AsyncSession, lang: str, raw: str) -> None:
    target = raw.strip().split("/")[-1].lstrip("@").lower()[:64]
    shown = "@" + escape(target)
    bl = await session.scalar(select(Blacklist).where(Blacklist.target == target))
    if bl:
        await message.answer(t(lang, "check_bad", t=shown, note=escape(bl.note or "-")))
        return
    reports = await session.scalar(select(func.count(Report.id)).where(Report.target == target)) or 0
    extra = ""
    member = await session.scalar(select(User).where(func.lower(User.username) == target))
    if member:
        total = await session.scalar(select(func.count(Listing.id)).where(Listing.seller_id == member.id)) or 0
        sold = await session.scalar(select(func.count(Listing.id)).where(
            Listing.seller_id == member.id, Listing.status == "sold")) or 0
        extra = t(lang, "check_member", listings=total, sold=sold,
                  verified=t(lang, "verified") if member.is_verified else "")
    await message.answer(t(lang, "check_ok", t=shown, reports=reports, extra=extra))
