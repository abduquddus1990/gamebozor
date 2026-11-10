"""⭐️ Sotuvchi obro'si: tasdiq belgisi + o'rtacha baho va sharhlar soni."""
from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Review, User


@dataclass(frozen=True)
class SellerInfo:
    verified: bool = False
    avg: float = 0.0
    count: int = 0

    @property
    def rating(self) -> tuple[float, int] | None:
        return (self.avg, self.count) if self.count else None


async def seller_info(session: AsyncSession, seller_id: int) -> SellerInfo:
    user = await session.get(User, seller_id)
    avg, cnt = (await session.execute(
        select(func.avg(Review.rating), func.count(Review.id)).where(Review.seller_id == seller_id))).one()
    return SellerInfo(bool(user and user.is_verified), round(float(avg or 0), 1), int(cnt or 0))


def stars(avg: float) -> str:
    full = int(round(avg))
    return "★" * full + "☆" * (5 - full)
