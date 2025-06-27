from app.schemas import AuthRequest, UserRole
from app.service import create_token_service, create_user_service
from app.core import (
    get_db,
    AccessTokenExpiredError,
    InvalidAccessToken,
)

from fastapi.security import OAuth2PasswordRequestForm
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

oauth2_scheme_access = OAuth2PasswordBearer(tokenUrl="token", scheme_name="AccessToken")

oauth2_scheme_refresh = OAuth2PasswordBearer(
    tokenUrl="refresh-token", scheme_name="RefreshToken"
)


def get_auth_request(form_data: OAuth2PasswordRequestForm) -> AuthRequest:
    return AuthRequest(
        password=form_data.password, email=form_data.username  # type: ignore
    )


async def get_current_user(
    token: str = Depends(oauth2_scheme_access), db: AsyncSession = Depends(get_db)
):
    token_service = create_token_service(db)
    try:
        user_id = await token_service.decode_access_token(token)
        user_service = create_user_service(db)
        user_in_db = await user_service.get_user_by_id(user_id.id)
        if user_in_db is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The access token contains a non-existent user ID",
            )
        if user_in_db.role != UserRole.ADMIN.value():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

    except AccessTokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )

    except InvalidAccessToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
