"""Middleware'lar: DB sessiya, foydalanuvchini ro'yxatga olish, til, bloklash, antiflood."""
import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, PreCheckoutQuery, TelegramObject, User as TgUser

from bot.config import config
from bot.db.base import Session
from bot.db.models import User
from bot.i18n import t


class DbMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[TelegramObject, dict], Awaitable[Any]],
                       event: TelegramObject, data: dict[str, Any]) -> Any:
        async with Session() as session:
            data["session"] = session
            tg: TgUser | None = data.get("event_from_user")
            if tg is None or tg.is_bot:
                return await handler(event, data)

            user = await session.get(User, tg.id)
            if user is None:
                user = User(id=tg.id, username=tg.username, full_name=tg.full_name[:128])
                session.add(user)
                await session.commit()
            elif user.username != tg.username or user.full_name != tg.full_name[:128]:
                user.username = tg.username
                user.full_name = tg.full_name[:128]
                await session.commit()

            data["user"] = user
            data["lang"] = user.lang or ("ru" if (tg.language_code or "").startswith("ru") else "uz")
            data["is_admin"] = tg.id in config.admin_ids

            if user.is_banned and not data["is_admin"]:
                if isinstance(event, Message):
                    await event.answer(t(data["lang"], "banned"))
                elif isinstance(event, CallbackQuery):
                    await event.answer(t(data["lang"], "banned"), show_alert=True)
                elif isinstance(event, PreCheckoutQuery):
                    await event.answer(ok=False, error_message="Banned")
                return None
            return await handler(event, data)


class ThrottleMiddleware(BaseMiddleware):
    """Oddiy antiflood: bir foydalanuvchidan soniyasiga ~3 tadan ko'p so'rov bo'lsa e'tiborsiz."""

    def __init__(self, rate: float = 0.3) -> None:
        self.rate = rate
        self.last: dict[int, float] = {}

    async def __call__(self, handler, event: TelegramObject, data: dict[str, Any]) -> Any:
        tg: TgUser | None = data.get("event_from_user")
        # Rasmlar albom bo'lib keladi — ularni cheklamaymiz
        if tg and not (isinstance(event, Message) and (event.media_group_id or event.photo or event.successful_payment)):
            now = time.monotonic()
            if now - self.last.get(tg.id, 0) < self.rate:
                if isinstance(event, CallbackQuery):
                    await event.answer()
                return None
            self.last[tg.id] = now
            if len(self.last) > 50_000:
                self.last.clear()
        return await handler(event, data)
