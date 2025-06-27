from pydantic import BaseModel, Field
from typing import Optional, List


class RegionBase(BaseModel):
    """Базовая схема региона (общие поля для всех схем)."""

    name_region: str = Field(
        ..., min_length=1, max_length=60, json_schema_extra={"example": "Asia"}
    )


class RegionCreate(RegionBase):
    """Схема для создания региона. Наследует все поля RegionBase."""

    id: Optional[int] = Field(
        None,
        description="ID региона. Оставьте None для автоинкремента.",
        json_schema_extra={"example": 14},
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


class SubregionInDB(SubregionBase):
    """Схема субрегиона, возвращаемая из БД (с ID)."""

    id: int
    id_region: int


class SubregionCreate(SubregionBase):
    """Схема для создания субрегиона. Наследует все поля SubregionBase."""

    id: Optional[int] = Field(
        None, description="ID субрегиона. Оставьте None для автоинкремента."
    )
    id_region: int


class SubregionCreateByName(SubregionBase):
    """Схема для создания субрегиона, по имени региона. Наследует все поля SubregionBase."""

    id: Optional[int] = Field(
        None, description="ID субрегиона. Оставьте None для автоинкремента."
    )
    region_name: str = Field(
        ..., min_length=1, max_length=60, json_schema_extra={"example": "Asia"}
    )


class SubregionUpdate(BaseModel):
    """Схема для обновления субрегиона (все поля опциональны)."""

    name_subregion: Optional[str] = Field(
        None,
        min_length=1,
        max_length=60,
        json_schema_extra={"example": "Moscow region"},
    )

    id_region: Optional[int] = Field(
        None, description="ID региона к которому от данный субрегион"
    )


class Subregion(SubregionBase):
    """Схема для одного субрегиона для регоина"""

    id: int


class ZoneRegionDetails(RegionInDB):
    """Схема для одного региона зоны"""

    subregion_list: List[Subregion]
