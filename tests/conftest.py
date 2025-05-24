import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core import settings
from app.db import Base
from httpx import ASGITransport, AsyncClient
from app.main import app


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
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
