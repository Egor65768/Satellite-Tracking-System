import pytest

from app.service import verify_password
from app.service import create_user_service
from app.schemas import (
    UserCreate,
    UserRole,
    PaginationBase,
    AdminPassword,
    AuthRequest,
    UserUpdate,
    UserPassword,
)
from app.core import (
    settings,
    AdminPasswordRequiredError,
    InvalidPasswordError,
    EmailNotFoundError,
    NewPasswordMatchesOldError,
)
from tests.test_data import user_data, user_data_admin, invalid_email


class TestUserService:
    @pytest.mark.asyncio
    async def test_create_1(self, db_session):
        service = create_user_service(db_session)
        user_create = UserCreate(**user_data)
        assert await service.create_user(user_create=user_create, admin_password=None)
        user_in_db = await service.get_user_by_email(user_data.get("email"))
        assert user_in_db.name == "Egor"
        assert user_in_db.role == UserRole.USER
        assert verify_password("Egor21212e", user_in_db.hashed_password)
        assert user_in_db.email == user_data.get("email")

        user_list = await service.get_users(PaginationBase())
        assert len(user_list) == 1

    @pytest.mark.asyncio
    async def test_create_2_invalid(self, db_session):
        service = create_user_service(db_session)
        user_create = UserCreate(**user_data)
        assert not await service.create_user(
            user_create=user_create, admin_password=None
        )
        user_in_db = await service.get_user_by_email(user_data.get("email"))
        assert user_in_db.name == "Egor"
        assert user_in_db.role == UserRole.USER
        assert verify_password("Egor21212e", user_in_db.hashed_password)
        assert user_in_db.email == user_data.get("email")

        user_list = await service.get_users(PaginationBase())
        assert len(user_list) == 1

    @pytest.mark.asyncio
    async def test_create_3_admin(self, db_session):
        service = create_user_service(db_session)
        user_create = UserCreate(**user_data_admin)
        with pytest.raises(AdminPasswordRequiredError):
            await service.create_user(user_create=user_create, admin_password=None)
        assert len(await service.get_users(PaginationBase())) == 1
        with pytest.raises(AdminPasswordRequiredError):
            await service.create_user(
                user_create=user_create,
                admin_password=AdminPassword(password="Invalid_password"),
            )
        assert len(await service.get_users(PaginationBase())) == 1

        assert await service.create_user(
            user_create=user_create,
            admin_password=AdminPassword(password=settings.ADMIN_SECRET_KEY),
        )
        assert len(await service.get_users(PaginationBase())) == 2

        user_in_db = await service.get_user_by_email(user_data_admin.get("email"))
        assert user_in_db.name == user_data_admin.get("name")
        assert user_in_db.role == user_data_admin.get("role")
        assert verify_password(
            user_data_admin.get("password"), user_in_db.hashed_password
        )
        assert user_in_db.email == user_data_admin.get("email")

    @pytest.mark.asyncio
    async def test_authenticate_user(self, db_session):
        service = create_user_service(db_session)
        with pytest.raises(InvalidPasswordError):
            await service.authenticate_user(
                AuthRequest(
                    password="Invalid_password_123", email=user_data.get("email")
                )
            )
        with pytest.raises(EmailNotFoundError):
            await service.authenticate_user(
                AuthRequest(
                    password="Invalid_password_1487", email=invalid_email.get("email")
                )
            )

        with pytest.raises(EmailNotFoundError):
            await service.authenticate_user(
                AuthRequest(
                    password=user_data.get("password"), email=invalid_email.get("email")
                )
            )
        assert await service.authenticate_user(
            AuthRequest(
                password=user_data.get("password"), email=user_data.get("email")
            )
        )

    async def test_update_user_1(self, db_session):
        service = create_user_service(db_session)
        update_data_1 = {"name": "Alina"}
        auth_request = AuthRequest(
            password=user_data.get("password"), email=user_data.get("email")
        )
        assert await service.update_user_data(UserUpdate(**update_data_1), auth_request)
        user = await service.get_user_by_email(user_data.get("email"))
        assert user is not None
        assert user.name == "Alina"
        assert verify_password(user_data.get("password"), user.hashed_password)
        assert user.email == user_data.get("email")
        assert user.role == UserRole.USER

    async def test_update_user_2_invalid(self, db_session):
        service = create_user_service(db_session)
        update_data_1 = {"name": "Dima"}
        auth_request = AuthRequest(
            password=user_data.get("password"), email=invalid_email.get("email")
        )
        with pytest.raises(EmailNotFoundError):
            assert await service.update_user_data(
                UserUpdate(**update_data_1), auth_request
            )
        user = await service.get_user_by_email(user_data.get("email"))
        assert user is not None
        assert user.name == "Alina"

        auth_request = AuthRequest(
            password="Invalid_password_123", email=user_data.get("email")
        )
        with pytest.raises(InvalidPasswordError):
            assert await service.update_user_data(
                UserUpdate(**update_data_1), auth_request
            )
        user = await service.get_user_by_email(user_data.get("email"))
        assert user is not None
        assert user.name == "Alina"

    async def test_update_user_3_invalid(self, db_session):
        service = create_user_service(db_session)
        update_data_1 = {"email": user_data_admin.get("email")}
        auth_request = AuthRequest(
            password=user_data.get("password"), email=user_data.get("email")
        )
        assert not await service.update_user_data(
            UserUpdate(**update_data_1), auth_request
        )
        user = await service.get_user_by_email(user_data.get("email"))
        assert user is not None
        assert user.name == "Alina"

        update_data_1 = {"name": "Misha", "email": user_data_admin.get("email")}
        assert not await service.update_user_data(
            UserUpdate(**update_data_1), auth_request
        )
        assert user is not None
        assert user.name == "Alina"

    async def test_update_user_4_update_password(self, db_session):
        service = create_user_service(db_session)
        update_data_1 = {"password": user_data.get("password")}
        auth_request = AuthRequest(
            password=user_data.get("password"), email=user_data.get("email")
        )
        with pytest.raises(NewPasswordMatchesOldError):
            await service.update_password(UserPassword(**update_data_1), auth_request)
        update_data_1 = {"password": "fhfG384hdhHDwh"}
        auth_request = AuthRequest(
            password=user_data.get("password"), email=invalid_email.get("email")
        )
        with pytest.raises(EmailNotFoundError):
            await service.update_password(UserPassword(**update_data_1), auth_request)
        auth_request = AuthRequest(
            password="uduheiwoihhvhhHjkj2", email=user_data.get("email")
        )
        with pytest.raises(InvalidPasswordError):
            await service.update_password(UserPassword(**update_data_1), auth_request)
        auth_request = AuthRequest(
            password=user_data.get("password"), email=user_data.get("email")
        )
        assert await service.update_password(
            UserPassword(**update_data_1), auth_request
        )
        user = await service.get_user_by_email(user_data.get("email"))
        assert user is not None
        assert user.name == "Alina"
        assert verify_password(update_data_1.get("password"), user.hashed_password)

        auth_request = AuthRequest(
            password=update_data_1.get("password"), email=user_data.get("email")
        )
        update_data_1 = {"password": user_data.get("password")}
        assert await service.update_password(
            UserPassword(**update_data_1), auth_request
        )
        user = await service.get_user_by_email(user_data.get("email"))
        assert user is not None
        assert user.name == "Alina"
        assert verify_password(user_data.get("password"), user.hashed_password)

    async def test_update_user_5(self, db_session):
        service = create_user_service(db_session)
        update_data_1 = {"name": "Dima", "email": "dimasik12092@mail.ru"}
        auth_request = AuthRequest(
            password=user_data.get("password"), email=user_data.get("email")
        )
        await service.update_user_data(UserUpdate(**update_data_1), auth_request)
        user = await service.get_user_by_email(update_data_1.get("email"))  # type: ignore
        assert user is not None
        assert user.name == "Dima"
        assert user.role == UserRole.USER
        assert user.email == "dimasik12092@mail.ru"
