"""Oflayn test: Telegram serverisiz butun oqimni simulyatsiya qiladi.

Ishga tushirish:  python -m tests.test_flow
"""
import asyncio
import hashlib
import hmac
import json
import os
import sys
import tempfile
import time
from datetime import datetime
from itertools import count
from pathlib import Path
from urllib.parse import urlencode

DB = Path(tempfile.gettempdir()) / "gb_test.db"
DB.unlink(missing_ok=True)
TOKEN = "123456:TEST"
os.environ.update(BOT_TOKEN=TOKEN, ADMIN_IDS="1", DATABASE_URL=f"sqlite+aiosqlite:///{DB.as_posix()}",
                  CHANNEL="@eakkbozor", WEBAPP_URL="https://example.test")

from aiogram import Bot  # noqa: E402
from aiogram.client.default import DefaultBotProperties  # noqa: E402
from aiogram.client.session.base import BaseSession  # noqa: E402
from aiogram.methods import TelegramMethod  # noqa: E402
from aiogram.types import (CallbackQuery, Chat, InlineQuery, Message, PhotoSize, PreCheckoutQuery,  # noqa: E402
                           SuccessfulPayment, Update, User)

from bot.__main__ import build_dispatcher  # noqa: E402
from bot.db.base import init_db  # noqa: E402
from bot.services.search import parse_price_range  # noqa: E402

msg_ids = count(1000)
upd_ids = count(1)
calls: list[tuple[str, dict]] = []


class FakeSession(BaseSession):
    async def make_request(self, bot, method: TelegramMethod, timeout=None):
        name = type(method).__name__
        calls.append((name, method.model_dump(exclude_none=True)))
        chat_id = getattr(method, "chat_id", 1) or 1
        chat = Chat(id=chat_id if isinstance(chat_id, int) else -100, type="private")
        msg = Message(message_id=next(msg_ids), date=datetime.now(), chat=chat, text="x",
                      photo=[PhotoSize(file_id="x", file_unique_id="x", width=1, height=1)])
        if name in ("SendMessage", "SendPhoto", "EditMessageText", "EditMessageCaption", "EditMessageMedia",
                    "SendInvoice", "CopyMessage"):
            return msg
        if name == "SendMediaGroup":
            return [msg]
        return True

    async def close(self):
        pass

    async def stream_content(self, *a, **k):
        yield b""


U_ADMIN = User(id=1, is_bot=False, first_name="Admin", username="admin1")
U_SELLER = User(id=2, is_bot=False, first_name="Ali", username="ali_seller")
U_BUYER = User(id=3, is_bot=False, first_name="Vali", username="vali", language_code="ru")


def m(user, text=None, photo=False, mgid=None, **kw):
    return Update(update_id=next(upd_ids), message=Message(
        message_id=next(msg_ids), date=datetime.now(), chat=Chat(id=user.id, type="private"), from_user=user,
        text=text, media_group_id=mgid,
        photo=[PhotoSize(file_id=f"ph{next(msg_ids)}", file_unique_id="u", width=1, height=1)] if photo else None,
        **kw))


def cb(user, data, photo=False):
    return Update(update_id=next(upd_ids), callback_query=CallbackQuery(
        id=str(next(upd_ids)), from_user=user, chat_instance="x", data=data,
        message=Message(message_id=next(msg_ids), date=datetime.now(), chat=Chat(id=user.id, type="private"),
                        text=None if photo else "msg",
                        photo=[PhotoSize(file_id="p", file_unique_id="p", width=1, height=1)] if photo else None)))


def last(name, chat_id=None):
    rows = [c for c in calls if c[0] == name and (chat_id is None or c[1].get("chat_id") == chat_id)]
    return rows[-1][1]


def text_of(c: dict) -> str:
    return c.get("text") or c.get("caption") or ""


def last_out(chat_id=None) -> str:
    """Oxirgi chiqqan matn (yuborilgan yoki tahrirlangan)."""
    for name, c in reversed(calls):
        if name in ("SendMessage", "EditMessageText", "SendPhoto", "EditMessageMedia"):
            if chat_id is None or c.get("chat_id") in (chat_id, None):
                return text_of(c) or text_of(c.get("media", {}))
    return ""


def init_data(user: User) -> str:
    fields = {"auth_date": str(int(time.time())), "query_id": "q1",
              "user": json.dumps({"id": user.id, "first_name": user.first_name}, separators=(",", ":"))}
    dcs = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", TOKEN.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, dcs.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


async def main():
    # 0) Narx oralig'ini o'qish
    assert parse_price_range("500k-2mln") == (500_000, 2_000_000)
    assert parse_price_range("1 500 000") == (1_500_000, None)
    assert parse_price_range("1mln gacha") == (None, 1_000_000)
    assert parse_price_range("до 300 тыс") == (None, 300_000)
    assert parse_price_range("300ming - 1.5mln") == (300_000, 1_500_000)

    await init_db()
    bot = Bot(TOKEN, session=FakeSession(), default=DefaultBotProperties(parse_mode="HTML"))
    dp = build_dispatcher(throttle_rate=0)

    async def feed(u):
        await dp.feed_update(bot, u)

    # 1) Start → til → bot haqida + qo'llanma + qoidalar
    await feed(m(U_SELLER, "/start ads_test1"))
    assert "Tilni tanlang" in last("SendMessage")["text"]
    await feed(cb(U_SELLER, "lang:uz"))
    welcome = last("SendMessage")
    assert "garant (kafil) emasmiz" in welcome["text"].replace("<b>", "").replace("</b>", "")
    btns = [b["text"] for row in welcome["reply_markup"]["inline_keyboard"] for b in row]
    assert "📖 Qo'llanma" in btns and any("roziman" in b for b in btns), btns
    await feed(cb(U_SELLER, "g:0"))
    assert "Qo'llanma 1/5" in last("EditMessageText")["text"]
    await feed(cb(U_SELLER, "g:4"))
    assert "firibgar" in last("EditMessageText")["text"]
    await feed(cb(U_SELLER, "d:rules:"))
    assert "javobgarlik olmaymiz" in last("EditMessageText")["text"]

    # Qoidaga rozi bo'lmasdan e'lon berib bo'lmaydi
    await feed(m(U_SELLER, "/sell"))
    assert "Gamebozor qoidalari" in last("SendMessage")["text"]
    await feed(cb(U_SELLER, "d:accept:"))
    assert any("Rahmat" in text_of(c) for n, c in calls[-4:] if n == "SendMessage")
    assert "Dashboard" in last("SendMessage")["text"]

    # 2) E'lon berish
    await feed(m(U_SELLER, "➕ E'lon berish"))
    await feed(cb(U_SELLER, "sell:type:account"))
    kb = str(last("SendMessage")["reply_markup"])
    assert "PUBG Mobile" in kb and "eFootball" in kb  # PUBG bo'limi ochiq
    await feed(cb(U_SELLER, "sell:game:efootball"))
    await feed(m(U_SELLER, "TS 3250, 18 Epic, Messi"))
    await feed(cb(U_SELLER, "sell:opt:0"))        # platform Android
    await feed(cb(U_SELLER, "sell:opt:0"))        # binding KONAMI ID
    await feed(m(U_SELLER, "3250"))               # team strength
    await feed(m(U_SELLER, "abc"))                # noto'g'ri raqam
    assert "Faqat raqam" in last("SendMessage")["text"]
    await feed(m(U_SELLER, "18"))                 # epic
    await feed(m(U_SELLER, "5"))                  # bigtime
    await feed(m(U_SELLER, "Messi 103, Mbappe 102"))
    await feed(m(U_SELLER, "Epic Ballon d'Or, POTW"))  # packs
    await feed(m(U_SELLER, "12 500"))             # coins
    await feed(cb(U_SELLER, "sell:skip:"))         # gp (ixtiyoriy)
    await feed(cb(U_SELLER, "sell:opt:0"))        # division
    await feed(cb(U_SELLER, "sell:opt:1"))        # donat yo'q
    await feed(m(U_SELLER, "1 500 000 so'm"))      # narx
    await feed(cb(U_SELLER, "sell:neg:1"))
    await feed(m(U_SELLER, "Tez sotaman, almashinuv ham bor"))
    await asyncio.gather(*(feed(m(U_SELLER, photo=True, mgid="G1")) for _ in range(3)))  # albom
    await feed(cb(U_SELLER, "sell:photos_done:"))
    await feed(cb(U_SELLER, "sell:contact_me:"))
    preview = last("SendPhoto")["caption"]
    print("---- PREVIEW ----\n" + preview)
    assert "Messi 103" in preview and "1 500 000" in preview and "POTW" in preview

    # Xaridor oldindan obuna bo'ladi: eFootball, TS ≥ 3200, «messi», 1–3 mln
    await feed(m(U_BUYER, "/start"))
    await feed(cb(U_BUYER, "lang:ru"))
    await feed(cb(U_BUYER, "d:accept:"))
    await feed(m(U_BUYER, "🔎 Поиск"))
    menu = last("SendMessage")["text"]
    assert "Поиск" in menu and "все игры" in menu, menu
    await feed(cb(U_BUYER, "s:sg:efootball::0"))
    assert "eFootball" in last("EditMessageText")["text"]
    await feed(cb(U_BUYER, "s:f:team_strength::0"))
    assert "не меньше" in last("EditMessageText")["text"]
    await feed(cb(U_BUYER, "s:set:team_strength:3200:0"))
    await feed(cb(U_BUYER, "s:f:top_players::0"))
    await feed(m(U_BUYER, "messi"))               # matn kiritish → filtr
    await feed(cb(U_BUYER, "s:price:::0"))
    await feed(m(U_BUYER, "1mln-3mln"))
    menu = last("EditMessageText")["text"]
    print("---- SEARCH MENU ----\n" + menu)
    assert "1M–3M" in menu and "«messi»" in menu and "≥3200" in menu
    assert "Найдено: <b>0</b>" in menu
    await feed(cb(U_BUYER, "s:sub:::0"))
    assert "сохранена" in last("AnswerCallbackQuery")["text"]
    await feed(cb(U_BUYER, "s:sub:::0"))
    assert "уже подписаны" in last("AnswerCallbackQuery")["text"]

    await feed(cb(U_SELLER, "sell:submit:"))
    assert "moderatsiyaga yuborildi" in last("SendMessage", 2)["text"]
    assert last("SendPhoto")["chat_id"] == 1  # adminga keldi

    # 3) Admin tasdiqlaydi → kanal + obunachiga xabar
    await feed(cb(U_ADMIN, "mod:ok:1:"))
    ch = [c for c in calls if c[0] == "SendPhoto" and c[1]["chat_id"] == "@eakkbozor"]
    assert ch, "kanalga chiqmadi"
    print("---- CHANNEL ----\n" + ch[-1][1]["caption"])
    hit = last("SendMessage", 3)["text"]
    assert "подписке" in hit and "#1" in hit, hit
    print("---- ALERT ----\n" + hit)

    # 4) Dashboard bo'limlari
    await feed(m(U_BUYER, "/menu"))
    home = last("SendMessage")["text"]
    assert "Активных: <b>1</b>" in home, home
    await feed(cb(U_BUYER, "d:games:"))
    kb = last("EditMessageText")["reply_markup"]["inline_keyboard"]
    assert any("eFootball · 1" in b["text"] for row in kb for b in row)
    assert any("🔜" in b["text"] for row in kb for b in row)
    await feed(cb(U_BUYER, "d:game:efootball"))
    game_page = last("EditMessageText")["text"]
    print("---- GAME PAGE ----\n" + game_page)
    assert "1 500 000" in game_page and "3 250" in game_page
    await feed(cb(U_BUYER, "d:profile:"))
    assert "r_3" in last("EditMessageText")["text"]
    await feed(cb(U_BUYER, "d:info:"))
    await feed(cb(U_BUYER, "d:cmds:"))
    assert "/search" in last("EditMessageText")["text"]

    # 5) Qidiruv natijalari: tez havola, filtr, erkin matn
    await feed(cb(U_BUYER, "s:quick:efootball:strong:0"))
    res = last("SendPhoto", 3)
    assert "Messi 103" in res["caption"] and "1 / 1" not in str(res["reply_markup"])
    await feed(cb(U_BUYER, "s:quick:efootball:p4:0"))  # 3 mln+ → bo'sh
    assert "ничего не найдено" in last("AnswerCallbackQuery")["text"]
    await feed(m(U_BUYER, "mbappe"))                  # erkin matn
    assert "Mbappe 102" in last("SendPhoto", 3)["caption"]
    await feed(m(U_BUYER, "/search ronaldo"))
    assert "ничего не найдено" in last_out(3)
    await feed(m(U_BUYER, "/search POTW"))
    assert "#1" in last("SendPhoto", 3)["caption"]
    await feed(cb(U_BUYER, "s:reset:::0"))
    await feed(cb(U_BUYER, "s:f:platform::0"))
    await feed(cb(U_BUYER, "s:ch:platform::1"))       # iOS → bo'sh
    assert "Найдено: <b>0</b>" in last("EditMessageText")["text"]
    await feed(cb(U_BUYER, "s:ch:platform::0"))       # Android
    assert "Найдено: <b>1</b>" in last("EditMessageText")["text"]
    await feed(cb(U_BUYER, "s:show:::0"))
    await feed(cb(U_BUYER, "s:pg:::0", photo=True))   # karusel — tahrirlash
    assert last("EditMessageMedia")

    # 6) Kartochka amallari
    await feed(cb(U_BUYER, "it:fav:1"))
    await feed(cb(U_BUYER, "it:contact:1"))
    assert any(c[0] == "SendMessage" and c[1]["chat_id"] == 2 and "qiziqishdi" in c[1]["text"] for c in calls)
    await feed(m(U_BUYER, "/check @ali_seller"))
    print("---- CHECK ----\n" + last("SendMessage")["text"])
    await feed(m(U_BUYER, "/l1"))
    assert "Messi" in last("SendPhoto", 3)["caption"]

    # 7) Firibgar tekshiruvi
    await feed(m(U_ADMIN, "/blacklist @scammer pul olib qochgan"))
    await feed(m(U_BUYER, "🛡 Проверить продавца"))
    await feed(m(U_BUYER, "@Scammer"))
    assert "ЧЁРНОМ" in last("SendMessage")["text"]

    # 8) Inline rejim
    await feed(Update(update_id=next(upd_ids), inline_query=InlineQuery(
        id="iq1", from_user=U_BUYER, query="messi", offset="")))
    iq = last("AnswerInlineQuery")
    assert len(iq["results"]) == 1 and iq["results"][0]["id"] == "1"
    await feed(Update(update_id=next(upd_ids), inline_query=InlineQuery(
        id="iq2", from_user=U_BUYER, query="#1", offset="")))
    assert len(last("AnswerInlineQuery")["results"]) == 1

    # 9) Mini App API
    from aiohttp.test_utils import TestClient, TestServer
    from bot.web.server import build_app
    async with TestClient(TestServer(build_app(bot))) as client:
        r = await client.post("/api/search", json={"initData": "bad", "filters": {}})
        assert r.status == 401
        good = init_data(U_BUYER)
        r = await client.post("/api/meta", json={"initData": good})
        meta = await r.json()
        assert meta["lang"] == "ru" and meta["games"][0]["filters"]
        r = await client.post("/api/search", json={"initData": good, "filters": {
            "g": "efootball", "min": {"team_strength": 3000}, "tx": {"packs": "potw"}}})
        data = await r.json()
        assert data["total"] == 1 and data["items"][0]["id"] == 1, data
        r = await client.post("/api/open", json={"initData": good, "id": 1})
        assert (await r.json())["ok"] is True
        r = await client.get("/")
        assert r.status == 200 and "Gamebozor" in await r.text()
    print("---- MINI APP API ✓ ----")

    # 10) TOP: Stars to'lovi
    await feed(cb(U_SELLER, "top:1:3"))
    inv = last("SendInvoice")
    assert inv["currency"] == "XTR" and inv["prices"][0]["amount"] == 50
    await feed(Update(update_id=next(upd_ids), pre_checkout_query=PreCheckoutQuery(
        id="pc1", from_user=U_SELLER, currency="XTR", total_amount=50, invoice_payload="top3:1")))
    assert last("AnswerPreCheckoutQuery")["ok"] is True
    await feed(m(U_SELLER, successful_payment=SuccessfulPayment(
        currency="XTR", total_amount=50, invoice_payload="top3:1",
        telegram_payment_charge_id="ch_1", provider_payment_charge_id="")))
    assert "TOP" in last("SendMessage", 2)["text"]

    # 10b) Narxni tushirish → saralagan xaridorga xabar, kanal posti yangilanadi
    await feed(cb(U_SELLER, "it:price:1"))
    assert "1 500 000" in last("SendMessage", 2)["text"]
    await feed(m(U_SELLER, "1 200 000"))
    assert "1 200 000" in last("SendMessage", 2)["text"]
    drop = last("SendMessage", 3)["text"]
    assert "Цена снижена" in drop and "<s>1 500 000</s>" in drop, drop
    assert "<s>1 500 000</s>" in last("EditMessageMedia")["media"]["caption"]
    print("---- PRICE DROP ----\n" + drop)

    # 10c) 💎 PRO: xarid → bepul TOP → belgi → avto-ko'tarish
    await feed(m(U_SELLER, "/pro"))
    assert "PRO sotuvchi" in last("SendMessage", 2)["text"]
    await feed(cb(U_SELLER, "pro:buy:30"))
    inv = last("SendInvoice")
    assert inv["payload"] == "pro30:2" and inv["prices"][0]["amount"] == 250 and inv["currency"] == "XTR"
    await feed(Update(update_id=next(upd_ids), pre_checkout_query=PreCheckoutQuery(
        id="pc2", from_user=U_SELLER, currency="XTR", total_amount=250, invoice_payload="pro30:2")))
    assert last("AnswerPreCheckoutQuery")["ok"] is True
    await feed(Update(update_id=next(upd_ids), pre_checkout_query=PreCheckoutQuery(
        id="pc3", from_user=U_BUYER, currency="XTR", total_amount=250, invoice_payload="pro30:2")))
    assert last("AnswerPreCheckoutQuery")["ok"] is False  # boshqa odamning PRO to'lovi
    await feed(m(U_SELLER, successful_payment=SuccessfulPayment(
        currency="XTR", total_amount=250, invoice_payload="pro30:2",
        telegram_payment_charge_id="ch_pro", provider_payment_charge_id="")))
    assert "PRO faollashtirildi" in last("SendMessage", 2)["text"]
    await feed(cb(U_SELLER, "it:top:1"))
    assert "it:topfree:1" in str(last("SendMessage", 2)["reply_markup"])
    await feed(cb(U_SELLER, "it:topfree:1"))
    assert "Bepul TOP ishlatildi" in last("SendMessage", 2)["text"]
    await feed(cb(U_SELLER, "it:topfree:1"))
    assert "qolmagan" in last("AnswerCallbackQuery")["text"]
    await feed(m(U_BUYER, "/l1"))
    assert "💎 PRO" in last("SendPhoto", 3)["caption"]

    from datetime import timedelta as _td
    from bot.db.base import Session as _S
    from bot.db.models import Listing as _L
    from bot.services.pro import bump_pro_listings
    async with _S() as s:
        lst = await s.get(_L, 1)
        lst.approved_at = lst.approved_at - _td(days=3)
        await s.commit()
        assert await bump_pro_listings(s) == 1
        assert await bump_pro_listings(s) == 0  # 48 soat o'tmaguncha qayta ko'tarilmaydi
    await feed(m(U_ADMIN, "/givepro 3 7"))
    assert "PRO активирован" in last("SendMessage", 3)["text"]

    # 11) Sotildi → banner «SOTILDI», bog'langan xaridordan baho so'raladi
    await feed(cb(U_SELLER, "it:sold:1"))
    assert "SOTILDI" in last("EditMessageMedia")["media"]["caption"]
    ask = last("SendMessage", 3)
    assert "продано" in ask["text"] and "rv:r:1:5" in str(ask["reply_markup"]), ask["text"]

    # 11b) Reyting va sharh
    await feed(cb(U_SELLER, "rv:ask:1:0"))
    assert "самого себя" in last("AnswerCallbackQuery")["text"] or "o'zingizga" in last("AnswerCallbackQuery")["text"].lower()
    await feed(cb(U_BUYER, "rv:r:1:5"))
    assert "Оценка принята" in last("SendMessage", 3)["text"]
    assert "★★★★★" in last("SendMessage", 2)["text"]  # sotuvchiga xabar
    await feed(m(U_BUYER, "Hammasi halol, tez topshirdi"))
    assert "Спасибо" in last("SendMessage", 3)["text"]
    await feed(cb(U_BUYER, "rv:r:1:4"))
    assert "уже оценили" in last("AnswerCallbackQuery")["text"]
    await feed(m(U_BUYER, "/check @ali_seller"))
    chk = last("SendMessage")["text"]
    assert "5.0" in chk and "halol" in chk, chk
    print("---- CHECK + REVIEWS ----\n" + chk)
    await feed(m(U_BUYER, "/l1"))
    assert "⭐️ 5.0 (1" in last("SendPhoto", 3)["caption"]

    # Kanal posti haqiqatan banner rasm bilan chiqqanmi
    ch_photo = [c for c in calls if c[0] == "SendPhoto" and c[1]["chat_id"] == "@eakkbozor"][0][1]["photo"]
    assert not isinstance(ch_photo, str), "banner o'rniga skrinshot chiqdi"

    # 12) Admin statistika
    await feed(cb(U_ADMIN, "adm:stats"))
    print("---- STATS ----\n" + last("SendMessage")["text"])
    await feed(cb(U_ADMIN, "adm:sources"))
    assert "ads_test1" in last("SendMessage")["text"]

    # 13) Coin xizmati e'loni (admin — darhol chiqadi)
    await feed(m(U_ADMIN, "/start"))
    await feed(cb(U_ADMIN, "lang:uz"))
    await feed(cb(U_ADMIN, "d:accept:"))
    await feed(m(U_ADMIN, "➕ E'lon berish"))
    await feed(cb(U_ADMIN, "sell:type:topup"))
    await feed(cb(U_ADMIN, "sell:game:efb_coin"))
    await feed(m(U_ADMIN, "eFootball coin arzon va tez"))
    await feed(cb(U_ADMIN, "sell:opt:3"))   # PC/Steam
    await feed(cb(U_ADMIN, "sell:opt:2"))   # login orqali -> ogohlantirish
    await feed(cb(U_ADMIN, "sell:opt:0"))   # 5-30 min
    await feed(m(U_ADMIN, "130 coin — 17 000\n1040 coin — 137 000"))
    await feed(cb(U_ADMIN, "sell:skip:"))
    await feed(m(U_ADMIN, "17000"))
    await feed(cb(U_ADMIN, "sell:skip:"))
    await feed(m(U_ADMIN, photo=True))
    await feed(cb(U_ADMIN, "sell:photos_done:"))
    await feed(cb(U_ADMIN, "sell:contact_me:"))
    await feed(cb(U_ADMIN, "sell:submit:"))
    ch = [c for c in calls if c[0] == "SendPhoto" and c[1]["chat_id"] == "@eakkbozor"][-1][1]["caption"]
    print("---- COIN XIZMATI ----\n" + ch)
    assert "dan boshlab" in ch and "login/paroli" in ch
    await feed(m(U_BUYER, "🪙 Coin / UC"))
    await feed(cb(U_BUYER, "d:game:efb_coin"))
    await feed(cb(U_BUYER, "s:quick:efb_coin:top:0"))
    assert "Coin" in last("SendPhoto", 3)["caption"]

    # 14) Obunani o'chirish
    await feed(m(U_BUYER, "/alerts"))
    assert "🗑" in str(last("SendMessage")["reply_markup"])
    await feed(cb(U_BUYER, "al:del:1"))
    assert "Подписок нет" in last("EditMessageText")["text"]

    # 15) Noma'lum buyruq
    await feed(m(U_BUYER, "/qwerty"))
    assert "/menu" in last("SendMessage")["text"]

    errors = [c for c in calls if c[0] == "AnswerCallbackQuery" and c[1].get("show_alert")]
    print(f"\n✅ Barcha tekshiruvlar o'tdi. API chaqiruvlar: {len(calls)}, alertlar: {len(errors)}")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
