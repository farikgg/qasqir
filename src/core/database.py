from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from src.app.config import get_settings

settings = get_settings()
async_engine: AsyncEngine = create_async_engine(
    url=settings.database_settings.database_url,
    echo=False
)
async_session_maker: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False
)


class Base(AsyncAttrs, DeclarativeBase):
    pass

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
