from pydantic import BaseModel, Field


class CoverageZoneBase(BaseModel):
    id: str = Field(
        ..., min_length=5, max_length=60, json_schema_extra={"example": "2012-07B4-1"}
    )
    transmitter_type: str = Field(
        ..., min_length=5, max_length=25, json_schema_extra={"example": "Ku-band"}
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
