from __future__ import annotations
from typing import Optional, List, TYPE_CHECKING
from pydantic import ValidationError

from app.schemas import (
    Object_str_ID,
    SatelliteInDB,
    SatelliteCompleteInfo,
    SatelliteCharacteristicInDB,
    SatelliteCreate,
    SatelliteCharacteristicCreate,
    PaginationBase,
    SatelliteUpdate,
    SatelliteCharacteristicUpdate,
)

if TYPE_CHECKING:
    from app.db import SatelliteRepository, SatelliteCharacteristicRepository


class SatelliteService:
    def __init__(
        self,
        repository: SatelliteRepository,
        characteristic_repository: SatelliteCharacteristicRepository,
    ):
        self.repository = repository
        self.characteristic_repository = characteristic_repository

    @staticmethod
    async def _get_validated_code(satellite_id: str) -> Optional[Object_str_ID]:
        try:
            return Object_str_ID(id=satellite_id)
        except ValidationError:
            return None

    async def get_satellite_by_id(self, satellite_id: str) -> Optional[SatelliteInDB]:
        if not await self._get_validated_code(satellite_id):
            return None
        return await self.repository.get_by_field(
            field_name="international_code", field_value=satellite_id
        )

    async def get_satellite_complete_info(
        self, satellite_id: str
    ) -> Optional[SatelliteCompleteInfo]:
        international_code = await self._get_validated_code(satellite_id)
        return (
            await self.repository.get_complete_info(international_code)
            if international_code
            else None
        )

    async def get_satellite_characteristics(
        self, satellite_id: str
    ) -> Optional[SatelliteCharacteristicInDB]:
        if not await self._get_validated_code(satellite_id):
            return None
        return await self.characteristic_repository.get_by_field(
            field_name="international_code", field_value=satellite_id
        )

    async def get_satellites(self, pagination: PaginationBase) -> List[SatelliteInDB]:
        return await self.repository.get_models(pagination)

    async def get_satellites_characteristics_list(
        self, pagination: PaginationBase
    ) -> List[SatelliteCharacteristicInDB]:
        return await self.characteristic_repository.get_models(pagination)

    async def create_satellite_base(
        self, satellite_data: SatelliteCreate
    ) -> Optional[SatelliteInDB]:
        return await self.repository.create_entity(satellite_data)

    async def create_full_satellite(
        self,
        satellite_data: SatelliteCreate,
        characteristic: SatelliteCharacteristicCreate,
    ) -> Optional[SatelliteCompleteInfo]:
        return await self.repository.create_satellite(satellite_data, characteristic)

    async def create_satellite_characteristic(
        self, satellite_characteristic: SatelliteCharacteristicCreate
    ) -> Optional[SatelliteCharacteristicInDB]:
        return await self.characteristic_repository.create_entity(
            satellite_characteristic
        )

    async def delete_characteristic(self, satellite_id: str) -> bool:
        international_code = await self._get_validated_code(satellite_id)
        return await self.characteristic_repository.delete_model(international_code)

    async def delete_satellite(self, satellite_id: str) -> bool:
        international_code = await self._get_validated_code(satellite_id)
        return await self.repository.delete_model(international_code)

    async def update_satellite(
        self, satellite_id: str, satellite_update_data: SatelliteUpdate
    ) -> Optional[SatelliteInDB]:
        international_code = await self._get_validated_code(satellite_id)
        return await self.repository.update_satellite(
            international_code, satellite_update_data
        )

    async def update_satellite_characteristic(
        self,
        satellite_id: str,
        satellite_characteristic_update_data: SatelliteCharacteristicUpdate,
    ) -> Optional[SatelliteCharacteristicInDB]:
        international_code = await self._get_validated_code(satellite_id)
        return await self.characteristic_repository.update_characteristic_satellite(
            international_code, satellite_characteristic_update_data
        )
