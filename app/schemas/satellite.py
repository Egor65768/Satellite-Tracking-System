from datetime import date
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional


class SatelliteBase(BaseModel):
    """Базовая схема спутника"""

    international_code: str = Field(
        ..., max_length=50, description="Международный код спутника"
    )
    name_satellite: str = Field(..., max_length=100, description="Название спутника")
    norad_id: int = Field(..., description="NORAD ID спутника")
    launch_date: date = Field(..., description="Дата запуска")
    country_id: int = Field(..., description="ID страны")


class SatelliteCreate(SatelliteBase):
    """Схема для создания спутника"""

    pass


class SatelliteInDB(SatelliteBase):
    """Схема спутника в БД"""

    model_config = ConfigDict(from_attributes=True)


class SatelliteCharacteristicBase(BaseModel):
    """Базовая схема характеристик спутника"""

    longitude: Optional[float] = Field(
        None, ge=-180, le=180, description="Долгота орбиты в градусах (-180 до 180)"
    )
    period: Optional[float] = Field(
        None, gt=0, description="Период обращения в минутах"
    )
    launch_site: str = Field(..., max_length=100, description="Место запуска")
    rocket: str = Field(..., max_length=50, description="Ракета-носитель")
    launch_mass: Optional[float] = Field(
        None, gt=0, description="Масса при запуске в кг"
    )
    manufacturer: str = Field(..., max_length=100, description="Производитель")
    model: str = Field(..., max_length=50, description="Модель спутника")
    expected_lifetime: int = Field(
        ..., gt=0, description="Ожидаемый срок службы в месяцах"
    )
    remaining_lifetime: int = Field(..., description="Оставшийся срок службы в месяцах")
    details: Optional[str] = Field(
        None, description="Дополнительные технические характеристики"
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
