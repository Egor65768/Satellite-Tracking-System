from .repository import BaseRepository
from app.db import User
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import UserInDB, UserEmail
from typing import Optional
from sqlalchemy import select, delete


class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
        self.in_db_type = UserInDB

    async def get_hash_password_by_email(self, email: UserEmail) -> Optional[str]:
        query = select(User.hashed_password).where(User.email == email.email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_id_by_email(self, email: UserEmail) -> Optional[int]:
        query = select(User.id).where(User.email == email.email)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_model_by_email(self, email: UserEmail) -> bool:
        query = delete(User).where(User.email == email.email)
        result = await self.session.execute(query)
        number_lines_removed: int = result.rowcount  # type: ignore[attr-defined]
        return number_lines_removed > 0
