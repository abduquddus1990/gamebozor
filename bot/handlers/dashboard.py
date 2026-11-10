"""🏠 Dashboard — bitta xabar ichida ishlaydigan boshqaruv paneli.

Barcha ekranlar callback orqali shu xabarni tahrirlaydi (chat to'lib ketmaydi).
Bo'limlar: o'yinlar (har biri alohida bozor + ko'rsatkichlar), qidiruv, Coin/UC, profil,
qoidalar/xavfsizlik/qo'llanma/buyruqlar.
"""
from datetime import timedelta
from html import escape

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import DashCb, GuideCb
from bot.config import config
from bot.db.models import Favorite, Listing, SavedSearch, User
from bot.handlers.common import show_screen
from bot.i18n import all_variants, t
from bot.keyboards import (back_kb, dash_game_kb, dash_games_kb, dash_home_kb, dash_info_kb, guide_kb, lang_kb,
                           main_menu, profile_kb, rules_kb)
from bot.services.games import GAMES
from bot.services.render import fmt_price, utcnow
from bot.services.pro import is_pro, status_text
from bot.services.search import market_stats

router = Router(name="dashboard")


# ---------- Bosh sahifa ----------
async def home_text(session: AsyncSession, user: User, lang: str) -> str:
    day_ago = utcnow() - timedelta(days=1)
    by_status = dict((await session.execute(
        select(Listing.status, func.count(Listing.id)).group_by(Listing.status))).all())
    new24 = await session.scalar(select(func.count(Listing.id)).where(
        Listing.status == "active", Listing.approved_at >= day_ago)) or 0
    users = await session.scalar(select(func.count(User.id))) or 0
    my_active = await session.scalar(select(func.count(Listing.id)).where(
        Listing.seller_id == user.id, Listing.status == "active")) or 0
    favs = await session.scalar(select(func.count(Favorite.id)).where(Favorite.user_id == user.id)) or 0
    alerts = await session.scalar(select(func.count(SavedSearch.id)).where(SavedSearch.user_id == user.id)) or 0
    return t(lang, "dash_home", active=by_status.get("active", 0), new24=new24, sold=by_status.get("sold", 0),
             users=users, my_active=my_active, favs=favs, alerts=alerts)


async def send_home(event: Message | CallbackQuery, session: AsyncSession, user: User, lang: str,
                    is_admin: bool) -> None:
    await show_screen(event, await home_text(session, user, lang), dash_home_kb(lang, is_admin))


@router.message(Command("menu", "dashboard"))
@router.message(F.text.in_(all_variants("btn_dash")))
async def cmd_menu(message: Message, state: FSMContext, session: AsyncSession, user: User, lang: str,
                   is_admin: bool) -> None:
    await state.set_state(None)
    await send_home(message, session, user, lang, is_admin)


@router.callback_query(DashCb.filter(F.a == "home"))
async def cb_home(call: CallbackQuery, callback_data: DashCb, state: FSMContext, session: AsyncSession,
                  user: User, lang: str, is_admin: bool) -> None:
    await state.set_state(None)
    await send_home(call, session, user, lang, is_admin)
    await call.answer("🔄" if callback_data.v == "r" else None)


# ---------- O'yinlar bo'limlari ----------
async def _counts(session: AsyncSession) -> dict[str, int]:
    return dict((await session.execute(
        select(Listing.game, func.count(Listing.id)).where(Listing.status == "active").group_by(Listing.game))).all())


async def show_games(event: Message | CallbackQuery, session: AsyncSession, lang: str, kind: str) -> None:
    text = t(lang, "dash_games") if kind == "account" else t(lang, "topup_intro")
    await show_screen(event, text, dash_games_kb(lang, kind, await _counts(session)))


@router.callback_query(DashCb.filter(F.a.in_({"games", "topup"})))
async def cb_games(call: CallbackQuery, callback_data: DashCb, session: AsyncSession, lang: str) -> None:
    await show_games(call, session, lang, "topup" if callback_data.a == "topup" else "account")
    await call.answer()


@router.message(Command("catalog", "topup"))
@router.message(F.text.in_(all_variants("btn_buy") | all_variants("btn_topup")))
async def msg_games(message: Message, state: FSMContext, session: AsyncSession, lang: str) -> None:
    await state.set_state(None)
    topup = message.text in all_variants("btn_topup") or (message.text or "").startswith("/topup")
    await show_games(message, session, lang, "topup" if topup else "account")


@router.callback_query(DashCb.filter(F.a == "game"))
async def cb_game(call: CallbackQuery, callback_data: DashCb, session: AsyncSession, lang: str) -> None:
    game = GAMES.get(callback_data.v)
    if not game:
        await call.answer()
        return
    st = await market_stats(session, game.code)
    if st["count"]:
        best = t(lang, "dash_game_best", best=fmt_price(st["best"])) if st.get("best") else ""
        text = t(lang, "dash_game", emoji=game.emoji, name=game.name, count=st["count"], new24=st["new24"],
                 sold=st["sold"], min=fmt_price(st["min"]), max=fmt_price(st["max"]), avg=fmt_price(st["avg"]),
                 best=best)
    else:
        text = t(lang, "dash_game_empty", emoji=game.emoji, name=game.name)
    await show_screen(call, text, dash_game_kb(lang, game, bool(st["count"])))
    await call.answer()


@router.callback_query(DashCb.filter(F.a == "soon"))
async def cb_soon(call: CallbackQuery, callback_data: DashCb, lang: str) -> None:
    game = GAMES.get(callback_data.v)
    await call.answer(t(lang, "soon", name=game.name if game else "?"), show_alert=True)


# ---------- Ma'lumot markazi: qoidalar, xavfsizlik, qo'llanma, buyruqlar ----------
@router.callback_query(DashCb.filter(F.a == "info"))
async def cb_info(call: CallbackQuery, lang: str) -> None:
    await show_screen(call, t(lang, "dash_info"), dash_info_kb(lang))
    await call.answer()


@router.callback_query(DashCb.filter(F.a == "rules"))
async def cb_rules(call: CallbackQuery, user: User, lang: str) -> None:
    await show_screen(call, t(lang, "rules"), rules_kb(lang, bool(user.rules_accepted_at)))
    await call.answer()


@router.message(Command("rules", "terms"))
@router.message(F.text.in_(all_variants("btn_rules")))
async def msg_rules(message: Message, state: FSMContext, user: User, lang: str) -> None:
    await state.set_state(None)
    await message.answer(t(lang, "rules"), reply_markup=rules_kb(lang, bool(user.rules_accepted_at)))


@router.callback_query(DashCb.filter(F.a == "safety"))
async def cb_safety(call: CallbackQuery, lang: str) -> None:
    await show_screen(call, t(lang, "safety"), back_kb(lang, "info"))
    await call.answer()


@router.message(Command("safety"))
async def msg_safety(message: Message, lang: str) -> None:
    await message.answer(t(lang, "safety"), reply_markup=back_kb(lang, "info"))


def _commands_text(lang: str) -> str:
    return t(lang, "commands", bot=config.bot_username)


@router.callback_query(DashCb.filter(F.a == "cmds"))
async def cb_cmds(call: CallbackQuery, lang: str) -> None:
    await show_screen(call, _commands_text(lang), back_kb(lang, "info"))
    await call.answer()


@router.message(Command("commands"))
async def msg_cmds(message: Message, lang: str) -> None:
    await message.answer(_commands_text(lang), reply_markup=back_kb(lang))


def _guide_page(lang: str, page: int) -> tuple[str, int]:
    pages = t(lang, "guide")
    page = max(0, min(page, len(pages) - 1))
    return pages[page].format(bot=config.bot_username, channel=config.channel), len(pages)


@router.callback_query(GuideCb.filter())
async def cb_guide(call: CallbackQuery, callback_data: GuideCb, user: User, lang: str) -> None:
    text, total = _guide_page(lang, callback_data.p)
    await show_screen(call, text, guide_kb(lang, callback_data.p, total, bool(user.rules_accepted_at)))
    await call.answer()


@router.message(Command("guide"))
async def msg_guide(message: Message, user: User, lang: str) -> None:
    text, total = _guide_page(lang, 0)
    await message.answer(text, reply_markup=guide_kb(lang, 0, total, bool(user.rules_accepted_at)))


@router.callback_query(DashCb.filter(F.a == "accept"))
async def cb_accept(call: CallbackQuery, session: AsyncSession, user: User, lang: str, is_admin: bool) -> None:
    first = user.rules_accepted_at is None
    if first:
        user.rules_accepted_at = utcnow()
        await session.commit()
    await call.answer("✅")
    try:
        await call.message.edit_reply_markup(reply_markup=None)
    except Exception:  # noqa: BLE001
        pass
    # Pastki doimiy menyu + Dashboard
    await call.message.answer(t(lang, "rules_accepted"), reply_markup=main_menu(lang, is_admin))
    await send_home(call.message, session, user, lang, is_admin)


@router.callback_query(DashCb.filter(F.a == "lang"))
async def cb_lang(call: CallbackQuery, lang: str) -> None:
    await call.message.answer(t(lang, "choose_lang"), reply_markup=lang_kb())
    await call.answer()


# ---------- Profil ----------
@router.callback_query(DashCb.filter(F.a == "profile"))
async def cb_profile(call: CallbackQuery, session: AsyncSession, user: User, lang: str) -> None:
    by_status = dict((await session.execute(
        select(Listing.status, func.count(Listing.id)).where(Listing.seller_id == user.id)
        .group_by(Listing.status))).all())
    views = await session.scalar(select(func.coalesce(func.sum(Listing.views), 0)).where(
        Listing.seller_id == user.id)) or 0
    favs = await session.scalar(select(func.count(Favorite.id)).where(Favorite.user_id == user.id)) or 0
    alerts = await session.scalar(select(func.count(SavedSearch.id)).where(SavedSearch.user_id == user.id)) or 0
    from bot.handlers.reviews import reviews_block
    ref = f"https://t.me/{config.bot_username}?start=r_{user.id}"
    text = t(lang, "dash_profile", id=user.id, username=f"@{escape(user.username)}" if user.username else "",
             badge=t(lang, "badge_verified" if user.is_verified else "badge_none")
             + ("\n" + status_text(user, lang) if is_pro(user) else ""),
             rating=await reviews_block(session, user.id, lang, limit=0),
             active=by_status.get("active", 0), pending=by_status.get("pending", 0), sold=by_status.get("sold", 0),
             views=views, favs=favs, alerts=alerts,
             since=(user.created_at or utcnow()).strftime("%d.%m.%Y"), ref=ref)
    await show_screen(call, text, profile_kb(lang, ref))
    await call.answer()


# ---------- Boshqa bo'limlarga o'tish (mavjud handlerlarni chaqiramiz) ----------
@router.callback_query(DashCb.filter(F.a.in_({"sell", "my", "fav", "check", "alerts"})))
async def cb_delegate(call: CallbackQuery, callback_data: DashCb, state: FSMContext, session: AsyncSession,
                      user: User, lang: str, is_admin: bool) -> None:
    from bot.handlers import catalog, my_listings, search, sell

    await call.answer()
    msg = call.message
    a = callback_data.a
    if a == "sell":
        await sell.sell_start(msg, state, session, user, lang, is_admin)
    elif a == "my":
        await my_listings.my_listings(msg, state, session, user, lang)
    elif a == "fav":
        await catalog.favorites(msg, state, session, user, lang)
    elif a == "check":
        await catalog.check_start(msg, state, lang)
    elif a == "alerts":
        await search.show_alerts(call, session, user, lang)
