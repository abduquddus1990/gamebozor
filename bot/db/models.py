"""Ma'lumotlar bazasi modellari (SQLAlchemy 2, async).

SQLite (test) va PostgreSQL (prod) ikkalasida ishlaydi — faqat DATABASE_URL o'zgaradi.
"""
from datetime import datetime

from sqlalchemy import JSON, BigInteger, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)  # Telegram user id
    username: Mapped[str | None] = mapped_column(String(64))
    full_name: Mapped[str] = mapped_column(String(128), default="")
    lang: Mapped[str | None] = mapped_column(String(2))  # 'uz' / 'ru'
    source: Mapped[str | None] = mapped_column(String(64))  # reklama manbai: /start ads_xxx
    referred_by: Mapped[int | None] = mapped_column(BigInteger)
    is_banned: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)  # ✅ tasdiqlangan sotuvchi
    rules_accepted_at: Mapped[datetime | None] = mapped_column(DateTime)  # qoidalarga rozilik
    search: Mapped[dict | None] = mapped_column(JSON)  # joriy qidiruv filtrlari (restartdan keyin ham saqlanadi)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    listings: Mapped[list["Listing"]] = relationship(back_populates="seller")


class Listing(Base):
    __tablename__ = "listings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    seller_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    game: Mapped[str] = mapped_column(String(32), index=True)  # 'efootball', 'pubgm' ...
    title: Mapped[str] = mapped_column(String(120))
    price: Mapped[int] = mapped_column(BigInteger, index=True)  # so'mda
    negotiable: Mapped[bool] = mapped_column(default=False)
    data: Mapped[dict] = mapped_column(JSON, default=dict)  # o'yinga xos maydonlar
    description: Mapped[str] = mapped_column(Text, default="")
    contact: Mapped[str] = mapped_column(String(64), default="")
    photos: Mapped[list] = mapped_column(JSON, default=list)  # Telegram file_id lar
    status: Mapped[str] = mapped_column(String(16), default="pending", index=True)
    # pending | active | rejected | sold | deleted
    reject_reason: Mapped[str | None] = mapped_column(String(255))
    channel_msg_id: Mapped[int | None] = mapped_column(Integer)
    top_until: Mapped[datetime | None] = mapped_column(DateTime, index=True)
    views: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), index=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime)

    seller: Mapped[User] = relationship(back_populates="listings")


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (UniqueConstraint("user_id", "listing_id"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    listing_id: Mapped[int] = mapped_column(ForeignKey("listings.id", ondelete="CASCADE"))


class Report(Base):
    """Shikoyatlar (firibgarlik, yolg'on e'lon)."""
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    reporter_id: Mapped[int] = mapped_column(BigInteger)
    listing_id: Mapped[int | None] = mapped_column(Integer)
    target: Mapped[str] = mapped_column(String(64))  # @username yoki user id
    reason: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Blacklist(Base):
    """Admin tasdiqlagan firibgarlar ro'yxati."""
    __tablename__ = "blacklist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target: Mapped[str] = mapped_column(String(64), unique=True)  # username (kichik harfda, @siz) yoki id
    note: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class Payment(Base):
    """Telegram Stars to'lovlari (refund uchun charge_id saqlanadi)."""
    __tablename__ = "payments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    listing_id: Mapped[int] = mapped_column(Integer)
    product: Mapped[str] = mapped_column(String(32))  # top3 / top7
    amount: Mapped[int] = mapped_column(Integer)  # Stars
    charge_id: Mapped[str] = mapped_column(String(128), unique=True)
    refunded: Mapped[bool] = mapped_column(default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class SavedSearch(Base):
    """🔔 Saqlangan qidiruv: mos yangi e'lon chiqsa foydalanuvchiga xabar boradi."""
    __tablename__ = "saved_searches"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, index=True)
    filters: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
