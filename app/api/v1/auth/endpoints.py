from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from .dependencies import get_auth_request, oauth2_scheme_refresh
from app.core import (
    RefreshTokenExpiredError,
    InvalidRefreshToken,
    RefreshTokenNotFoundError,
)
from app.schemas import Token
from app.core import InvalidPasswordError, EmailNotFoundError
from app.service import UserService, TokenService
from app.api.v1.helpers import get_token_service, get_user_service

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
    user_service: UserService = Depends(get_user_service),
    token_service: TokenService = Depends(get_token_service),
):
    try:
        user_id, role = await user_service.authenticate_user(
            get_auth_request(form_data)
        )
    except InvalidPasswordError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )
    except EmailNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not found",
        )
    tokens = await token_service.create_tokens(user_id=user_id, data_dict={}, role=role)
    await token_service.repository.session.commit()
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
    token_service: TokenService = Depends(get_token_service),
):
    try:
        user_id, role = await token_service.decode_and_verify_refresh_token(
            refresh_token
        )
        if not await token_service.delete_refresh_token(refresh_token):
            raise InvalidRefreshToken()
        tokens = await token_service.create_tokens(
            user_id=user_id, data_dict={}, role=role
        )
        await token_service.repository.session.commit()
        return tokens

    except RefreshTokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token refresh expired",
        )
    except InvalidRefreshToken:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )
    except RefreshTokenNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found in db",
        )
