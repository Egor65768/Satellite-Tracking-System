from __future__ import annotations
import jwt
from typing import TYPE_CHECKING, Optional, Dict, List
from datetime import timedelta, datetime, timezone
from app.schemas import (
    RefreshToken,
    AccessToken,
    Object_ID,
    Token,
    CreateRefreshToken,
    RefreshTokenInDB,
)
from app.service import get_hash, verify_password
from app.core import (
    settings,
    InvalidRefreshToken,
    InvalidAccessToken,
    RefreshTokenNotFoundError,
    UserNotFoundError,
    RefreshTokenExpiredError,
    AccessTokenExpiredError,
)
from uuid import uuid4

if TYPE_CHECKING:
    from app.db import TokenRepository, UserRepository


class TokenService:
    def __init__(self, repository: TokenRepository, user_repository: UserRepository):
        self.repository = repository
        self.user_repository = user_repository

    @staticmethod
    async def _create_token(
        user_id: Object_ID, expire: datetime, secret_key: str, jti: str
    ) -> str:
        payload = {"sub": str(user_id.id), "exp": int(expire.timestamp()), "jti": jti}
        encoded_jwt = jwt.encode(payload, secret_key, algorithm=settings.ALGORITHM)
        return encoded_jwt

    async def create_access_token(self, user_id: Object_ID) -> AccessToken:
        return AccessToken(
            access_token=await self._create_token(
                user_id=user_id,
                expire=datetime.now(timezone.utc)
                + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS),
                secret_key=settings.ACCESS_TOKEN_SECRET_KEY,
                jti=str(uuid4()),
            )
        )

    async def create_refresh_token(
        self, data_dict: Dict, user_id: Object_ID
    ) -> Optional[RefreshToken]:
        jti = str(uuid4())
        expire = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS,
            seconds=settings.REFRESH_TOKEN_EXPIRE_SECONDS,
        )
        refresh_token = await self._create_token(
            user_id=user_id,
            expire=expire,
            secret_key=settings.REFRESH_TOKEN_SECRET_KEY,
            jti=jti,
        )
        if not await self.repository.create_entity(
            CreateRefreshToken(
                user_id=user_id.id,
                device_info=data_dict.get("device_info"),
                ip_address=data_dict.get("ip_address"),
                token_hash=get_hash(refresh_token),
                expires_at=expire,
                jti=jti,
            )
        ):
            return None
        await self.repository.session.flush()
        return RefreshToken(refresh_token=refresh_token)

    async def create_tokens(self, data_dict: Dict, user_id: Object_ID) -> Token:
        if await self.user_repository.get_as_model(user_id) is None:
            raise UserNotFoundError()
        return Token(
            access_token=(await self.create_access_token(user_id)).access_token,
            refresh_token=(
                await self.create_refresh_token(data_dict, user_id)
            ).refresh_token,
            token_type="Bearer",
        )

    @staticmethod
    async def _decode_token(token: str, secret_key: str) -> Dict:
        return jwt.decode(token, secret_key, algorithms=[settings.ALGORITHM])

    async def decode_access_token(self, token: str) -> Object_ID:
        try:
            return Object_ID(
                id=int(
                    (
                        await self._decode_token(
                            token=token, secret_key=settings.ACCESS_TOKEN_SECRET_KEY
                        )
                    ).get("sub")
                )
            )
        except jwt.ExpiredSignatureError:
            raise AccessTokenExpiredError()
        except jwt.PyJWTError as e:
            print(e)
            raise InvalidAccessToken()

    async def _decode_refresh_token(self, token: str) -> Object_ID:
        try:
            return Object_ID(
                id=(
                    await self._decode_token(
                        token=token, secret_key=settings.REFRESH_TOKEN_SECRET_KEY
                    )
                ).get("sub")
            )
        except jwt.ExpiredSignatureError:
            raise RefreshTokenExpiredError()
        except jwt.PyJWTError:
            raise InvalidRefreshToken()

    @staticmethod
    async def _get_token(
        refresh_tokens: List[RefreshTokenInDB], token: str
    ) -> Optional[RefreshTokenInDB]:
        for refresh_token in refresh_tokens:
            if verify_password(token, refresh_token.token_hash):
                payload = jwt.decode(
                    token,
                    settings.REFRESH_TOKEN_SECRET_KEY,
                    algorithms=[settings.ALGORITHM],
                )
                if payload.get("jti") == refresh_token.jti:
                    return refresh_token
        return None

    async def get_refresh_tokens_by_user_id(
        self, user_id: Object_ID
    ) -> List[RefreshTokenInDB]:
        return await self.repository.get_refresh_tokens_by_user_id(user_id)

    async def decode_and_verify_refresh_token(self, token: str) -> Object_ID:
        object_id = await self._decode_refresh_token(token)
        refresh_tokens = await self.get_refresh_tokens_by_user_id(object_id)
        if await self._get_token(refresh_tokens, token) is None:
            raise RefreshTokenNotFoundError()
        return object_id

    async def delete_refresh_token(self, token: str) -> bool:
        try:
            object_id = await self._decode_refresh_token(token)
        except InvalidRefreshToken:
            return False
        refresh_token_db = await self._get_token(
            await self.repository.get_refresh_tokens_by_user_id(object_id), token
        )
        if refresh_token_db is None:
            return False
        res = await self.repository.delete_refresh_token(
            Object_ID(id=refresh_token_db.id)
        )
        if res:
            await self.repository.session.flush()
        return res

    async def delete_refresh_token_by_id(self, token_id: Object_ID) -> bool:
        return await self.repository.delete_model(token_id)
