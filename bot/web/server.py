"""📱 Mini App (vitrina) uchun kichik veb-server — bot bilan bitta jarayonda ishlaydi (aiohttp).

Endpointlar:
  GET  /                      → index.html (Telegram WebApp)
  POST /api/meta              → o'yinlar, filtr maydonlari, saralash turlari
  POST /api/search            → filtrlangan e'lonlar (sahifalab)
  POST /api/open              → e'lonni foydalanuvchining bot chatiga yuborish (aloqa tugmasi bilan)
  GET  /api/photo/{id}/{n}    → e'lon rasmi (Telegram'dan olib keshlanadi)

Har bir POST so'rovda Telegram `initData` imzosi tekshiriladi (bot tokeni bilan HMAC) —
begona sayt API'dan foydalana olmaydi.
"""
import json
import logging
from collections import OrderedDict
from pathlib import Path

from aiogram import Bot
from aiogram.utils.web_app import safe_parse_webapp_init_data
from aiohttp import web

from bot.config import config
from bot.db.base import Session
from bot.db.models import Listing, User
from bot.handlers.common import show_single
from bot.i18n import PRICE_LABELS, PRICE_RANGES, t
from bot.services.games import GAMES, active_games, short_label
from bot.services.render import fmt_price, is_top
from bot.services.search import SORTS, clean, search

log = logging.getLogger(__name__)
STATIC = Path(__file__).parent / "static"
PAGE = 24

_photo_cache: "OrderedDict[str, bytes]" = OrderedDict()
PHOTO_CACHE_MAX = 300


def _auth(request_data: dict) -> int:
    try:
        data = safe_parse_webapp_init_data(config.bot_token, request_data.get("initData", ""))
    except ValueError:
        raise web.HTTPUnauthorized(text="bad initData")
    if not data.user:
        raise web.HTTPUnauthorized(text="no user")
    return data.user.id


async def _body(request: web.Request) -> dict:
    try:
        return await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise web.HTTPBadRequest()


async def index(request: web.Request) -> web.Response:
    return web.FileResponse(STATIC / "index.html", headers={"Cache-Control": "no-cache"})


async def meta(request: web.Request) -> web.Response:
    body = await _body(request)
    uid = _auth(body)
    async with Session() as session:
        user = await session.get(User, uid)
        lang = (user.lang if user and user.lang else body.get("lang")) or "uz"
    games = []
    for g in active_games():
        games.append({
            "code": g.code, "name": g.name, "emoji": g.emoji, "kind": g.kind,
            "filters": [{"key": f.key, "type": f.filter, "label": short_label(f, lang), "icon": f.icon,
                         "options": list(f.options), "presets": list(f.presets)} for f in g.filter_fields],
        })
    return web.json_response({
        "lang": lang, "bot": config.bot_username, "games": games,
        "sorts": [{"key": s, "label": t(lang, f"sort_{s}")} for s in SORTS],
        "prices": [{"key": k, "label": v, "min": PRICE_RANGES[k][0] or None, "max": PRICE_RANGES[k][1]}
                   for k, v in PRICE_LABELS.items()],
        "rules": t(lang, "rules"),
    })


def _card(l: Listing, verified: bool, lang: str) -> dict:
    game = GAMES.get(l.game)
    fields = []
    if game:
        for f in game.fields:
            v = (l.data or {}).get(f.key)
            if v in (None, ""):
                continue
            fields.append({"key": f.key, "icon": f.icon, "label": short_label(f, lang),
                           "value": fmt_price(v) if isinstance(v, int) else str(v)})
    return {
        "id": l.id, "game": l.game, "emoji": game.emoji if game else "", "gameName": game.name if game else l.game,
        "kind": game.kind if game else "account", "title": l.title, "price": l.price, "priceText": fmt_price(l.price),
        "negotiable": l.negotiable, "top": is_top(l), "verified": verified, "views": l.views,
        "photos": len(l.photos), "fields": fields, "description": l.description[:300],
    }


async def api_search(request: web.Request) -> web.Response:
    body = await _body(request)
    uid = _auth(body)
    f = clean(body.get("filters") or {})
    offset = max(0, int(body.get("offset") or 0))
    async with Session() as session:
        user = await session.get(User, uid)
        lang = (user.lang if user and user.lang else body.get("lang")) or "uz"
        items = await search(session, f)
        page = items[offset:offset + PAGE]
        sellers = {u.id: u.is_verified for u in [await session.get(User, l.seller_id) for l in page] if u}
        cards = [_card(l, sellers.get(l.seller_id, False), lang) for l in page]
    return web.json_response({"total": len(items), "offset": offset, "items": cards,
                              "next": offset + PAGE if len(items) > offset + PAGE else None})


async def api_open(request: web.Request) -> web.Response:
    body = await _body(request)
    uid = _auth(body)
    bot: Bot = request.app["bot"]
    async with Session() as session:
        user = await session.get(User, uid)
        if not user or user.is_banned:
            raise web.HTTPForbidden()
        ok = await show_single(bot, uid, session, int(body.get("id") or 0), user.lang or "uz", uid)
    return web.json_response({"ok": ok})


async def api_photo(request: web.Request) -> web.Response:
    lid, n = int(request.match_info["id"]), int(request.match_info["n"])
    key = f"{lid}:{n}"
    if key in _photo_cache:
        _photo_cache.move_to_end(key)
        data = _photo_cache[key]
    else:
        async with Session() as session:
            listing = await session.get(Listing, lid)
        if not listing or listing.status not in ("active", "sold") or not (0 <= n < len(listing.photos)):
            raise web.HTTPNotFound()
        bot: Bot = request.app["bot"]
        file = await bot.get_file(listing.photos[n])
        buf = await bot.download_file(file.file_path)
        data = buf.read()
        _photo_cache[key] = data
        if len(_photo_cache) > PHOTO_CACHE_MAX:
            _photo_cache.popitem(last=False)
    return web.Response(body=data, content_type="image/jpeg", headers={"Cache-Control": "public, max-age=86400"})


def build_app(bot: Bot) -> web.Application:
    app = web.Application(client_max_size=64 * 1024)
    app["bot"] = bot
    app.router.add_get("/", index)
    app.router.add_post("/api/meta", meta)
    app.router.add_post("/api/search", api_search)
    app.router.add_post("/api/open", api_open)
    app.router.add_get(r"/api/photo/{id:\d+}/{n:\d+}", api_photo)
    return app


async def start_web(bot: Bot) -> web.AppRunner:
    runner = web.AppRunner(build_app(bot))
    await runner.setup()
    site = web.TCPSite(runner, config.web_host, config.web_port)
    await site.start()
    log.info("Mini App server: http://%s:%s  (tashqi: %s)", config.web_host, config.web_port, config.webapp_url)
    return runner
