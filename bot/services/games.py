"""O'yin shablonlari.

Yangi o'yin qo'shish uchun GAMES ga bitta yozuv qo'shish kifoya —
e'lon berish formasi (FSM) maydonlarni avtomatik so'raydi.

Maydon turlari:
  choice — tugmalardan tanlash (options)
  int    — butun son
  text   — erkin matn

Qidiruv (filter):
  "min"    — int maydon bo'yicha "kamida N" filtri (presets — tez tanlash tugmalari)
  "choice" — tanlov maydoni bo'yicha aniq moslik
  "text"   — matn ichidan qidirish (o'yinchi, pack nomi ...)
  ""       — qidiruvda ishtirok etmaydi
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Field:
    key: str
    uz: str
    ru: str
    type: str = "text"  # choice | int | text
    options: tuple[str, ...] = ()
    required: bool = True
    icon: str = "▫️"
    filter: str = ""  # "" | min | choice | text
    presets: tuple[int, ...] = ()  # "min" filtri uchun tez tanlash qiymatlari

    def label(self, lang: str) -> str:
        return self.ru if lang == "ru" else self.uz


@dataclass(frozen=True)
class Game:
    code: str
    name: str
    emoji: str
    fields: tuple[Field, ...] = field(default_factory=tuple)
    enabled: bool = True
    kind: str = "account"  # account — akkaunt savdosi | topup — coin/UC xizmati e'loni

    def field(self, key: str) -> "Field | None":
        return next((f for f in self.fields if f.key == key), None)

    @property
    def filter_fields(self) -> tuple["Field", ...]:
        return tuple(f for f in self.fields if f.filter)


EFOOTBALL = Game(
    code="efootball",
    name="eFootball",
    emoji="⚽️",
    fields=(
        Field("platform", "Platforma", "Платформа", "choice", ("Android", "iOS", "Android + iOS"),
              icon="📱", filter="choice"),
        Field("binding", "Akkaunt nimaga bog'langan", "Привязка аккаунта", "choice",
              ("KONAMI ID", "Google", "Game Center", "Facebook", "Apple ID", "X (Twitter)"),
              icon="🔗", filter="choice"),
        Field("team_strength", "Umumiy ko'rsatkich — Team Strength (masalan: 3250)",
              "Общий показатель — Team Strength (например: 3250)", "int", icon="💪",
              filter="min", presets=(2500, 2800, 3000, 3100, 3200, 3300)),
        Field("epic_count", "Epic o'yinchilar soni", "Кол-во Epic игроков", "int", icon="🟣",
              filter="min", presets=(1, 5, 10, 20, 30, 50)),
        Field("bigtime_count", "Big Time / Show Time soni", "Кол-во Big Time / Show Time", "int", icon="🟠",
              filter="min", presets=(1, 5, 10, 20, 30, 50)),
        Field("top_players", "Eng kuchli o'yinchilar (masalan: Messi 103, Mbappe 102)",
              "Лучшие игроки (например: Messi 103, Mbappe 102)", "text", icon="⭐️", filter="text"),
        Field("packs", "Packlar / maxsus kartalar (masalan: Epic Ballon d'Or, POTW, Highlight)",
              "Паки / особые карты (например: Epic Ballon d'Or, POTW, Highlight)", "text",
              required=False, icon="📦", filter="text"),
        Field("coins", "eFootball Coin miqdori", "Кол-во eFootball Coin", "int", icon="🪙",
              filter="min", presets=(100, 500, 1000, 3000, 5000, 10000)),
        Field("gp", "GP miqdori", "Кол-во GP", "int", required=False, icon="💰",
              filter="min", presets=(100_000, 500_000, 1_000_000, 5_000_000)),
        Field("division", "Division", "Дивизион", "choice",
              ("Division 1", "Division 2", "Division 3", "Division 4", "Division 5",
               "Division 6", "Division 7", "Division 8", "Division 9", "Division 10"),
              icon="🏆", filter="choice"),
        Field("donated", "Akkauntga donat qilinganmi?", "Был ли донат на аккаунт?", "choice",
              ("Ha / Да", "Yo'q / Нет"), icon="💳", filter="choice"),
    ),
)

PUBG_RANKS = ("Bronze", "Silver", "Gold", "Platinum", "Diamond", "Crown", "Ace", "Ace Master",
              "Ace Dominator", "Conqueror")

PUBGM = Game(
    code="pubgm",
    name="PUBG Mobile",
    emoji="🔫",
    fields=(
        Field("binding", "Akkaunt nimaga bog'langan", "Привязка аккаунта", "choice",
              ("Facebook", "Google", "X (Twitter)", "Apple ID", "Game Center", "VK"), icon="🔗", filter="choice"),
        Field("level", "Akkaunt darajasi (Level)", "Уровень аккаунта (Level)", "int", icon="📈",
              filter="min", presets=(30, 50, 60, 70, 80, 90)),
        Field("rank", "Eng yuqori rank", "Высший ранг", "choice", PUBG_RANKS, icon="🏆", filter="choice"),
        Field("xsuits", "X-Suit soni", "Кол-во X-Suit", "int", icon="🥷", filter="min", presets=(1, 2, 3, 5)),
        Field("mythics", "Mifik skinlar soni", "Кол-во мификов", "int", icon="💎", filter="min",
              presets=(1, 5, 10, 30, 50)),
        Field("upgr_guns", "Yaxshilangan qurollar (masalan: M416 Glacier, AKM Glacier)",
              "Улучшаемое оружие (например: M416 Glacier, AKM Glacier)", "text", icon="🔫", filter="text"),
        Field("uc", "UC qoldig'i", "Остаток UC", "int", required=False, icon="🪙", filter="min",
              presets=(60, 300, 600, 1500, 3000)),
    ),
)

# Keyingi bosqich o'yini (enabled=False — Dashboard'da «🔜 tez kunda», admin yoqadi)
STANDOFF2 = Game(
    code="so2",
    name="Standoff 2",
    emoji="🎯",
    enabled=False,
    fields=(
        Field("level", "Daraja", "Уровень", "int", icon="📈", filter="min", presets=(20, 40, 60)),
        Field("rank", "Rank", "Ранг", "text", icon="🏆", filter="text"),
        Field("inventory", "Inventar qiymati (gold)", "Стоимость инвентаря (gold)", "int", icon="💰",
              filter="min", presets=(1000, 5000, 20000)),
        Field("knives", "Pichoqlar / qimmat skinlar", "Ножи / дорогие скины", "text", icon="🔪", filter="text"),
    ),
)

# ---------- Coin / UC xizmatlari (1-bosqich: sotuvchilar e'lonlari, biz pulga tegmaymiz) ----------
TOPUP_METHOD = Field("method", "To'ldirish usuli", "Способ пополнения", "choice",
                     ("ID orqali (parolsiz) / По ID", "Gift card / kod", "Login orqali ⚠️ / Через логин ⚠️"),
                     icon="🔐", filter="choice")
TOPUP_SPEED = Field("speed", "Yetkazish vaqti", "Срок выполнения", "choice",
                    ("5–30 daqiqa / мин", "1–3 soat / часа", "24 soat / часа"), icon="⏱", filter="choice")
TOPUP_PACKS = Field("packs", "Paketlar va narxlar (har qatorda bittadan: 1040 coin — 137 000)",
                    "Пакеты и цены (по одному в строке: 1040 coin — 137 000)", "text", icon="📦")
TOPUP_PROOF = Field("proof", "Isbot/otzivlar kanali (@kanal)", "Канал с отзывами (@канал)", "text",
                    required=False, icon="✅")

EFB_COIN = Game(
    code="efb_coin", name="eFootball Coin", emoji="🪙", kind="topup",
    fields=(
        Field("platform", "Platforma", "Платформа", "choice", ("Android", "iOS", "Android + iOS", "PC / Steam"), icon="📱"),
        TOPUP_METHOD, TOPUP_SPEED, TOPUP_PACKS, TOPUP_PROOF,
    ),
)

PUBG_UC = Game(
    code="pubg_uc", name="PUBG Mobile UC", emoji="💎", kind="topup",
    fields=(TOPUP_METHOD, TOPUP_SPEED, TOPUP_PACKS, TOPUP_PROOF),
)

GAMES: dict[str, Game] = {g.code: g for g in (EFOOTBALL, PUBGM, STANDOFF2, EFB_COIN, PUBG_UC)}


def active_games(kind: str | None = None) -> list[Game]:
    return [g for g in GAMES.values() if g.enabled and (kind is None or g.kind == kind)]


def soon_games(kind: str | None = None) -> list[Game]:
    """Tayyor shabloni bor, lekin hali yoqilmagan o'yinlar — dashboardda «🔜 Tez kunda»."""
    return [g for g in GAMES.values() if not g.enabled and (kind is None or g.kind == kind)]


# Tugmalar uchun qisqa nomlar (uz, ru)
SHORT_LABELS: dict[str, tuple[str, str]] = {
    "platform": ("Platforma", "Платформа"), "binding": ("Bog'lanish", "Привязка"),
    "team_strength": ("Ko'rsatkich (TS)", "Показатель (TS)"), "epic_count": ("Epic", "Epic"),
    "bigtime_count": ("Big Time", "Big Time"), "top_players": ("O'yinchi", "Игрок"),
    "packs": ("Pack", "Пак"), "coins": ("Coin", "Coin"), "gp": ("GP", "GP"),
    "division": ("Division", "Дивизион"), "donated": ("Donat", "Донат"),
    "level": ("Daraja", "Уровень"), "rank": ("Rank", "Ранг"), "mythics": ("Mifik", "Мифики"),
    "upgr_guns": ("Qurollar", "Оружие"), "xsuits": ("X-Suit", "X-Suit"), "uc": ("UC", "UC"), "inventory": ("Inventar", "Инвентарь"),
    "knives": ("Pichoq/skin", "Ножи/скины"), "method": ("Usul", "Способ"), "speed": ("Muddat", "Срок"),
}

TEXT_EXAMPLES: dict[str, str] = {
    "top_players": "Messi", "packs": "POTW", "rank": "Conqueror", "upgr_guns": "M416 Glacier", "knives": "Karambit",
}


def short_label(f: Field, lang: str) -> str:
    pair = SHORT_LABELS.get(f.key)
    if pair:
        return pair[1] if lang == "ru" else pair[0]
    return f.label(lang).split(" (")[0].split(" — ")[0]
