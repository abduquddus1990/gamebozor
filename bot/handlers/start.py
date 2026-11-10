"""/start (onboarding), til tanlash, yordam."""
from aiogram import Bot, F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.callbacks import LangCb
from bot.config import config
from bot.db.models import User
from bot.handlers.common import show_single
from bot.handlers.dashboard import send_home
from bot.i18n import all_variants, t
from bot.keyboards import dash_info_kb, lang_kb, main_menu, welcome_kb

router = Router(name="start")


async def _welcome(message: Message, user: User, lang: str, name: str) -> None:
    await message.answer(t(lang, "welcome", name=name), reply_markup=welcome_kb(lang, bool(user.rules_accepted_at)))


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject, state: FSMContext, session: AsyncSession, bot: Bot,
                    user: User, lang: str, is_admin: bool) -> None:
    await state.clear()
    arg = command.args or ""

    # Deep-link parametrlar:
    #   l_123      — kanal postidan / ulashilgan havoladan e'lonni ochish
    #   r_<id>     — referal
    #   ads_xxx    — Telegram Ads kampaniyasi (statistika uchun)
    if user.source is None and arg and not arg.startswith("l_"):
        if arg.startswith("r_") and arg[2:].isdigit() and int(arg[2:]) != user.id:
            user.referred_by = int(arg[2:])
            user.source = "referral"
        else:
            user.source = arg[:64]
        await session.commit()

    if user.lang is None:
        # Yangi foydalanuvchi: avval til, keyin bot haqida + qo'llanma + qoidalar
        if arg.startswith("l_"):
            await state.update_data(after_lang=arg)
        await message.answer(t(lang, "choose_lang"), reply_markup=lang_kb())
        return

    if arg.startswith("l_") and arg[2:].isdigit():
        await message.answer(t(lang, "menu"), reply_markup=main_menu(lang, is_admin))
        await show_single(bot, message.chat.id, session, int(arg[2:]), lang, user.id)
        return

    if not user.rules_accepted_at:
        await _welcome(message, user, lang, message.from_user.first_name)
        return
    # Qaytgan foydalanuvchi: pastki menyu + Dashboard
    await message.answer(t(lang, "menu"), reply_markup=main_menu(lang, is_admin))
    await send_home(message, session, user, lang, is_admin)


@router.callback_query(LangCb.filter())
async def set_lang(call: CallbackQuery, callback_data: LangCb, state: FSMContext, session: AsyncSession, bot: Bot,
                   user: User, is_admin: bool) -> None:
    first_time = user.lang is None
    user.lang = callback_data.code
    await session.commit()
    lang = user.lang
    try:
        await call.message.delete()
    except Exception:  # noqa: BLE001
        pass
    if first_time or not user.rules_accepted_at:
        await _welcome(call.message, user, lang, call.from_user.first_name)
    else:
        await call.message.answer(t(lang, "lang_set"), reply_markup=main_menu(lang, is_admin))

    after = (await state.get_data()).get("after_lang") or ""
    if after.startswith("l_") and after[2:].isdigit():
        await state.update_data(after_lang=None)
        await show_single(bot, call.message.chat.id, session, int(after[2:]), lang, user.id)
    await call.answer()


@router.message(Command("lang"))
@router.message(F.text.in_(all_variants("btn_lang")))
async def change_lang(message: Message, lang: str) -> None:
    await message.answer(t(lang, "choose_lang"), reply_markup=lang_kb())


@router.message(Command("help"))
@router.message(F.text.in_(all_variants("btn_help")))
async def cmd_help(message: Message, lang: str) -> None:
    await message.answer(t(lang, "help", channel=config.channel), reply_markup=dash_info_kb(lang))


@router.message(Command("paysupport"))
async def cmd_paysupport(message: Message, lang: str) -> None:
    await message.answer(t(lang, "paysupport", support=config.support))


@router.callback_query(F.data == "noop")
async def noop(call: CallbackQuery) -> None:
    await call.answer()
