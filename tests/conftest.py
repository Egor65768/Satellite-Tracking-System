import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.core import settings
from app.db import Base
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.schemas import AdminPassword
from tests.test_data import admin_data, token_data, headers_auth
from fastapi import status


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


@pytest_asyncio.fixture(scope="session")
async def async_client_ses():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_and_teardown(async_client_ses):
    """Фикстура для создания админа перед тестами и очистки после"""
    admin_password = AdminPassword(password=settings.ADMIN_SECRET_KEY)
    create_response = await async_client_ses.post(
        "/user/",
        json={
            "user_create": admin_data,
            "admin_password": admin_password.model_dump(),
        },
    )
    assert create_response.status_code == status.HTTP_200_OK
    login_data = {
        "username": admin_data.get("email"),
        "password": admin_data.get("password"),
    }
    response = await async_client_ses.post(
        "/auth/tokens",
        data=login_data,
    )
    assert response.status_code == status.HTTP_200_OK
    data_t = response.json()
    token_data["access_token"] = data_t.get("access_token")
    token_data["refresh_token"] = data_t.get("refresh_token")
    token_data["token_type"] = data_t.get("token_type")
    headers_auth["Authorization"] = f"Bearer {token_data['access_token']}"
    yield
    delete_response = await async_client_ses.delete(
        "/user/", params={"user_mail": admin_data.get("email")}
    )
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
