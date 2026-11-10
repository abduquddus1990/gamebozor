"""Inline rejim: istalgan chatda `@akkbozorbot messi 3200` yoki `@akkbozorbot #12`.

Yoqish: @BotFather → /setinline → botni tanlang → placeholder: «messi, TS 3200, #raqam»
"""
from aiogram import Router
from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, InlineQuery, InlineQueryResultCachedPhoto,
                           InlineQueryResultsButton)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import config
from bot.db.models import Listing, User
from bot.i18n import t
from bot.services.games import GAMES
from bot.services.render import fmt_price, render_listing
from bot.services.search import empty_filters, search

router = Router(name="inline")
PAGE = 20


def _open_kb(listing_id: int) -> InlineKeyboardMarkup:
    url = f"https://t.me/{config.bot_username}?start=l_{listing_id}"
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🛒 Batafsil / Подробнее", url=url)]])


@router.inline_query()
async def inline_search(query: InlineQuery, session: AsyncSession, user: User | None = None,
                        lang: str = "uz") -> None:
    text = (query.query or "").strip()
    offset = int(query.offset or 0)

    if text.startswith("#") and text[1:].isdigit():
        listing = await session.get(Listing, int(text[1:]))
        items = [listing] if listing and listing.status == "active" else []
    else:
        f = empty_filters("account", "")
        f["k"] = "account"
        if text:
            f["q"] = text[:60]
        items = await search(session, f)
        if not text:
            f["k"] = "topup"
            items += await search(session, f)

    results = []
    for l in items[offset:offset + PAGE]:
        game = GAMES.get(l.game)
        som = "сум" if lang == "ru" else "so'm"
        results.append(InlineQueryResultCachedPhoto(
            id=str(l.id),
            photo_file_id=l.photos[0],
            title=f"{game.emoji if game else ''} {l.title}"[:64],
            description=f"{fmt_price(l.price)} {som}",
            caption=render_listing(l, lang, for_channel=True),
            reply_markup=_open_kb(l.id),
        ))
    next_offset = str(offset + PAGE) if len(items) > offset + PAGE else ""
    await query.answer(
        results, cache_time=30, is_personal=False, next_offset=next_offset,
        button=InlineQueryResultsButton(text="🎮 Gamebozor — " + t(lang, "d_search"), start_parameter="inline"),
    )
