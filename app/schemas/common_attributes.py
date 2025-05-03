from pydantic import BaseModel, Field


class Object_ID(BaseModel):
    id: int = Field(
        gt=0,
        description="Id объекта",
    )


class Object_str_ID(BaseModel):
    id: str = Field(
        ..., min_length=5, max_length=60, json_schema_extra={"example": "2012-07B4-1"}
    )


class PaginationBase(BaseModel):
    limit: int = Field(
        default=100,
        gt=0,
        description="Максимальное количество возвращаемых элементов (по умолчанию: 100), должно быть больше 0",
    )
    offset: int = Field(
        default=0,
        ge=0,
        description="Смещение от начала (по умолчанию: 0), должно быть больше или равно 0",
    )
