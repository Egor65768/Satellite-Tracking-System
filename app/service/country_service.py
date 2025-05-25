from __future__ import annotations
from app.schemas import (
    CountryCreate,
    CountryInDB,
    CountryFind,
    CountryUpdate,
    Object_ID,
    PaginationBase,
    SatelliteInDB,
)
from typing import Optional, List
from typing import TYPE_CHECKING
from pydantic import ValidationError

if TYPE_CHECKING:
    from app.db import CountryRepository


class CountryService:
    def __init__(self, repository: CountryRepository):
        self.repository = repository

    @staticmethod
    async def _get_validated_abbreviation(abbreviation: str) -> Optional[CountryFind]:
        try:
            return CountryFind(abbreviation=abbreviation)
        except ValidationError:
            return None

    @staticmethod
    async def _get_validated_object_id(country_id: int) -> Optional[Object_ID]:
        try:
            return Object_ID(id=country_id)
        except ValidationError:
            return None

    async def get_by_abbreviation(self, abbreviation: str) -> Optional[CountryInDB]:
        abbreviation = await self._get_validated_abbreviation(abbreviation)
        return (
            await self.repository.get_by_abbreviation(abbreviation)
            if abbreviation
            else None
        )

    async def create_country(
        self, country_data: CountryCreate
    ) -> Optional[CountryInDB]:
        country = await self.repository.create_entity(country_data)
        if country is not None:
            await self.repository.session.commit()
        return country

    async def delete_country(self, country_id: int) -> bool:
        object_id = await self._get_validated_object_id(country_id)
        if not object_id:
            return False
        res = await self.repository.delete_model(object_id)
        if res:
            await self.repository.session.commit()
        return res

    async def update_country(
        self, country_id: int, country_data_update: CountryUpdate
    ) -> Optional[CountryInDB]:
        country_id = await self._get_validated_object_id(country_id)
        if not country_id:
            return None
        country = await self.repository.update_model(country_id, country_data_update)
        if country is not None:
            await self.repository.session.commit()
        return country

    async def get_countries(self, pagination: PaginationBase) -> List[CountryInDB]:
        return await self.repository.get_models(pagination)

    async def get_country(self, country_id: int) -> Optional[CountryInDB]:
        return await self.repository.get_as_model(Object_ID(id=country_id))

    async def get_satellites_by_country_id(
        self, country_id: int
    ) -> Optional[List[SatelliteInDB]]:
        return await self.repository.get_satellite_list(Object_ID(id=country_id))
