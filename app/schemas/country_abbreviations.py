from pydantic import BaseModel, Field
from typing import Optional


class CountryBase(BaseModel):
    """Базовая схема страны (общие поля для всех схем)."""

    abbreviation: str = Field(
        ..., min_length=1, max_length=10, json_schema_extra={"example": "CA"}
    )
    full_name: str = Field(
        ..., min_length=2, max_length=100, json_schema_extra={"example": "Канада"}
    )


class CountryCreate(CountryBase):
    """Схема для создания страны. Наследует все поля CountryBase."""

    id: Optional[int] = Field(
        None, gt=0, description="ID страны. Оставьте None для автоинкремента."
    )


class CountryUpdate(BaseModel):
    """Схема для обновления страны (все поля опциональны)."""

    abbreviation: Optional[str] = Field(
        None, min_length=1, max_length=10, json_schema_extra={"example": "US"}
    )
    full_name: Optional[str] = Field(
        None, min_length=2, max_length=100, json_schema_extra={"example": "США"}
    )


class CountryInDB(CountryBase):
    """Схема страны, возвращаемая из БД (с ID)."""

    id: int


class CountryFind(BaseModel):
    abbreviation: str = Field(
        ..., min_length=1, max_length=10, json_schema_extra={"example": "CA"}
    )
