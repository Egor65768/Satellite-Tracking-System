from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core import (
    get_db,
    RefreshTokenExpiredError,
    InvalidRefreshToken,
    RefreshTokenNotFoundError,
)
from app.service import create_token_service, create_user_service
from app.schemas import (
    Token,
)
from app.core import InvalidPasswordError, EmailNotFoundError
from .dependencies import get_auth_request, oauth2_scheme_refresh
from app.api.v1.helpers import raise_if_object_none

router = APIRouter()


@router.post(
    path="/tokens",
    response_model=Token,
    summary="Authenticate user and get tokens",
    description="Authenticates user credentials and returns JWT access and refresh tokens",
    responses={
        401: {"description": "Invalid credentials"},
        200: {"description": "Successful authentication", "model": Token},
    },
)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    user_service = create_user_service(db)
    user_id = None
    try:
        user_id = await user_service.authenticate_user(get_auth_request(form_data))
    except InvalidPasswordError:
        await raise_if_object_none(
            None, status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
        )
    except EmailNotFoundError:
        await raise_if_object_none(
            None, status_code=status.HTTP_401_UNAUTHORIZED, detail="Email not found"
        )

    token_service = create_token_service(db)
    tokens = await token_service.create_tokens(user_id=user_id, data_dict={})
    return tokens


@router.post(
    path="/refresh-token",
    response_model=Token,
    summary="Refresh JWT tokens",
    description="""Validates the refresh token and returns new pair of access and refresh tokens.
      \n\n**Security Note:** Previous refresh token will be invalidated after this operation.""",
    responses={
        401: {"description": "Invalid or expired refresh token"},
        200: {"description": "New tokens generated successfully", "model": Token},
    },
)
async def refresh_tokens(
    refresh_token: str = Depends(oauth2_scheme_refresh),
    db: AsyncSession = Depends(get_db),
):
    token_service = create_token_service(db)
    try:
        user_id = await token_service.decode_and_verify_refresh_token(refresh_token)
        token_service = create_token_service(db)
        if not await token_service.delete_refresh_token(refresh_token):
            raise InvalidRefreshToken()
        tokens = await token_service.create_tokens(user_id=user_id, data_dict={})
        return tokens

    except RefreshTokenExpiredError:
        await raise_if_object_none(
            None,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh expired",
        )
    except InvalidRefreshToken:
        await raise_if_object_none(
            None,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    except RefreshTokenNotFoundError:
        await raise_if_object_none(
            None,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in db",
        )
