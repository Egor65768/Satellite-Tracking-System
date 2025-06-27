from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: int
    device_info: Optional[str] = Field(
        None,
        max_length=512,
        description="Информация об устройстве, с которого выполнен вход.",
    )
    ip_address: Optional[str] = Field(
        None,
        max_length=256,
        description="IP-адрес устройства, с которого получен токен.",
    )
    expires_at: datetime = Field(
        ...,
        description="Дата истечения срока действия (в UTC). Пример: 2024-12-31T23:59:59Z",
    )


class CreateRefreshToken(TokenData):
    token_hash: str = Field(
        ...,
        description="Хэш рефреш токена.",
    )


class RefreshToken(BaseModel):
    refresh_token: str = Field(
        ...,
        description="Рефреш токен.",
    )


class AccessToken(BaseModel):
    access_token: str = Field(
        ...,
        description="Аксес токен.",
    )


class RefreshTokenInDB(CreateRefreshToken):
    id: int
    created_at: datetime = Field(
        ..., description="Дата создания токена в UTC. Пример: 2024-06-18T12:00:00Z"
    )
