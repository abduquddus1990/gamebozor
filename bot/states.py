from aiogram.fsm.state import State, StatesGroup


class SellForm(StatesGroup):
    title = State()
    field = State()
    price = State()
    negotiable = State()
    description = State()
    photos = State()
    contact = State()
    confirm = State()


class ReportForm(StatesGroup):
    reason = State()


class CheckForm(StatesGroup):
    target = State()


class BroadcastForm(StatesGroup):
    message = State()
    confirm = State()


class SearchInput(StatesGroup):
    value = State()  # qidiruv filtri uchun matn kiritish (narx, raqam, so'z)
