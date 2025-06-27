from fastapi import APIRouter, Path, Depends, status, Query, HTTPException
from typing import Annotated, Optional, List
from pydantic import EmailStr
from app.core import (
    EmailNotFoundError,
    InvalidPasswordError,
    AccessDeniedError,
    AdminPasswordRequiredError,
)
from app.schemas import (
    UserInDB,
    UserCreate,
    AdminPassword,
    UserUpdate,
    AuthRequest,
    PaginationBase,
)
from app.service import UserService
from app.api.v1.helpers import raise_if_object_none, get_user_service

router = APIRouter()

UserID = Annotated[
    int,
    Path(
        title="User ID",
        ge=0,
        le=100000,
    ),
]

UserEmail = Annotated[EmailStr, Query(description="User email address")]


@router.get(
    "/{user_id}",
    response_model=UserInDB,
    summary="Get user by id",
    description="Retrieves a user information by its id",
    responses={
        404: {"description": "User not found"},
        200: {"description": "User found", "model": UserInDB},
    },
)
async def get_user_by_id(
    user_id: UserID, user_service: UserService = Depends(get_user_service)
) -> UserInDB:
    user = await user_service.get_user_by_id(user_id)
    await raise_if_object_none(user, status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.get(
    "/",
    response_model=UserInDB,
    summary="Get user by email",
    description="Retrieves a user information by its email address",
    responses={
        404: {"description": "User not found"},
        200: {"description": "User found", "model": UserInDB},
    },
)
async def get_user_by_id(
    user_mail: UserEmail, user_service: UserService = Depends(get_user_service)
) -> UserInDB:
    user = await user_service.get_user_by_email(user_mail)
    await raise_if_object_none(user, status.HTTP_404_NOT_FOUND, "User not found")
    return user


@router.get(
    "/users/",
    response_model=List[UserInDB],
    summary="Get a list users",
    responses={
        200: {"description": "Users list", "model": List[UserInDB]},
    },
)
async def get_users(
    limit: Annotated[int, Query(ge=1)] = 10,
    offset: Annotated[int, Query(ge=0)] = 0,
    user_service: UserService = Depends(get_user_service),
) -> List[UserInDB]:
    user_list = await user_service.get_users(PaginationBase(limit=limit, offset=offset))
    return user_list


@router.post(
    path="/",
    response_model=UserInDB,
    summary="Create user",
    description="Returns the user information if created successfully",
    responses={
        409: {"description": "User has not been created"},
        403: {"description": "Admin password required"},
        200: {"description": "User create", "model": UserInDB},
    },
)
async def create_user(
    user_create: UserCreate,
    admin_password: Optional[AdminPassword] = None,
    user_service: UserService = Depends(get_user_service),
) -> UserInDB:
    try:
        user = await user_service.create_user(user_create, admin_password)
    except AdminPasswordRequiredError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin password is required for this operation",
        )
    detail_fail_create = "User has not been created"
    await raise_if_object_none(user, status.HTTP_409_CONFLICT, detail_fail_create)
    return user


@router.delete(
    path="/",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user by email address",
    responses={
        404: {"description": "User not found"},
        204: {"description": "User was successfully deleted, no content returned"},
    },
)
async def delete_user_by_email(
    user_mail: UserEmail, user_service: UserService = Depends(get_user_service)
):
    res = await user_service.delete_user(user_mail)
    detail = "User not found"
    await raise_if_object_none(res, status.HTTP_404_NOT_FOUND, detail)


@router.put(
    path="/user_data",
    response_model=UserInDB,
    summary="Update user information",
    description="Updates the information of a user. "
    "Upon successful update, returns the updated user details.",
    responses={
        400: {"description": "Invalid input data"},
        404: {"description": "User not found"},
        200: {"description": "User update successfully", "model": UserInDB},
        409: {
            "description": "Conflict - User could not be updated "
            "(e.g., invalid data or constraints violation)"
        },
        403: {"description": "Access denied - insufficient permissions"},
    },
)
async def update_user(
    user_update: UserUpdate,
    auth_request: AuthRequest,
    user_service: UserService = Depends(get_user_service),
) -> UserInDB:
    try:
        user = await user_service.update_user_data(user_update, auth_request)
    except InvalidPasswordError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password",
        )
    except EmailNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    except AccessDeniedError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied - insufficient permissions",
        )

    await raise_if_object_none(
        user,
        status.HTTP_409_CONFLICT,
        "A user with such data cannot be updated",
    )
    return user
