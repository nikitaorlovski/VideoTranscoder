from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


engine = create_async_engine(
    url=settings.db.url,
    future=True,
    pool_size=10,
)

new_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
