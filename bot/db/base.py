from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from bot.config import config
from bot.db.models import Base

engine = create_async_engine(config.database_url, echo=False)
Session = async_sessionmaker(engine, expire_on_commit=False)


def _add_missing_columns(sync_conn) -> None:
    """Yengil migratsiya: modelga qo'shilgan yangi ustunlarni mavjud jadvalga qo'shadi.

    create_all() faqat yangi jadvallarni yaratadi; eski bazada (v0.2) yangi ustunlar
    bo'lmaydi — shuni shu yerda to'g'rilaymiz. Faqat nullable/defaultli ustunlar uchun.
    """
    insp = inspect(sync_conn)
    for table in Base.metadata.sorted_tables:
        if not insp.has_table(table.name):
            continue
        existing = {c["name"] for c in insp.get_columns(table.name)}
        for col in table.columns:
            if col.name in existing:
                continue
            col_type = col.type.compile(dialect=sync_conn.dialect)
            sync_conn.execute(text(f'ALTER TABLE {table.name} ADD COLUMN {col.name} {col_type}'))


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.run_sync(_add_missing_columns)
