import pytest
from app.service import verify_password
from app.service import create_token_service, create_user_service
from app.schemas import (
    UserCreate,
    UserRole,
    PaginationBase,
    Object_ID,
)
from asyncio import sleep
from app.core import (
    RefreshTokenNotFoundError,
    AccessTokenExpiredError,
    RefreshTokenExpiredError,
    InvalidAccessToken,
    InvalidRefreshToken,
    settings,
)
from tests.test_data import user_data


class TestTokenService:
    @pytest.mark.asyncio
    async def test_create_user(self, db_session):
        async with db_session.begin():
            service = create_user_service(db_session)
            user_create = UserCreate(**user_data)
            assert await service.create_user(
                user_create=user_create, admin_password=None
            )
        async with db_session.begin():
            user_in_db = await service.get_user_by_email(user_data.get("email"))
            assert user_in_db.name == "Egor"
            assert user_in_db.role == UserRole.USER
            assert verify_password("Egor21212e", user_in_db.hashed_password)
            assert user_in_db.email == user_data.get("email")

            user_list = await service.get_users(PaginationBase())
            assert len(user_list) == 1

    @pytest.mark.asyncio
    async def test_create_1(self, db_session):
        async with db_session.begin():
            service = create_token_service(db_session)
            user_service = create_user_service(db_session)
            user_in_db = await user_service.get_user_by_email(user_data.get("email"))
            tokens = await service.create_tokens(
                data_dict={}, user_id=Object_ID(id=user_in_db.id)
            )
            assert tokens is not None
            assert tokens.token_type == "Bearer"
            assert tokens.refresh_token is not None
            assert tokens.access_token is not None

            user_id = await service.decode_and_verify_refresh_token(
                tokens.refresh_token
            )
            assert user_id
            assert user_id.id == user_in_db.id

            tokens_list = await service.get_refresh_tokens_by_user_id(user_id)
            assert len(tokens_list) == 1
            assert await service.delete_refresh_token_by_id(
                Object_ID(id=tokens_list[0].id)
            )

            with pytest.raises(RefreshTokenNotFoundError):
                await service.decode_and_verify_refresh_token(tokens.refresh_token)

            with pytest.raises(InvalidRefreshToken):
                await service.decode_and_verify_refresh_token(
                    "hferhouhroerehiohvoiefjiodj"
                )

    @pytest.mark.asyncio
    async def test_create_2(self, db_session):
        async with db_session.begin():
            service = create_token_service(db_session)
            user_service = create_user_service(db_session)
            access_token_expire_seconds = settings.ACCESS_TOKEN_EXPIRE_SECONDS
            refresh_token_expire_seconds = settings.REFRESH_TOKEN_EXPIRE_SECONDS
            refresh_token_expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
            settings.ACCESS_TOKEN_EXPIRE_SECONDS = 2
            settings.REFRESH_TOKEN_EXPIRE_DAYS = 0
            settings.REFRESH_TOKEN_EXPIRE_SECONDS = 4
            assert settings.ACCESS_TOKEN_EXPIRE_SECONDS == 2
            assert settings.REFRESH_TOKEN_EXPIRE_SECONDS == 4
            assert settings.REFRESH_TOKEN_EXPIRE_DAYS == 0
            user_in_db = await user_service.get_user_by_email(user_data.get("email"))
            tokens = await service.create_tokens(
                data_dict={}, user_id=Object_ID(id=user_in_db.id)
            )
            assert tokens is not None
            assert tokens.token_type == "Bearer"
            assert tokens.refresh_token is not None
            assert tokens.access_token is not None

            user_id = await service.decode_and_verify_refresh_token(
                tokens.refresh_token
            )
            assert user_id
            assert user_id.id == user_in_db.id

            user_id_a = await service.decode_access_token(tokens.access_token)
            assert user_id == user_id_a

            user_id_b = await service.decode_and_verify_refresh_token(
                tokens.refresh_token
            )
            assert user_id_b.id == user_id.id

            await sleep(2)
            with pytest.raises(AccessTokenExpiredError):
                await service.decode_access_token(tokens.access_token)

            user_id_b = await service.decode_and_verify_refresh_token(
                tokens.refresh_token
            )
            assert user_id_b.id == user_id.id

            await sleep(2.1)
            with pytest.raises(RefreshTokenExpiredError):
                await service.decode_and_verify_refresh_token(tokens.refresh_token)

            settings.ACCESS_TOKEN_EXPIRE_SECONDS = access_token_expire_seconds
            settings.REFRESH_TOKEN_EXPIRE_SECONDS = refresh_token_expire_seconds
            settings.REFRESH_TOKEN_EXPIRE_DAYS = refresh_token_expire_days

            assert await service.create_tokens(
                data_dict={}, user_id=Object_ID(id=user_in_db.id)
            )
            tokens = await service.get_refresh_tokens_by_user_id(
                Object_ID(id=user_in_db.id)
            )
            assert len(tokens) != 0

    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        async with db_session.begin():
            service = create_token_service(db_session)
            user_service = create_user_service(db_session)
            user_in_db = await user_service.get_user_by_email(user_data.get("email"))
            tokens = await service.get_refresh_tokens_by_user_id(
                Object_ID(id=user_in_db.id)
            )
            assert len(tokens) != 0
            for token in tokens:
                assert await service.delete_refresh_token_by_id(Object_ID(id=token.id))
            tokens = await service.get_refresh_tokens_by_user_id(
                Object_ID(id=user_in_db.id)
            )
            assert len(tokens) == 0
            refresh_token_list = list()
            for _ in range(3):
                tokens = await service.create_tokens(
                    data_dict={}, user_id=Object_ID(id=user_in_db.id)
                )
                assert tokens
                refresh_token_list.append(tokens.refresh_token)
            tokens = await service.get_refresh_tokens_by_user_id(
                Object_ID(id=user_in_db.id)
            )
            assert len(tokens) == 3
            for token in refresh_token_list:
                assert await service.delete_refresh_token(token)
            tokens = await service.get_refresh_tokens_by_user_id(
                Object_ID(id=user_in_db.id)
            )
            assert len(tokens) == 0
            with pytest.raises(RefreshTokenNotFoundError):
                assert await service.decode_and_verify_refresh_token(
                    refresh_token_list[0]
                )
            assert await user_service.delete_user(user_data.get("email"))
        async with db_session.begin():
            assert await user_service.get_user_by_email(user_data.get("email")) is None
