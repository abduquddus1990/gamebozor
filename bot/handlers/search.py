"""🔎 Kengaytirilgan qidiruv: filtrlar paneli, natijalar karuseli, 🔔 obunalar, erkin matnli qidiruv."""
from html import escape

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import AlertCb, SrchCb
from bot.config import config
from bot.db.models import SavedSearch, User
from bot.handlers.common import is_fav, listing_caption, show_screen
from bot.i18n import MENU_TEXTS, PRICE_RANGES, all_variants, t
from bot.keyboards import (alerts_kb, result_kb, search_field_kb, search_game_kb, search_kb, search_price_kb,
                           search_sort_kb, search_text_kb)
from bot.services.alerts import describe
from bot.services.games import GAMES, TEXT_EXAMPLES, short_label
from bot.services.search import SORTS, active_count, clean, empty_filters, parse_price_range, search
from bot.states import SearchInput

router = Router(name="search")


# ---------- Filtrlarni saqlash (User.search JSON) ----------
def get_f(user: User) -> dict:
    return clean(dict(user.search or {}))


async def save_f(session: AsyncSession, user: User, f: dict) -> dict:
    f = clean(f)
    user.search = {**f, "min": dict(f["min"]), "ch": dict(f["ch"]), "tx": dict(f["tx"])}  # yangi obyekt — JSON o'zgarishi saqlanadi
    await session.commit()
    return f


async def menu_text(session: AsyncSession, f: dict, lang: str) -> tuple[str, int]:
    total = len(await search(session, f))
    lines = [t(lang, "search_title"), "━━━━━━━━━━━━━━━━━━━━", f"🎛 {describe(f, lang)}"]
    if not active_count(f):
        lines.append(f"<i>{t(lang, 'search_no_filters')}</i>")
    lines += ["━━━━━━━━━━━━━━━━━━━━", t(lang, "search_found", n=total), "", t(lang, "search_hint")]
    return "\n".join(lines), total


async def show_menu(event: Message | CallbackQuery, session: AsyncSession, user: User, lang: str) -> Message | None:
    f = get_f(user)
    text, total = await menu_text(session, f, lang)
    return await show_screen(event, text, search_kb(lang, f, total))


# ---------- Natijalar karuseli ----------
async def show_results(event: Message | CallbackQuery, session: AsyncSession, user: User, lang: str,
                       idx: int = 0) -> None:
    f = get_f(user)
    items = await search(session, f)
    if not items:
        if isinstance(event, CallbackQuery):
            await event.answer(t(lang, "search_empty")[:190], show_alert=True)
        text, total = await menu_text(session, f, lang)
        await show_screen(event, t(lang, "search_empty") + "\n\n" + text, search_kb(lang, f, total))
        return
    total = len(items)
    idx %= total
    listing = items[idx]
    listing.views += 1
    await session.commit()

    caption = await listing_caption(session, listing, lang)
    if len(listing.photos) > 1:
        extra = "\n\n" + t(lang, "more_photos", n=len(listing.photos) - 1, id=listing.id)
        caption = (caption[:1024 - len(extra)] + extra) if len(caption) + len(extra) > 1024 else caption + extra
    kb = result_kb(lang, listing.id, idx, total, await is_fav(session, user.id, listing.id))

    if isinstance(event, CallbackQuery):
        msg = event.message
        if msg and msg.photo:
            # Karusel: bitta xabar tahrirlanadi — chat to'lib ketmaydi
            try:
                await msg.edit_media(InputMediaPhoto(media=listing.photos[0], caption=caption), reply_markup=kb)
            except TelegramBadRequest:
                pass
            return True
        if msg:
            try:
                await msg.delete()
            except TelegramBadRequest:
                pass
            await msg.answer_photo(listing.photos[0], caption=caption, reply_markup=kb)
        return True
    await event.answer_photo(listing.photos[0], caption=caption, reply_markup=kb)
    return True


async def answer_found(call: CallbackQuery, found: bool, lang: str) -> None:
    if found:
        await call.answer()
    else:
        await call.answer(t(lang, "search_empty")[:190], show_alert=True)


# ---------- Kirish nuqtalari ----------
@router.message(Command("search"))
async def cmd_search(message: Message, command: CommandObject, state: FSMContext, session: AsyncSession,
                     user: User, lang: str) -> None:
    await state.set_state(None)
    if command.args:
        f = get_f(user)
        f["q"] = command.args.strip()[:60]
        await save_f(session, user, f)
        await show_results(message, session, user, lang)
    else:
        await show_menu(message, session, user, lang)


@router.message(F.text.in_(all_variants("btn_search")))
async def btn_search(message: Message, state: FSMContext, session: AsyncSession, user: User, lang: str) -> None:
    await state.set_state(None)
    await show_menu(message, session, user, lang)


@router.callback_query(SrchCb.filter(F.a == "menu"))
async def cb_menu(call: CallbackQuery, state: FSMContext, session: AsyncSession, user: User, lang: str) -> None:
    await state.set_state(None)
    await show_menu(call, session, user, lang)
    await call.answer()


@router.callback_query(SrchCb.filter(F.a == "quick"))
async def cb_quick(call: CallbackQuery, callback_data: SrchCb, session: AsyncSession, user: User, lang: str) -> None:
    """Dashboard o'yin sahifasidan: «barchasi», «arzonlari», «kuchlilari», narx oralig'i."""
    game = GAMES.get(callback_data.k)
    f = empty_filters(game.kind if game else "account", callback_data.k)
    if callback_data.v in SORTS:
        f["sort"] = callback_data.v
    elif callback_data.v in PRICE_RANGES:
        lo, hi = PRICE_RANGES[callback_data.v]
        f["pmin"], f["pmax"] = (lo or None), hi
    await save_f(session, user, f)
    await answer_found(call, await show_results(call, session, user, lang), lang)


@router.callback_query(SrchCb.filter(F.a == "show"))
async def cb_show(call: CallbackQuery, session: AsyncSession, user: User, lang: str) -> None:
    await answer_found(call, await show_results(call, session, user, lang), lang)


@router.callback_query(SrchCb.filter(F.a == "pg"))
async def cb_page(call: CallbackQuery, callback_data: SrchCb, session: AsyncSession, user: User, lang: str) -> None:
    await answer_found(call, await show_results(call, session, user, lang, callback_data.i), lang)


# ---------- Filtrlar ----------
@router.callback_query(SrchCb.filter(F.a == "game"))
async def cb_game(call: CallbackQuery, lang: str) -> None:
    await show_screen(call, t(lang, "choose_game"), search_game_kb(lang))
    await call.answer()


@router.callback_query(SrchCb.filter(F.a == "sg"))
async def cb_set_game(call: CallbackQuery, callback_data: SrchCb, session: AsyncSession, user: User,
                      lang: str) -> None:
    f = get_f(user)
    game = GAMES.get(callback_data.k)
    f["g"] = game.code if game else ""
    f["k"] = game.kind if game else "account"
    await save_f(session, user, f)
    await show_menu(call, session, user, lang)
    await call.answer()


async def _ask_input(call: CallbackQuery, state: FSMContext, key: str, text: str, kb) -> None:
    msg = await show_screen(call, text, kb)
    await state.set_state(SearchInput.value)
    await state.update_data(skey=key, smsg=msg.message_id if msg else None)


@router.callback_query(SrchCb.filter(F.a == "price"))
async def cb_price(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await _ask_input(call, state, "price", t(lang, "ask_price_range"), search_price_kb(lang))
    await call.answer()


@router.callback_query(SrchCb.filter(F.a == "pp"))
async def cb_price_preset(call: CallbackQuery, callback_data: SrchCb, state: FSMContext, session: AsyncSession,
                          user: User, lang: str) -> None:
    await state.set_state(None)
    f = get_f(user)
    lo, hi = PRICE_RANGES.get(callback_data.v, (0, None))
    f["pmin"], f["pmax"] = (lo or None), hi
    await save_f(session, user, f)
    await show_menu(call, session, user, lang)
    await call.answer()


@router.callback_query(SrchCb.filter(F.a == "q"))
async def cb_query(call: CallbackQuery, state: FSMContext, user: User, lang: str) -> None:
    f = get_f(user)
    await _ask_input(call, state, "q", t(lang, "ask_query"), search_text_kb(lang, "q", bool(f.get("q"))))
    await call.answer()


@router.callback_query(SrchCb.filter(F.a == "f"))
async def cb_field(call: CallbackQuery, callback_data: SrchCb, state: FSMContext, user: User, lang: str) -> None:
    f = get_f(user)
    game = GAMES.get(f["g"])
    fld = game.field(callback_data.k) if game else None
    if not fld:
        await call.answer()
        return
    label = short_label(fld, lang)
    if fld.filter == "min":
        await _ask_input(call, state, fld.key, t(lang, "ask_min", icon=fld.icon, label=label),
                         search_field_kb(lang, fld, fld.key in f["min"]))
    elif fld.filter == "choice":
        await state.set_state(None)
        await show_screen(call, t(lang, "ask_choice", icon=fld.icon, label=label),
                          search_field_kb(lang, fld, fld.key in f["ch"]))
    else:
        await _ask_input(call, state, fld.key,
                         t(lang, "ask_text_field", icon=fld.icon, label=fld.label(lang),
                           example=TEXT_EXAMPLES.get(fld.key, "...")),
                         search_text_kb(lang, fld.key, fld.key in f["tx"]))
    await call.answer()


@router.callback_query(SrchCb.filter(F.a.in_({"set", "ch", "rm", "so", "ver", "reset"})))
async def cb_apply(call: CallbackQuery, callback_data: SrchCb, state: FSMContext, session: AsyncSession,
                   user: User, lang: str) -> None:
    await state.set_state(None)
    f = get_f(user)
    a, key = callback_data.a, callback_data.k
    game = GAMES.get(f["g"])
    if a == "set" and callback_data.v.isdigit():
        f["min"][key] = int(callback_data.v)
    elif a == "ch" and game and (fld := game.field(key)) and 0 <= callback_data.i < len(fld.options):
        f["ch"][key] = fld.options[callback_data.i]
    elif a == "rm":
        if key == "q":
            f["q"] = ""
        for part in ("min", "ch", "tx"):
            f[part].pop(key, None)
    elif a == "so" and callback_data.v in SORTS:
        f["sort"] = callback_data.v
    elif a == "ver":
        f["ver"] = not f.get("ver")
    elif a == "reset":
        f = empty_filters(f["k"], f["g"])
    await save_f(session, user, f)
    await show_menu(call, session, user, lang)
    await call.answer("✓")


@router.callback_query(SrchCb.filter(F.a == "sort"))
async def cb_sort(call: CallbackQuery, user: User, lang: str) -> None:
    await show_screen(call, t(lang, "s_sort"), search_sort_kb(lang, get_f(user)))
    await call.answer()


# ---------- Matn kiritish (narx, raqam, so'z) ----------
@router.message(SearchInput.value, F.text, ~F.text.in_(MENU_TEXTS), ~F.text.startswith("/"))
async def input_value(message: Message, state: FSMContext, session: AsyncSession, bot: Bot, user: User,
                      lang: str) -> None:
    data = await state.get_data()
    key, smsg = data.get("skey"), data.get("smsg")
    f = get_f(user)
    raw = message.text.strip()
    if key == "price":
        rng = parse_price_range(raw)
        if not rng:
            await message.answer(t(lang, "bad_range"))
            return
        f["pmin"], f["pmax"] = rng
    elif key == "q":
        f["q"] = raw[:60]
    else:
        game = GAMES.get(f["g"])
        fld = game.field(key) if game else None
        if not fld:
            await state.set_state(None)
            return
        if fld.filter == "min":
            digits = raw.replace(" ", "").replace(",", "").replace(".", "")
            if not digits.isdigit():
                await message.answer(t(lang, "bad_int"))
                return
            f["min"][key] = int(digits)
        else:
            f["tx"][key] = raw[:40]
    await state.set_state(None)
    await save_f(session, user, f)
    try:
        await message.delete()  # chatni toza saqlaymiz
    except TelegramBadRequest:
        pass
    text, total = await menu_text(session, f, lang)
    if smsg:
        try:
            await bot.edit_message_text(text, chat_id=message.chat.id, message_id=smsg,
                                        reply_markup=search_kb(lang, f, total))
            return
        except TelegramBadRequest:
            pass
    await message.answer(text, reply_markup=search_kb(lang, f, total))


# ---------- 🔔 Obunalar ----------
def _same(a: dict, b: dict) -> bool:
    a, b = clean(a), clean(b)
    a.pop("sort"), b.pop("sort")
    return a == b


@router.callback_query(SrchCb.filter(F.a == "sub"))
async def cb_subscribe(call: CallbackQuery, session: AsyncSession, user: User, lang: str) -> None:
    f = get_f(user)
    rows = (await session.execute(select(SavedSearch).where(SavedSearch.user_id == user.id))).scalars().all()
    if any(_same(r.filters, f) for r in rows):
        await call.answer(t(lang, "alert_dup"), show_alert=True)
        return
    if len(rows) >= config.max_alerts:
        await call.answer(t(lang, "alert_limit", n=config.max_alerts), show_alert=True)
        return
    session.add(SavedSearch(user_id=user.id, filters=f))
    await session.commit()
    await call.answer(t(lang, "alert_saved"), show_alert=True)


async def show_alerts(event: Message | CallbackQuery, session: AsyncSession, user: User, lang: str) -> None:
    rows = (await session.execute(select(SavedSearch).where(SavedSearch.user_id == user.id)
                                  .order_by(SavedSearch.id))).scalars().all()
    if not rows:
        await show_screen(event, t(lang, "alerts_empty"), alerts_kb(lang, []))
        return
    lines = [t(lang, "alerts_title"), ""]
    items = []
    for i, r in enumerate(rows, 1):
        d = describe(r.filters, lang)
        lines.append(f"{i}. {escape(d)}")
        items.append((r.id, f"{i}. {d}"))
    await show_screen(event, "\n".join(lines), alerts_kb(lang, items))


@router.message(Command("alerts"))
async def cmd_alerts(message: Message, session: AsyncSession, user: User, lang: str) -> None:
    await show_alerts(message, session, user, lang)


@router.callback_query(AlertCb.filter(F.a == "del"))
async def cb_alert_del(call: CallbackQuery, callback_data: AlertCb, session: AsyncSession, user: User,
                       lang: str) -> None:
    row = await session.get(SavedSearch, callback_data.id)
    if row and row.user_id == user.id:
        await session.delete(row)
        await session.commit()
    await show_alerts(call, session, user, lang)
    await call.answer(t(lang, "alert_deleted"))


# ---------- Erkin matn: shunchaki yozilgan so'z — qidiruv ----------
fallback_router = Router(name="search_fallback")


@fallback_router.message(StateFilter(None), F.text, ~F.text.startswith("/"), ~F.text.in_(MENU_TEXTS))
async def free_text(message: Message, session: AsyncSession, user: User, lang: str) -> None:
    f = get_f(user)
    f["q"] = message.text.strip()[:60]
    await save_f(session, user, f)
    await show_results(message, session, user, lang)


@fallback_router.message(StateFilter(None), F.text.startswith("/"))
async def unknown_command(message: Message, lang: str) -> None:
    await message.answer(t(lang, "unknown"))

