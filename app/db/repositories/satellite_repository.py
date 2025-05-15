from .repository import BaseRepository
from app.db import Satellite, SatelliteCharacteristic
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import (
    SatelliteCreate,
    SatelliteInDB,
    SatelliteCharacteristicInDB,
    SatelliteCharacteristicCreate,
    SatelliteCompleteInfo,
)
from typing import Optional
from app.schemas import Object_str_ID
from sqlalchemy import select, delete, Column
from typing import Type, TypeVar, cast

T = TypeVar("T", bound="Base")


async def delete_model_by_international_code(
    session: AsyncSession, object_id: Object_str_ID, model: Type[T]
) -> bool:
    international_code_column = cast(Column, model.international_code)
    query = delete(model).where(international_code_column == object_id.id)
    result = await session.execute(query)
    number_lines_removed: int = result.rowcount  # type: ignore[attr-defined]
    return number_lines_removed > 0


class SatelliteCharacteristicRepository(BaseRepository[SatelliteCharacteristic]):
    def __init__(self, session: AsyncSession):
        super().__init__(SatelliteCharacteristic, session)
        self.in_db_type = SatelliteCharacteristicInDB

    async def delete_model(self, object_id: Object_str_ID) -> bool:
        return await delete_model_by_international_code(
            self.session, object_id, SatelliteCharacteristic
        )


class SatelliteRepository(BaseRepository[Satellite]):
    def __init__(self, session: AsyncSession):
        super().__init__(Satellite, session)
        self.in_db_type = SatelliteInDB

    async def delete_model(self, object_id: Object_str_ID) -> bool:
        await delete_model_by_international_code(
            self.session, object_id, SatelliteCharacteristic
        )
        return await delete_model_by_international_code(
            self.session, object_id, Satellite
        )

    async def create_satellite(
        self, satellite: SatelliteCreate, characteristic: SatelliteCharacteristicCreate
    ) -> Optional[SatelliteCompleteInfo]:
        satellite_db = await self.create(**satellite.model_dump())
        if satellite_db is None:
            return None
        satellite_characteristic_db = SatelliteCharacteristic(
            **characteristic.model_dump(), satellite=satellite_db
        )
        self.session.add(satellite_characteristic_db)
        await self.session.flush()
        return SatelliteCompleteInfo(
            **satellite.model_dump(),
            **characteristic.model_dump(exclude={"international_code"})
        )

    async def get_complete_info(
        self, satellite_id: Object_str_ID
    ) -> Optional[SatelliteCompleteInfo]:
        query = select(Satellite).where(Satellite.international_code == satellite_id.id)
        satellite: Optional[Satellite] = (
            await self.session.execute(query)
        ).scalar_one_or_none()
        if satellite is None:
            return None
        satellite_data = SatelliteInDB(**satellite.__dict__)
        if satellite.characteristics is not None:
            satellite_characteristic_data = SatelliteCharacteristicInDB(
                **satellite.characteristics.__dict__
            )
            dict_satellite_characteristic = satellite_characteristic_data.model_dump()
            dict_satellite_characteristic.pop("international_code")
            return SatelliteCompleteInfo(
                **satellite_data.model_dump(), **dict_satellite_characteristic
            )
        return None
