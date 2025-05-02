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
