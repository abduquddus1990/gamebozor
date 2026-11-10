"""Ishga tushirish: python -m bot"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, BotCommandScopeChat, BotCommandScopeDefault, MenuButtonCommands

from bot.config import config
from bot.db.base import init_db
from bot.handlers import admin, catalog, dashboard, inline, my_listings, search, sell, start
from bot.middlewares import DbMiddleware, ThrottleMiddleware

log = logging.getLogger(__name__)

# «/» menyusidagi buyruqlar (Dashboard'dan alohida, tez kirish uchun)
COMMANDS = {
    "uz": [
        ("menu", "🏠 Dashboard"), ("search", "🔎 Qidiruv (masalan: /search messi)"),
        ("catalog", "🛒 Akkauntlar katalogi"), ("topup", "🪙 Coin / UC xizmatlari"),
        ("sell", "➕ E'lon berish"), ("my", "📂 Mening e'lonlarim"), ("fav", "❤️ Saralanganlar"),
        ("alerts", "🔔 Qidiruv obunalarim"), ("check", "🛡 Sotuvchini tekshirish"),
        ("rules", "📜 Qoidalar"), ("safety", "🛡 Xavfsiz savdo"), ("guide", "📖 Qo'llanma"),
        ("commands", "⌨️ Barcha buyruqlar"), ("lang", "🌐 Til"), ("help", "ℹ️ Yordam"),
        ("paysupport", "💬 To'lov bo'yicha yordam"), ("start", "🔄 Qayta boshlash"),
    ],
    "ru": [
        ("menu", "🏠 Dashboard"), ("search", "🔎 Поиск (например: /search messi)"),
        ("catalog", "🛒 Каталог аккаунтов"), ("topup", "🪙 Услуги Coin / UC"),
        ("sell", "➕ Подать объявление"), ("my", "📂 Мои объявления"), ("fav", "❤️ Избранное"),
        ("alerts", "🔔 Мои подписки на поиск"), ("check", "🛡 Проверить продавца"),
        ("rules", "📜 Правила"), ("safety", "🛡 Безопасная сделка"), ("guide", "📖 Руководство"),
        ("commands", "⌨️ Все команды"), ("lang", "🌐 Язык"), ("help", "ℹ️ Помощь"),
        ("paysupport", "💬 Поддержка по оплатам"), ("start", "🔄 Перезапуск"),
    ],
}
ADMIN_COMMANDS = [
    ("admin", "🛠 Admin panel"), ("ban", "ID — bloklash"), ("unban", "ID — blokdan chiqarish"),
    ("verify", "ID — ✅ tasdiqlangan sotuvchi"), ("blacklist", "@user izoh — qora ro'yxat"),
    ("unblacklist", "@user — qora ro'yxatdan olish"), ("refund", "CHARGE_ID — Stars qaytarish"),
]

# Bo'sh chatda ko'rinadigan matn («Bu bot nima qila oladi?») — shu bo'lsa Telegram
# stiker/smaylik taklif qilish o'rniga katta «START / BOSHLASH» tugmasini ko'rsatadi.
DESCRIPTION = {
    "uz": ("🎮 Gamebozor — o'yin akkauntlari e'lonlari bozori.\n\n"
           "🔎 eFootball va boshqa o'yinlar akkauntlarini umumiy ko'rsatkich, o'yinchilar, packlar va narx bo'yicha izlang\n"
           "➕ O'z akkauntingizni bepul sotuvga qo'ying\n"
           "🛡 Sotuvchini firibgarlar ro'yxatidan tekshiring\n"
           "🔔 Mos e'lon chiqsa xabar oling\n\n"
           "⚠️ Biz garant emasmiz va to'lovlar uchun javobgar emasmiz.\n\n"
           "Boshlash uchun «START» tugmasini bosing 👇"),
    "ru": ("🎮 Gamebozor — доска объявлений игровых аккаунтов.\n\n"
           "🔎 Ищите аккаунты eFootball и других игр по общему показателю, игрокам, пакам и цене\n"
           "➕ Бесплатно выставляйте свой аккаунт\n"
           "🛡 Проверяйте продавца по списку мошенников\n"
           "🔔 Получайте уведомления о подходящих объявлениях\n\n"
           "⚠️ Мы не гарант и не отвечаем за платежи.\n\n"
           "Нажмите «START», чтобы начать 👇"),
}
SHORT_DESCRIPTION = {
    "uz": "🎮 O'yin akkauntlari bozori: qidiruv, filtrlar, e'lonlar. Kanal: @eakkbozor",
    "ru": "🎮 Рынок игровых аккаунтов: поиск, фильтры, объявления. Канал: @eakkbozor",
}


async def setup_bot_profile(bot: Bot) -> None:
    """Buyruqlar menyusi, tavsif va menyu tugmasi. Xato bo'lsa bot baribir ishlayveradi."""
    try:
        for lang, cmds in COMMANDS.items():
            await bot.set_my_commands([BotCommand(command=c, description=d) for c, d in cmds],
                                      scope=BotCommandScopeDefault(), language_code=None if lang == "uz" else lang)
        await bot.set_chat_menu_button(menu_button=MenuButtonCommands())
        for lang in ("uz", "ru"):
            code = None if lang == "uz" else lang
            await bot.set_my_description(description=DESCRIPTION[lang], language_code=code)
            await bot.set_my_short_description(short_description=SHORT_DESCRIPTION[lang], language_code=code)
    except TelegramAPIError as e:
        log.warning("Bot profilini sozlab bo'lmadi: %s", e)
    admin_cmds = [BotCommand(command=c, description=d) for c, d in COMMANDS["uz"] + ADMIN_COMMANDS]
    for admin_id in config.admin_ids:
        try:
            await bot.set_my_commands(admin_cmds, scope=BotCommandScopeChat(chat_id=admin_id))
        except TelegramAPIError:
            pass  # admin hali botga /start bosmagan


def build_dispatcher(throttle_rate: float = 0.3) -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage())
    throttle, db = ThrottleMiddleware(throttle_rate), DbMiddleware()
    for observer in (dp.message, dp.callback_query):
        observer.outer_middleware(throttle)
        observer.outer_middleware(db)
    dp.pre_checkout_query.outer_middleware(db)
    dp.inline_query.outer_middleware(db)

    # Tartib muhim: admin birinchi (moderatsiya tugmalari), oxirida — erkin matnli qidiruv
    dp.include_routers(admin.router, start.router, dashboard.router, search.router, sell.router,
                       my_listings.router, catalog.router, inline.router, search.fallback_router)
    return dp


async def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    if not config.bot_token:
        raise SystemExit("BOT_TOKEN topilmadi — .env faylni to'ldiring (.env.example dan nusxa oling).")

    await init_db()
    bot = Bot(config.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = build_dispatcher()
    await setup_bot_profile(bot)

    runner = None
    if config.webapp_url:
        from bot.web.server import start_web
        runner = await start_web(bot)

    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("Gamebozor bot ishga tushdi")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        if runner:
            await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
