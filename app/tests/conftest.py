import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core import settings
from app.db import Base


@pytest_asyncio.fixture(scope="session")
async def engine():
    async_engine = create_async_engine(
        settings.get_test_db_url(),
    )
    yield async_engine
    await async_engine.dispose()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture()
async def db_session(engine):
    async_session_maker = async_sessionmaker(
        engine, expire_on_commit=False, autocommit=False
    )
    async with async_session_maker() as session:
        # async with session.begin():
        yield session
        await session.rollback()
