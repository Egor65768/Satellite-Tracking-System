from .repository import BaseRepository
from app.db import RefreshToken
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import RefreshTokenInDB, Object_ID
from typing import List
from sqlalchemy import select, delete
from datetime import datetime, timezone


class TokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)
        self.in_db_type = RefreshTokenInDB

    async def get_refresh_tokens_by_user_id(
        self, user_id: Object_ID
    ) -> List[RefreshTokenInDB]:
        query = select(RefreshToken).where(RefreshToken.user_id == user_id.id)
        result = await self.session.execute(query)
        tokens_list = list()
        tokens = result.scalars()
        flag_delete = False
        for token in tokens:
            if token.expires_at < datetime.now(timezone.utc):
                await self.delete_refresh_token(Object_ID(id=token.id))
                flag_delete = True
                continue
            tokens_list.append(RefreshTokenInDB(**token.__dict__))
        if flag_delete:
            await self.session.flush()
        return tokens_list

    async def delete_refresh_token(self, refresh_token_id: Object_ID) -> bool:
        return await self.delete_model(refresh_token_id)

    async def delete_refresh_token_by_user_id(self, user_id: Object_ID) -> bool:
        query = delete(RefreshToken).where(RefreshToken.user_id == user_id.id)
        result = await self.session.execute(query)
        number_lines_removed: int = result.rowcount  # type: ignore[attr-defined]
        return number_lines_removed > 0
