from pydantic import BaseModel, Field, field_validator, EmailStr
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class UserBase(BaseModel):
    name: str = Field(
        ..., min_length=2, max_length=60, json_schema_extra={"example": "Slava"}
    )
    email: EmailStr = Field(
        ..., max_length=320, json_schema_extra={"example": "user@example.com"}
    )


def validate_password(password: str) -> str:
    if not any(symbol.isupper() for symbol in password):
        raise ValueError("Password must contain at least one uppercase letter")
    if not any(symbol.isdigit() for symbol in password):
        raise ValueError("Password must contain at least one digit")
    return password


class UserCreate(UserBase):
    password: str = Field(
        ..., min_length=8, max_length=64, json_schema_extra={"example": "Password_123"}
    )
    role: UserRole = Field(UserRole.USER)

    @classmethod
    @field_validator("password")
    def validate_password(cls, v):
        return validate_password(v)


class UserCreateInDB(UserBase):
    hashed_password: str
    role: UserRole = Field(UserRole.USER)


class UserInDB(UserBase):
    id: int
    hashed_password: str
    role: str
    is_active: bool


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=60)
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None


class UserEmail(BaseModel):
    email: EmailStr = Field(
        ..., max_length=320, json_schema_extra={"example": "user@example.com"}
    )


class UserPassword(BaseModel):
    password: str = Field(
        ..., min_length=8, max_length=64, json_schema_extra={"example": "Password_123"}
    )

    @classmethod
    @field_validator("password")
    def validate_password(cls, v):
        return validate_password(v)


class AuthRequest(UserEmail, UserPassword):
    pass


class AdminPassword(BaseModel):
    password: str


class UserPasswordHash(BaseModel):
    hashed_password: str
