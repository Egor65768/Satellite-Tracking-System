from pydantic import BaseModel, Field
from typing import Optional


class CoverageZoneBase(BaseModel):
    id: str = Field(
        ..., min_length=5, max_length=60, json_schema_extra={"example": "2012-07B4-1"}
    )
    transmitter_type: str = Field(
        ..., min_length=5, max_length=25, json_schema_extra={"example": "Ku-band"}
    )
    satellite_code: str = Field(
        ..., min_length=5, max_length=50, json_schema_extra={"example": "123_A_123_A"}
    )


class CoverageZoneCreate(CoverageZoneBase):
    image_data: bytes = Field(
        ...,
        description="Бинарные данные изображения",
    )


class CoverageZoneInDB(CoverageZoneBase):
    image_data: str = Field(
        ...,
        min_length=5,
        max_length=90,
        description="Ссылка на изображение в S3 хранилище",
    )


class CoverageZoneUpdate(BaseModel):
    image_data: Optional[bytes] = Field(
        None,
        description="Бинарные данные изображения",
    )
    transmitter_type: Optional[str] = Field(
        None, min_length=5, max_length=25, json_schema_extra={"example": "Ku-band"}
    )
    satellite_code: Optional[str] = Field(
        None, min_length=5, max_length=50, json_schema_extra={"example": "123_A_123_A"}
    )


class NumberOfZones(BaseModel):
    number_of_coverage_zones: int = Field(..., ge=0, json_schema_extra={"example": 15})
