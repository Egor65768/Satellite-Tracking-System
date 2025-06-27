from __future__ import annotations
from typing import TYPE_CHECKING, Optional, List
from app.schemas import (
    Object_ID,
    UserInDB,
    UserCreate,
    AdminPassword,
    UserRole,
    AuthRequest,
    UserEmail,
    UserUpdate,
    UserCreateInDB,
    PaginationBase,
    UserPassword,
    UserPasswordHash,
)
from pydantic import ValidationError, EmailStr
from app.core import (
    AdminPasswordRequiredError,
    InvalidPasswordError,
    EmailNotFoundError,
    NewPasswordMatchesOldError,
    AccessDeniedError,
)
from app.service import get_hash, verify_password

if TYPE_CHECKING:
    from app.db import UserRepository


class UserService:
    def __init__(
        self,
        repository: UserRepository,
    ):
        self.repository = repository

    @staticmethod
    async def _get_validated_id(satellite_id: int) -> Optional[Object_ID]:
        try:
            return Object_ID(id=satellite_id)
        except ValidationError:
            return None

    async def get_user_by_id(self, user_id: int) -> Optional[UserInDB]:
        object_id = await self._get_validated_id(user_id)
        return (
            await self.repository.get_as_model(object_id)
            if object_id is not None
            else None
        )

    async def get_user_by_email(self, email: EmailStr) -> Optional[UserInDB]:
        return await self.repository.get_by_field("email", email)

    async def create_user(
        self, user_create: UserCreate, admin_password: Optional[AdminPassword]
    ) -> Optional[UserInDB]:
        if user_create.role == UserRole.ADMIN:
            from app.core import settings

            if (
                admin_password is None
                or settings.ADMIN_SECRET_KEY != admin_password.password
            ):
                raise AdminPasswordRequiredError()
        user_create_db = UserCreateInDB(
            name=user_create.name,
            email=user_create.email,
            hashed_password=get_hash(user_create.password),
            role=user_create.role,
        )
        user = await self.repository.create_entity(user_create_db)
        if user:
            await self.repository.session.commit()
        return user

    async def authenticate_user(self, auth_request: AuthRequest) -> Object_ID:
        password_hash_db = await self.repository.get_hash_password_by_email(
            UserEmail(email=auth_request.email)
        )
        if password_hash_db is None:
            raise EmailNotFoundError(email=str(auth_request.email))
        if not verify_password(auth_request.password, password_hash_db):
            raise InvalidPasswordError()
        user = await self.get_user_by_email(auth_request.email)
        return Object_ID(id=user.id)

    async def delete_user(self, email_user: EmailStr) -> bool:
        try:
            email = UserEmail(email=email_user)
            res = await self.repository.delete_model_by_email(email)
            if res:
                await self.repository.session.commit()
            return res
        except ValidationError:
            return False

    async def _get_user_id_by_email(self, email: EmailStr) -> Optional[Object_ID]:
        try:
            user_id = Object_ID(
                id=await self.repository.get_id_by_email(UserEmail(email=email))
            )
            return user_id
        except ValidationError:
            return None

    async def update_user_data(
        self, user_update: UserUpdate, auth_request: AuthRequest
    ) -> Optional[UserInDB]:
        await self.authenticate_user(auth_request)
        user_id = await self._get_user_id_by_email(auth_request.email)
        if user_id is None:
            return None
        if user_update.role == UserRole.ADMIN:
            raise AccessDeniedError()
        res = await self.repository.update_model(
            object_id=user_id, object_update=user_update
        )
        if res:
            await self.repository.session.commit()
        return res

    async def update_password(
        self, new_password: UserPassword, auth_request: AuthRequest
    ) -> bool:
        if new_password.password == auth_request.password:
            raise NewPasswordMatchesOldError()
        await self.authenticate_user(auth_request)
        user_id = await self._get_user_id_by_email(auth_request.email)
        if user_id is None:
            return False
        user_password_hash = UserPasswordHash(
            hashed_password=get_hash(new_password.password)
        )
        res = await self.repository.update_model(
            object_id=user_id, object_update=user_password_hash
        )
        if res:
            await self.repository.session.commit()

        return res is not None

    async def get_users(self, pagination: PaginationBase) -> List[UserInDB]:
        return await self.repository.get_models(pagination)
