from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core import settings

DATABASE_URL = settings.get_db_url()

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
)

async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)

# Генератор для Dependency Injection в FastAPI
async def get_db() -> AsyncGenerator[AsyncSession, Any]:
    async with async_session_maker() as session:
        yield session