"""Inline tugmalar uchun tiplashtirilgan callback_data (aiogram CallbackData). Limit — 64 bayt."""
from aiogram.filters.callback_data import CallbackData


class LangCb(CallbackData, prefix="lang"):
    code: str


class DashCb(CallbackData, prefix="d"):
    """Dashboard ekranlari: a=home|games|topup|game|info|rules|safety|cmds|profile|accept|sell|my|fav|alerts|check|lang;
    v=o'yin kodi yoki qo'shimcha qiymat."""
    a: str
    v: str = ""


class GuideCb(CallbackData, prefix="g"):
    p: int  # sahifa (0..4)


class SrchCb(CallbackData, prefix="s"):
    """Qidiruv: a=menu|game|sg|price|pp|f|set|ch|rm|q|sort|so|ver|reset|show|pg|sub|quick;
    k=maydon kaliti/qiymat; v=qiymat; i=indeks."""
    a: str
    k: str = ""
    v: str = ""
    i: int = 0


class AlertCb(CallbackData, prefix="al"):
    a: str  # del
    id: int


class ItemCb(CallbackData, prefix="it"):
    """E'lon ustidagi amallar: fav, contact, report, top, sold, del, open, view."""
    a: str
    id: int


class TopCb(CallbackData, prefix="top"):
    id: int
    days: int


class SellCb(CallbackData, prefix="sell"):
    """E'lon berish formasi: a=type|game|opt|skip|neg|photos_done|contact_me|submit|restart|cancel."""
    a: str
    v: str = ""


class ModCb(CallbackData, prefix="mod"):
    a: str  # ok | rej | reason
    id: int
    r: str = ""


class AdminCb(CallbackData, prefix="adm"):
    a: str  # stats | pending | broadcast | sources


class RevCb(CallbackData, prefix="rv"):
    """Sharh: a=ask (baholash oynasi) | r (baho, v=1..5) | no (sotib olmadim) | skip (izohsiz)."""
    a: str
    id: int
    v: int = 0
