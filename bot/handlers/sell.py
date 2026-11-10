"""E'lon berish — bosqichma-bosqich forma (FSM).

Maydonlar o'yin shablonidan (services/games.py) avtomatik olinadi.
"""
import asyncio
from collections import defaultdict

from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import SellCb
from bot.config import config
from bot.db.models import Listing, User
from bot.handlers.common import require_rules
from bot.i18n import MENU_TEXTS, all_variants, t
from bot.keyboards import (confirm_kb, contact_kb, field_kb, games_kb, main_menu, photos_done_kb,
                           skip_cancel_kb, type_kb, yes_no_kb)
from bot.services.games import GAMES, active_games
from bot.services.listings import approve, send_to_moderation, user_open_count
from bot.services.pro import is_pro, listing_limit
from bot.services.render import render_listing
from bot.states import SellForm

router = Router(name="sell")
NOT_MENU = ~F.text.in_(MENU_TEXTS) & ~F.text.startswith("/")

# Albom rasmlari parallel keladi — har foydalanuvchi uchun qulf
_photo_locks: defaultdict[int, asyncio.Lock] = defaultdict(asyncio.Lock)


# ---------- Boshlash ----------
@router.message(Command("sell"))
@router.message(F.text.in_(all_variants("btn_sell")))
async def sell_start(message: Message, state: FSMContext, session: AsyncSession, user: User,
                     lang: str, is_admin: bool) -> None:
    await state.clear()
    if not await require_rules(message, user, lang):
        return
    limit = listing_limit(user)
    if not is_admin and await user_open_count(session, user.id) >= limit:
        hint = "" if is_pro(user) else t(lang, "pro_hint", n=config.pro_listing_limit)
        await message.answer(t(lang, "limit_reached", n=limit) + hint)
        return
    if not user.username:
        await message.answer(t(lang, "need_username"))
    if active_games("topup") and active_games("account"):
        await message.answer(t(lang, "choose_type"), reply_markup=type_kb(lang))
    else:
        await _choose_game(message, state, active_games(), lang)


async def _choose_game(message: Message, state: FSMContext, games: list, lang: str) -> None:
    if len(games) == 1:
        await _begin(message, state, games[0].code, lang)
    else:
        await message.answer(t(lang, "choose_game"), reply_markup=games_kb(games))


@router.callback_query(SellCb.filter(F.a == "type"))
async def sell_type(call: CallbackQuery, callback_data: SellCb, state: FSMContext, lang: str) -> None:
    await call.message.delete()
    await _choose_game(call.message, state, active_games(callback_data.v), lang)
    await call.answer()


@router.callback_query(SellCb.filter(F.a == "game"))
async def sell_game(call: CallbackQuery, callback_data: SellCb, state: FSMContext, lang: str) -> None:
    await call.message.delete()
    await _begin(call.message, state, callback_data.v, lang)
    await call.answer()


async def _begin(message: Message, state: FSMContext, game: str, lang: str) -> None:
    await state.set_state(SellForm.title)
    await state.update_data(game=game, fields={}, fi=0, photos=[])
    g = GAMES[game]
    await message.answer(f"{g.emoji} <b>{g.name}</b>\n\n" + t(lang, "ask_title"),
                         reply_markup=skip_cancel_kb(lang))


@router.callback_query(SellCb.filter(F.a == "cancel"))
async def sell_cancel(call: CallbackQuery, state: FSMContext, lang: str, is_admin: bool) -> None:
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(t(lang, "cancelled"), reply_markup=main_menu(lang, is_admin))
    await call.answer()


@router.message(SellForm.title, F.text, NOT_MENU)
async def sell_title(message: Message, state: FSMContext, lang: str) -> None:
    await state.update_data(title=message.text.strip()[:120])
    await state.set_state(SellForm.field)
    await _ask_field(message, state, lang)


# ---------- O'yinga xos maydonlar ----------
async def _ask_field(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    game = GAMES[data["game"]]
    fi = data["fi"]
    if fi >= len(game.fields):
        await state.set_state(SellForm.price)
        key = "ask_price_topup" if game.kind == "topup" else "ask_price"
        await message.answer(t(lang, key), reply_markup=skip_cancel_kb(lang))
        return
    f = game.fields[fi]
    text = t(lang, "ask_field", icon=f.icon, label=f.label(lang))
    if f.type == "choice":
        await message.answer(text, reply_markup=field_kb(lang, f))
    else:
        await message.answer(text, reply_markup=skip_cancel_kb(lang, skip=not f.required))


async def _save_field(message: Message, state: FSMContext, lang: str, value) -> None:
    data = await state.get_data()
    f = GAMES[data["game"]].fields[data["fi"]]
    fields = data["fields"]
    if value is not None:
        fields[f.key] = value
    await state.update_data(fields=fields, fi=data["fi"] + 1)
    await _ask_field(message, state, lang)


@router.callback_query(SellForm.field, SellCb.filter(F.a == "opt"))
async def field_option(call: CallbackQuery, callback_data: SellCb, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    f = GAMES[data["game"]].fields[data["fi"]]
    value = f.options[int(callback_data.v)]
    await call.message.edit_text(f"{call.message.html_text}\n➡️ <b>{value}</b>")
    await _save_field(call.message, state, lang, value)
    await call.answer()


@router.callback_query(SellForm.field, SellCb.filter(F.a == "skip"))
async def field_skip(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await call.message.edit_reply_markup(reply_markup=None)
    await _save_field(call.message, state, lang, None)
    await call.answer()


@router.message(SellForm.field, F.text, NOT_MENU)
async def field_text(message: Message, state: FSMContext, lang: str) -> None:
    data = await state.get_data()
    f = GAMES[data["game"]].fields[data["fi"]]
    if f.type == "choice":
        await message.answer(t(lang, "ask_field", icon=f.icon, label=f.label(lang)), reply_markup=field_kb(lang, f))
        return
    raw = message.text.strip()
    if f.type == "int":
        digits = raw.replace(" ", "").replace(",", "").replace(".", "")
        if not digits.isdigit() or len(digits) > 12:
            await message.answer(t(lang, "bad_int"))
            return
        await _save_field(message, state, lang, int(digits))
    else:
        await _save_field(message, state, lang, raw[:400])


# ---------- Narx ----------
@router.message(SellForm.price, F.text, NOT_MENU)
async def sell_price(message: Message, state: FSMContext, lang: str) -> None:
    digits = "".join(ch for ch in message.text if ch.isdigit())
    if not digits or not (1_000 <= int(digits) <= 1_000_000_000):
        await message.answer(t(lang, "bad_price"))
        return
    await state.update_data(price=int(digits))
    if GAMES[(await state.get_data())["game"]].kind == "topup":
        # Xizmat e'lonida "kelishuv" so'ralmaydi
        await state.update_data(negotiable=False)
        await state.set_state(SellForm.description)
        await message.answer(t(lang, "ask_desc"), reply_markup=skip_cancel_kb(lang, skip=True))
        return
    await state.set_state(SellForm.negotiable)
    await message.answer(t(lang, "ask_negotiable"), reply_markup=yes_no_kb(lang))


@router.callback_query(SellForm.negotiable, SellCb.filter(F.a == "neg"))
async def sell_negotiable(call: CallbackQuery, callback_data: SellCb, state: FSMContext, lang: str) -> None:
    await state.update_data(negotiable=callback_data.v == "1")
    await call.message.edit_reply_markup(reply_markup=None)
    await state.set_state(SellForm.description)
    await call.message.answer(t(lang, "ask_desc"), reply_markup=skip_cancel_kb(lang, skip=True))
    await call.answer()


# ---------- Izoh ----------
async def _ask_photos(message: Message, state: FSMContext, lang: str) -> None:
    await state.set_state(SellForm.photos)
    await message.answer(t(lang, "ask_photos", n=config.max_photos), reply_markup=photos_done_kb(lang))


@router.message(SellForm.description, F.text, NOT_MENU)
async def sell_desc(message: Message, state: FSMContext, lang: str) -> None:
    await state.update_data(description=message.text.strip()[:500])
    await _ask_photos(message, state, lang)


@router.callback_query(SellForm.description, SellCb.filter(F.a == "skip"))
async def sell_desc_skip(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    await state.update_data(description="")
    await call.message.edit_reply_markup(reply_markup=None)
    await _ask_photos(call.message, state, lang)
    await call.answer()


# ---------- Rasmlar ----------
@router.message(SellForm.photos, F.photo)
async def sell_photo(message: Message, state: FSMContext, lang: str) -> None:
    async with _photo_locks[message.from_user.id]:
        data = await state.get_data()
        photos: list[str] = data.get("photos", [])
        if len(photos) >= config.max_photos:
            if not message.media_group_id or data.get("last_group") != message.media_group_id:
                await message.answer(t(lang, "photo_limit", n=config.max_photos))
            await state.update_data(last_group=message.media_group_id)
            return
        photos.append(message.photo[-1].file_id)  # eng yuqori sifat
        await state.update_data(photos=photos)
        # Albomda har rasmga javob bermaslik uchun — guruh bo'yicha bitta javob
        first_in_group = not message.media_group_id or data.get("last_group") != message.media_group_id
        await state.update_data(last_group=message.media_group_id)
    if first_in_group:
        await asyncio.sleep(1.0)  # albomning qolgan rasmlari yetib kelsin
        n = len((await state.get_data()).get("photos", []))
        await message.answer(t(lang, "photo_added", n=n, max=config.max_photos), reply_markup=photos_done_kb(lang))


@router.callback_query(SellForm.photos, SellCb.filter(F.a == "photos_done"))
async def sell_photos_done(call: CallbackQuery, state: FSMContext, user: User, lang: str) -> None:
    if not (await state.get_data()).get("photos"):
        await call.answer(t(lang, "need_photo"), show_alert=True)
        return
    await call.message.edit_reply_markup(reply_markup=None)
    await state.set_state(SellForm.contact)
    me = f"@{user.username}" if user.username else f"ID {user.id}"
    await call.message.answer(t(lang, "ask_contact", username=me), reply_markup=contact_kb(lang, me))
    await call.answer()


# ---------- Kontakt ----------
@router.callback_query(SellForm.contact, SellCb.filter(F.a == "contact_me"))
async def sell_contact_me(call: CallbackQuery, state: FSMContext, user: User, lang: str) -> None:
    contact = f"@{user.username}" if user.username else f"tg://user?id={user.id}"
    await call.message.edit_reply_markup(reply_markup=None)
    await _preview(call.message, state, contact, user, lang)
    await call.answer()


@router.message(SellForm.contact, F.text, NOT_MENU)
async def sell_contact_text(message: Message, state: FSMContext, user: User, lang: str) -> None:
    await _preview(message, state, message.text.strip()[:64], user, lang)


async def _build(data: dict, user: User) -> Listing:
    return Listing(
        seller_id=user.id, game=data["game"], title=data.get("title", "")[:120], price=data["price"],
        negotiable=data.get("negotiable", False), data=data.get("fields", {}),
        description=data.get("description", ""), contact=data["contact"], photos=data["photos"],
    )


async def _preview(message: Message, state: FSMContext, contact: str, user: User, lang: str) -> None:
    await state.update_data(contact=contact)
    await state.set_state(SellForm.confirm)
    data = await state.get_data()
    preview = await _build(data, user)
    preview.id = 0
    await message.answer(t(lang, "preview"))
    await message.answer_photo(data["photos"][0], caption=render_listing(preview, lang),
                               reply_markup=confirm_kb(lang))


# ---------- Tasdiqlash ----------
@router.callback_query(SellForm.confirm, SellCb.filter(F.a == "restart"))
async def sell_restart(call: CallbackQuery, state: FSMContext, lang: str) -> None:
    game = (await state.get_data())["game"]
    await call.message.edit_reply_markup(reply_markup=None)
    await _begin(call.message, state, game, lang)
    await call.answer()


@router.callback_query(SellForm.confirm, SellCb.filter(F.a == "submit"))
async def sell_submit(call: CallbackQuery, state: FSMContext, session: AsyncSession, bot: Bot,
                      user: User, lang: str, is_admin: bool) -> None:
    data = await state.get_data()
    await state.clear()
    await call.message.edit_reply_markup(reply_markup=None)
    listing = await _build(data, user)
    session.add(listing)
    await session.commit()

    if is_admin:
        await approve(bot, session, listing)
        await call.message.answer(t(lang, "published_admin", id=listing.id), reply_markup=main_menu(lang, True))
    else:
        await send_to_moderation(bot, listing, pro=is_pro(user))
        await call.message.answer(t(lang, "submitted", id=listing.id), reply_markup=main_menu(lang, False))
    await call.answer()
