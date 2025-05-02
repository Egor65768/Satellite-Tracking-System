from pydantic import BaseModel, Field
from typing import Optional


class RegionBase(BaseModel):
    """Базовая схема региона (общие поля для всех схем)."""

    name_region: str = Field(
        ..., min_length=1, max_length=60, json_schema_extra={"example": "Asia"}
    )


class RegionCreate(RegionBase):
    """Схема для создания региона. Наследует все поля RegionBase."""

    id: Optional[int] = Field(
        None, description="ID региона. Оставьте None для автоинкремента."
    )


class RegionInDB(RegionBase):
    """Схема региона, возвращаемая из БД (с ID)."""

    id: int


class RegionUpdate(RegionBase):
    """Схема для обновления региона (все поля опциональны)."""

    pass


class SubregionBase(BaseModel):
    """Базовая схема субрегиона (общие поля для всех схем)."""

    name_subregion: str = Field(
        ..., min_length=1, max_length=60, json_schema_extra={"example": "Moscow region"}
    )


class SubregionInDB(RegionBase):
    """Схема субрегиона, возвращаемая из БД (с ID)."""

    id: int
    id_region: int
    name_region: Optional[str] = Field(
        None, min_length=1, max_length=60, json_schema_extra={"example": "Asia"}
    )
