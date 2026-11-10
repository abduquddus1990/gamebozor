from aiogram.types import (InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup,
                           SwitchInlineQueryChosenChat, WebAppInfo)
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.callbacks import (AdminCb, AlertCb, DashCb, GuideCb, ItemCb, LangCb, ModCb, SellCb, SrchCb,
                           TopCb)
from bot.config import config
from bot.i18n import PRICE_LABELS, REJECT_REASONS, t
from bot.services.games import GAMES, Field, Game, active_games, short_label, soon_games
from bot.services.render import fmt_short


def lang_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data=LangCb(code="uz").pack()),
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data=LangCb(code="ru").pack()),
    ]])


def main_menu(lang: str, is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Pastki doimiy klaviatura — eng ko'p ishlatiladigan bo'limlar."""
    first = [KeyboardButton(text=t(lang, "btn_dash")), KeyboardButton(text=t(lang, "btn_search"))]
    if config.webapp_url:
        first.append(KeyboardButton(text=t(lang, "btn_webapp"), web_app=WebAppInfo(url=f"{config.webapp_url}/?lang={lang}")))
    rows = [
        first,
        [KeyboardButton(text=t(lang, "btn_buy")), KeyboardButton(text=t(lang, "btn_topup"))],
        [KeyboardButton(text=t(lang, "btn_sell")), KeyboardButton(text=t(lang, "btn_my"))],
        [KeyboardButton(text=t(lang, "btn_fav")), KeyboardButton(text=t(lang, "btn_check"))],
        [KeyboardButton(text=t(lang, "btn_rules")), KeyboardButton(text=t(lang, "btn_lang"))],
    ]
    if is_admin:
        rows.append([KeyboardButton(text=t(lang, "btn_admin"))])
    return ReplyKeyboardMarkup(keyboard=rows, resize_keyboard=True, is_persistent=True,
                               input_field_placeholder="🔎 messi 3200 …")


# ---------- Onboarding ----------
def welcome_kb(lang: str, accepted: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_guide"), callback_data=GuideCb(p=0).pack())
    kb.button(text=t(lang, "btn_rules"), callback_data=DashCb(a="rules").pack())
    if not accepted:
        kb.button(text=t(lang, "btn_accept"), callback_data=DashCb(a="accept").pack())
    kb.button(text=t(lang, "btn_to_dash"), callback_data=DashCb(a="home").pack())
    kb.adjust(2, 1, 1)
    return kb.as_markup()


def guide_kb(lang: str, page: int, total: int, accepted: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    nav = 0
    if page > 0:
        kb.button(text=t(lang, "btn_prev"), callback_data=GuideCb(p=page - 1).pack())
        nav += 1
    kb.button(text=f"{'●' * (page + 1)}{'○' * (total - page - 1)}", callback_data="noop")
    nav += 1
    if page < total - 1:
        kb.button(text=t(lang, "btn_next"), callback_data=GuideCb(p=page + 1).pack())
        nav += 1
    sizes = [nav]
    if page == total - 1:
        kb.button(text=t(lang, "btn_rules"), callback_data=DashCb(a="rules").pack())
        sizes.append(1)
        if not accepted:
            kb.button(text=t(lang, "btn_accept"), callback_data=DashCb(a="accept").pack())
            sizes.append(1)
    kb.button(text=t(lang, "d_home"), callback_data=DashCb(a="home").pack())
    sizes.append(1)
    kb.adjust(*sizes)
    return kb.as_markup()


def rules_kb(lang: str, accepted: bool, back: str = "info") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if not accepted:
        kb.button(text=t(lang, "btn_accept"), callback_data=DashCb(a="accept").pack())
    kb.button(text=t(lang, "d_safety"), callback_data=DashCb(a="safety").pack())
    kb.button(text=t(lang, "btn_back"), callback_data=DashCb(a=back).pack())
    kb.adjust(*([1, 2] if not accepted else [2]))
    return kb.as_markup()


# ---------- Dashboard ----------
def dash_home_kb(lang: str, is_admin: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for a, key in (("games", "d_games"), ("search", "d_search"), ("topup", "d_topup"), ("sell", "d_sell"),
                   ("my", "d_my"), ("fav", "d_fav"), ("alerts", "d_alerts"), ("profile", "d_profile"),
                   ("check", "d_check"), ("info", "d_info")):
        if a == "search":
            kb.button(text=t(lang, key), callback_data=SrchCb(a="menu").pack())
        else:
            kb.button(text=t(lang, key), callback_data=DashCb(a=a).pack())
    kb.adjust(2)
    if config.webapp_url:
        kb.row(InlineKeyboardButton(text=t(lang, "d_webapp"),
                                    web_app=WebAppInfo(url=f"{config.webapp_url}/?lang={lang}")))
    kb.row(InlineKeyboardButton(text=t(lang, "d_refresh"), callback_data=DashCb(a="home", v="r").pack()))
    return kb.as_markup()


def dash_games_kb(lang: str, kind: str, counts: dict[str, int]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for g in active_games(kind):
        kb.button(text=f"{g.emoji} {g.name} · {counts.get(g.code, 0)}", callback_data=DashCb(a="game", v=g.code).pack())
    for g in soon_games(kind):
        kb.button(text=f"🔜 {g.name}", callback_data=DashCb(a="soon", v=g.code).pack())
    kb.adjust(1)
    kb.row(InlineKeyboardButton(text=t(lang, "d_search"), callback_data=SrchCb(a="menu").pack()),
           InlineKeyboardButton(text=t(lang, "d_home"), callback_data=DashCb(a="home").pack()))
    return kb.as_markup()


def dash_game_kb(lang: str, game: Game, has_items: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    g = game.code
    if has_items:
        kb.button(text=t(lang, "d_browse"), callback_data=SrchCb(a="quick", k=g, v="top").pack())
        kb.button(text=t(lang, "d_filter"), callback_data=SrchCb(a="sg", k=g).pack())
        kb.button(text=t(lang, "d_cheap"), callback_data=SrchCb(a="quick", k=g, v="cheap").pack())
        if game.kind == "account":
            kb.button(text=t(lang, "d_strong"), callback_data=SrchCb(a="quick", k=g, v="strong").pack())
        kb.button(text=t(lang, "d_newest"), callback_data=SrchCb(a="quick", k=g, v="new").pack())
        for code, label in PRICE_LABELS.items():
            kb.button(text=f"💵 {label}", callback_data=SrchCb(a="quick", k=g, v=code).pack())
        kb.adjust(*([2, 2, 1, 2, 2] if game.kind == "account" else [2, 2, 2, 2]))
    back = "topup" if game.kind == "topup" else "games"
    kb.row(InlineKeyboardButton(text=t(lang, "d_sell"), callback_data=DashCb(a="sell").pack()))
    kb.row(InlineKeyboardButton(text=t(lang, "btn_back"), callback_data=DashCb(a=back).pack()),
           InlineKeyboardButton(text=t(lang, "d_home"), callback_data=DashCb(a="home").pack()))
    return kb.as_markup()


def dash_info_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_rules"), callback_data=DashCb(a="rules").pack())
    kb.button(text=t(lang, "d_safety"), callback_data=DashCb(a="safety").pack())
    kb.button(text=t(lang, "btn_guide"), callback_data=GuideCb(p=0).pack())
    kb.button(text=t(lang, "d_commands"), callback_data=DashCb(a="cmds").pack())
    kb.button(text=t(lang, "d_lang"), callback_data=DashCb(a="lang").pack())
    kb.button(text=t(lang, "d_home"), callback_data=DashCb(a="home").pack())
    kb.adjust(2, 2, 2)
    return kb.as_markup()


def back_kb(lang: str, back: str = "home") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if back != "home":
        kb.button(text=t(lang, "btn_back"), callback_data=DashCb(a=back).pack())
    kb.button(text=t(lang, "d_home"), callback_data=DashCb(a="home").pack())
    kb.adjust(2)
    return kb.as_markup()


def profile_kb(lang: str, ref_link: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "d_my"), callback_data=DashCb(a="my").pack())
    kb.button(text=t(lang, "d_alerts"), callback_data=DashCb(a="alerts").pack())
    kb.adjust(2)
    share = ("🎮 Gamebozor — o'yin akkauntlari bozori 👉 " if lang != "ru" else "🎮 Gamebozor — рынок игровых аккаунтов 👉 ")
    kb.row(InlineKeyboardButton(text="🎁 " + ("Do'stga yuborish" if lang != "ru" else "Отправить другу"),
                                url=f"https://t.me/share/url?url={ref_link}&text={share}"))
    kb.row(InlineKeyboardButton(text=t(lang, "d_home"), callback_data=DashCb(a="home").pack()))
    return kb.as_markup()


# ---------- Qidiruv ----------
def _price_text(f: dict) -> str:
    lo, hi = f.get("pmin"), f.get("pmax")
    if lo and hi:
        return f"{fmt_short(lo)}–{fmt_short(hi)}"
    if lo:
        return f"≥{fmt_short(lo)}"
    if hi:
        return f"≤{fmt_short(hi)}"
    return ""


def _field_value(f: dict, fld: Field) -> str:
    if fld.filter == "min" and fld.key in f.get("min", {}):
        return f"≥{fmt_short(int(f['min'][fld.key]))}"
    if fld.filter == "choice" and fld.key in f.get("ch", {}):
        return str(f["ch"][fld.key]).split(" / ")[0]
    if fld.filter == "text" and fld.key in f.get("tx", {}):
        return f"«{f['tx'][fld.key]}»"
    return ""


def _btn(label: str, value: str) -> str:
    return f"✓ {label}: {value}" if value else label


def search_kb(lang: str, f: dict, total: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    game = GAMES.get(f.get("g", ""))
    game_name = f"{game.emoji} {game.name}" if game else t(lang, "search_any_game")
    kb.button(text=f"{t(lang, 's_game')}: {game_name}", callback_data=SrchCb(a="game").pack())
    kb.button(text=f"{t(lang, 's_sort')}: {t(lang, 'sort_' + f.get('sort', 'top')).split(' ', 1)[0]}",
              callback_data=SrchCb(a="sort").pack())
    kb.button(text=_btn(t(lang, "s_price"), _price_text(f)), callback_data=SrchCb(a="price").pack())
    kb.button(text=_btn(t(lang, "s_text"), f"«{f['q']}»" if f.get("q") else ""), callback_data=SrchCb(a="q").pack())
    sizes = [2, 2]
    if game:
        n = 0
        for fld in game.filter_fields:
            kb.button(text=_btn(f"{fld.icon} {short_label(fld, lang)}", _field_value(f, fld)),
                      callback_data=SrchCb(a="f", k=fld.key).pack())
            n += 1
        sizes += [2] * (n // 2) + ([1] if n % 2 else [])
    kb.button(text=("✅ " if f.get("ver") else "☑️ ") + t(lang, "s_verified_plain"), callback_data=SrchCb(a="ver").pack())
    kb.button(text=t(lang, "s_reset"), callback_data=SrchCb(a="reset").pack())
    kb.button(text=t(lang, "s_subscribe"), callback_data=SrchCb(a="sub").pack())
    kb.button(text=t(lang, "s_show", n=total), callback_data=SrchCb(a="show").pack())
    kb.button(text=t(lang, "d_home"), callback_data=DashCb(a="home").pack())
    sizes += [1, 2, 1, 1]
    kb.adjust(*sizes)
    return kb.as_markup()


def search_game_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🎮 " + t(lang, "search_any_game"), callback_data=SrchCb(a="sg", k="").pack())
    for g in active_games():
        kb.button(text=f"{g.emoji} {g.name}", callback_data=SrchCb(a="sg", k=g.code).pack())
    kb.button(text=t(lang, "btn_back"), callback_data=SrchCb(a="menu").pack())
    kb.adjust(1)
    return kb.as_markup()


def search_price_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, label in PRICE_LABELS.items():
        kb.button(text=f"💵 {label}", callback_data=SrchCb(a="pp", v=code).pack())
    kb.button(text=t(lang, "s_any"), callback_data=SrchCb(a="pp", v="all").pack())
    kb.button(text=t(lang, "btn_back"), callback_data=SrchCb(a="menu").pack())
    kb.adjust(2, 2, 2)
    return kb.as_markup()


def search_field_kb(lang: str, fld: Field, active: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    sizes: list[int] = []
    if fld.filter == "min":
        for v in fld.presets:
            kb.button(text=f"≥ {fmt_short(v)}", callback_data=SrchCb(a="set", k=fld.key, v=str(v)).pack())
        n = len(fld.presets)
        sizes += [3] * (n // 3) + ([n % 3] if n % 3 else [])
    elif fld.filter == "choice":
        for i, opt in enumerate(fld.options):
            kb.button(text=opt, callback_data=SrchCb(a="ch", k=fld.key, i=i).pack())
        n = len(fld.options)
        sizes += [2] * (n // 2) + ([1] if n % 2 else [])
    if active:
        kb.button(text=t(lang, "s_clear_one"), callback_data=SrchCb(a="rm", k=fld.key).pack())
        sizes.append(1)
    kb.button(text=t(lang, "btn_back"), callback_data=SrchCb(a="menu").pack())
    sizes.append(1)
    kb.adjust(*sizes)
    return kb.as_markup()


def search_text_kb(lang: str, key: str, active: bool) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if active:
        kb.button(text=t(lang, "s_clear_one"), callback_data=SrchCb(a="rm", k=key).pack())
    kb.button(text=t(lang, "btn_back"), callback_data=SrchCb(a="menu").pack())
    kb.adjust(1)
    return kb.as_markup()


def search_sort_kb(lang: str, f: dict) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    sorts = ["top", "new", "cheap", "exp"]
    game = GAMES.get(f.get("g", ""))
    if game and any(x.filter == "min" for x in game.fields) and game.kind == "account":
        sorts.append("strong")
    for s in sorts:
        mark = "• " if f.get("sort", "top") == s else ""
        kb.button(text=mark + t(lang, f"sort_{s}"), callback_data=SrchCb(a="so", v=s).pack())
    kb.button(text=t(lang, "btn_back"), callback_data=SrchCb(a="menu").pack())
    kb.adjust(1)
    return kb.as_markup()


def result_kb(lang: str, listing_id: int, idx: int, total: int, is_fav: bool) -> InlineKeyboardMarkup:
    """Qidiruv natijalari karuseli (bitta xabar tahrirlanadi)."""
    kb = InlineKeyboardBuilder()
    sizes = []
    if total > 1:
        kb.button(text="◀️", callback_data=SrchCb(a="pg", i=(idx - 1) % total).pack())
        kb.button(text=f"{idx + 1} / {total}", callback_data="noop")
        kb.button(text="▶️", callback_data=SrchCb(a="pg", i=(idx + 1) % total).pack())
        sizes.append(3)
    _item_buttons(kb, lang, listing_id, is_fav)
    sizes += [2, 2]
    kb.button(text=t(lang, "s_filters"), callback_data=SrchCb(a="menu").pack())
    kb.button(text=t(lang, "d_home"), callback_data=DashCb(a="home").pack())
    sizes.append(2)
    kb.adjust(*sizes)
    return kb.as_markup()


def _item_buttons(kb: InlineKeyboardBuilder, lang: str, listing_id: int, is_fav: bool) -> None:
    kb.button(text=t(lang, "btn_contact"), callback_data=ItemCb(a="contact", id=listing_id).pack())
    kb.button(text="💔" if is_fav else "❤️", callback_data=ItemCb(a="fav", id=listing_id).pack())
    kb.button(text=t(lang, "btn_share"), switch_inline_query_chosen_chat=SwitchInlineQueryChosenChat(
        query=f"#{listing_id}", allow_user_chats=True, allow_group_chats=True, allow_channel_chats=True))
    kb.button(text="🚩", callback_data=ItemCb(a="report", id=listing_id).pack())


def card_kb(lang: str, listing_id: int, is_fav: bool = False) -> InlineKeyboardMarkup:
    """Bitta e'lon kartochkasi (deep-link, saralanganlar, obuna xabari)."""
    kb = InlineKeyboardBuilder()
    _item_buttons(kb, lang, listing_id, is_fav)
    kb.adjust(2, 2)
    return kb.as_markup()


def alerts_kb(lang: str, items: list[tuple[int, str]]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for aid, label in items:
        kb.button(text=f"🗑 {label}"[:60], callback_data=AlertCb(a="del", id=aid).pack())
    kb.button(text=t(lang, "d_search"), callback_data=SrchCb(a="menu").pack())
    kb.button(text=t(lang, "d_home"), callback_data=DashCb(a="home").pack())
    kb.adjust(*([1] * len(items)), 2)
    return kb.as_markup()


def open_listing_kb(lang: str, listing_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="👀 " + ("Ochish" if lang != "ru" else "Открыть"),
                             callback_data=ItemCb(a="view", id=listing_id).pack())
    ]])


def channel_post_kb(listing_id: int) -> InlineKeyboardMarkup:
    url = f"https://t.me/{config.bot_username}?start=l_{listing_id}"
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🛒 Batafsil / Подробнее", url=url)
    ]])


# ---------- E'lon berish ----------
def type_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "type_account"), callback_data=SellCb(a="type", v="account").pack())
    kb.button(text=t(lang, "type_topup"), callback_data=SellCb(a="type", v="topup").pack())
    kb.adjust(1)
    return kb.as_markup()


def games_kb(games: list[Game]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for g in games:
        kb.button(text=f"{g.emoji} {g.name}", callback_data=SellCb(a="game", v=g.code).pack())
    kb.adjust(2)
    return kb.as_markup()


def field_kb(lang: str, f: Field) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i, opt in enumerate(f.options):
        kb.button(text=opt, callback_data=SellCb(a="opt", v=str(i)).pack())
    if not f.required:
        kb.button(text=t(lang, "btn_skip"), callback_data=SellCb(a="skip").pack())
    kb.button(text=t(lang, "btn_cancel"), callback_data=SellCb(a="cancel").pack())
    n = len(f.options)
    kb.adjust(*([2] * (n // 2) + ([1] if n % 2 else []) + [1] * (1 + (not f.required))))
    return kb.as_markup()


def skip_cancel_kb(lang: str, skip: bool = False) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if skip:
        kb.button(text=t(lang, "btn_skip"), callback_data=SellCb(a="skip").pack())
    kb.button(text=t(lang, "btn_cancel"), callback_data=SellCb(a="cancel").pack())
    kb.adjust(1)
    return kb.as_markup()


def yes_no_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_yes"), callback_data=SellCb(a="neg", v="1").pack())
    kb.button(text=t(lang, "btn_no"), callback_data=SellCb(a="neg", v="0").pack())
    kb.adjust(2)
    return kb.as_markup()


def photos_done_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_done"), callback_data=SellCb(a="photos_done").pack())
    kb.button(text=t(lang, "btn_cancel"), callback_data=SellCb(a="cancel").pack())
    kb.adjust(1)
    return kb.as_markup()


def contact_kb(lang: str, username: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=username, callback_data=SellCb(a="contact_me").pack())
    kb.button(text=t(lang, "btn_cancel"), callback_data=SellCb(a="cancel").pack())
    kb.adjust(1)
    return kb.as_markup()


def confirm_kb(lang: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "btn_submit"), callback_data=SellCb(a="submit").pack())
    kb.button(text=t(lang, "btn_restart"), callback_data=SellCb(a="restart").pack())
    kb.button(text=t(lang, "btn_cancel"), callback_data=SellCb(a="cancel").pack())
    kb.adjust(1, 2)
    return kb.as_markup()


# ---------- Mening e'lonlarim ----------
def my_list_kb(items: list[tuple[int, str]], action: str = "open") -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for lid, label in items:
        kb.button(text=label, callback_data=ItemCb(a=action, id=lid).pack())
    kb.adjust(1)
    return kb.as_markup()


def owner_kb(lang: str, listing_id: int, status: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if status == "active":
        kb.button(text=t(lang, "btn_top"), callback_data=ItemCb(a="top", id=listing_id).pack())
        kb.button(text=t(lang, "btn_sold"), callback_data=ItemCb(a="sold", id=listing_id).pack())
    if status in ("active", "pending", "rejected"):
        kb.button(text=t(lang, "btn_delete"), callback_data=ItemCb(a="del", id=listing_id).pack())
    kb.adjust(1)
    return kb.as_markup()


def top_kb(lang: str, listing_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=t(lang, "top_3d", n=config.top_3d_stars), callback_data=TopCb(id=listing_id, days=3).pack())
    kb.button(text=t(lang, "top_7d", n=config.top_7d_stars), callback_data=TopCb(id=listing_id, days=7).pack())
    kb.adjust(1)
    return kb.as_markup()


# ---------- Moderatsiya / Admin ----------
def mod_kb(listing_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Tasdiqlash", callback_data=ModCb(a="ok", id=listing_id).pack())
    kb.button(text="❌ Rad etish", callback_data=ModCb(a="rej", id=listing_id).pack())
    kb.adjust(2)
    return kb.as_markup()


def reject_reasons_kb(listing_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for code, (uz, _) in REJECT_REASONS.items():
        kb.button(text=uz, callback_data=ModCb(a="reason", id=listing_id, r=code).pack())
    kb.adjust(1)
    return kb.as_markup()


def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📊 Statistika", callback_data=AdminCb(a="stats").pack())
    kb.button(text="⏳ Moderatsiyadagilar", callback_data=AdminCb(a="pending").pack())
    kb.button(text="📈 Reklama manbalari", callback_data=AdminCb(a="sources").pack())
    kb.button(text="📣 Hammaga xabar", callback_data=AdminCb(a="broadcast").pack())
    kb.adjust(2)
    return kb.as_markup()

