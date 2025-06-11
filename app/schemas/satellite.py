from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, ClassVar


class SatelliteBase(BaseModel):
    """Базовая схема спутника"""

    international_code: str = Field(
        ...,
        max_length=50,
        description="Международный код спутника",
        json_schema_extra={"example": "2002-007A"},
    )
    name_satellite: str = Field(
        ...,
        max_length=100,
        description="Название спутника",
        json_schema_extra={"example": "Yamal-401"},
    )
    norad_id: int = Field(
        ..., description="NORAD ID спутника", json_schema_extra={"example": 56756}
    )
    launch_date: date = Field(
        ...,
        description="Дата запуска",
        json_schema_extra={
            "example": "2002-12-07",
        },
    )
    country_id: int = Field(
        ..., description="ID страны", json_schema_extra={"example": "1"}
    )


class SatelliteCreate(SatelliteBase):
    """Схема для создания спутника"""

    pass


class SatelliteInDB(SatelliteBase):
    """Схема спутника в БД"""

    model_config = ConfigDict(from_attributes=True)


class SatelliteUpdate(SatelliteBase):
    """Схема для обновления спутника (все поля необязательные)"""

    international_code: Optional[str] = Field(
        None,
        max_length=50,
        description="Международный код спутника",
        json_schema_extra={"example": "2002-007A"},
    )
    name_satellite: Optional[str] = Field(
        None,
        max_length=100,
        description="Название спутника",
        json_schema_extra={"example": "Yamal-401"},
    )
    norad_id: Optional[int] = Field(
        None, description="NORAD ID спутника", json_schema_extra={"example": 56756}
    )
    launch_date: Optional[date] = Field(
        None,
        description="Дата запуска",
        json_schema_extra={"example": "2002-12-7"},
    )
    country_id: Optional[int] = Field(
        None, description="ID страны", json_schema_extra={"example": "1"}
    )

    _is_satellite: ClassVar[bool] = True


class SatelliteCharacteristicBase(BaseModel):
    """Базовая схема характеристик спутника"""

    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Долгота орбиты в градусах (-180 до 180)",
        json_schema_extra={"example": 171.1},
    )
    period: Optional[float] = Field(
        None,
        gt=0,
        description="Период обращения в минутах",
        json_schema_extra={"example": 1171.2},
    )
    launch_site: str = Field(
        ...,
        max_length=100,
        description="Место запуска",
        json_schema_extra={"example": "Cape Canaveral"},
    )
    rocket: str = Field(
        ...,
        max_length=50,
        description="Ракета-носитель",
        json_schema_extra={"example": "Falcon 9"},
    )
    launch_mass: Optional[float] = Field(
        None,
        gt=0,
        description="Масса при запуске в кг",
        json_schema_extra={"example": 1223435.1},
    )
    manufacturer: str = Field(
        ...,
        max_length=100,
        description="Производитель",
        json_schema_extra={"example": "SpaceX"},
    )
    model: str = Field(..., max_length=50, description="Модель спутника")
    expected_lifetime: int = Field(
        ...,
        gt=0,
        description="Ожидаемый срок службы в годах",
        json_schema_extra={"example": "A2100A"},
    )
    remaining_lifetime: int = Field(
        ...,
        description="Оставшийся срок службы в годах",
        json_schema_extra={"example": 5},
    )
    details: Optional[str] = Field(
        None,
        description="Дополнительные технические характеристики",
        json_schema_extra={
            "example": "24 Ku- and 24 C-band to provide broadcasting, business, cable services to CONUS, Hawaii, Caribbean and southern Canada"
        },
    )


class SatelliteCharacteristicUpdate(BaseModel):
    """Схема для обновления характеристик спутника (все поля необязательные)"""

    longitude: Optional[float] = Field(
        None,
        ge=-180,
        le=180,
        description="Долгота орбиты в градусах (-180 до 180)",
        json_schema_extra={"example": 171.1},
    )
    period: Optional[float] = Field(
        None,
        gt=0,
        description="Период обращения в минутах",
        json_schema_extra={"example": 1171.2},
    )
    launch_site: Optional[str] = Field(
        None,
        max_length=100,
        description="Место запуска",
        json_schema_extra={"example": "Cape Canaveral"},
    )
    rocket: Optional[str] = Field(
        None,
        max_length=50,
        description="Ракета-носитель",
        json_schema_extra={"example": "Falcon 9"},
    )
    launch_mass: Optional[float] = Field(
        None,
        gt=0,
        description="Масса при запуске в кг",
        json_schema_extra={"example": 1223435.1},
    )
    manufacturer: Optional[str] = Field(
        None,
        max_length=100,
        description="Производитель",
        json_schema_extra={"example": "SpaceX"},
    )
    model: Optional[str] = Field(None, max_length=50, description="Модель спутника")
    expected_lifetime: Optional[int] = Field(
        None,
        gt=0,
        description="Ожидаемый срок службы в годах",
        json_schema_extra={"example": "A2100A"},
    )
    remaining_lifetime: Optional[int] = Field(
        None,
        description="Оставшийся срок службы в годах",
        json_schema_extra={"example": 5},
    )
    details: Optional[str] = Field(
        None,
        description="Дополнительные технические характеристики",
        json_schema_extra={
            "example": "24 Ku- and 24 C-band to provide broadcasting, business, cable services to CONUS, Hawaii, Caribbean and southern Canada"
        },
    )


class SatelliteCharacteristicCreate(SatelliteCharacteristicBase):
    """Схема для создания характеристик спутника"""

    international_code: str = Field(
        ..., max_length=50, description="Международный код спутника"
    )


class SatelliteCharacteristicInDB(SatelliteCharacteristicCreate):
    """Схема характеристик спутника в БД"""

    pass


class SatelliteCompleteInfo(SatelliteInDB, SatelliteCharacteristicBase):
    """Полная информация о спутнике"""


class SatelliteCompleteUpdate(SatelliteUpdate, SatelliteCharacteristicUpdate):
    """Схема для обновления полной информации о спутнике"""
