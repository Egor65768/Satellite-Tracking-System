from __future__ import annotations
from app.schemas import (
    CountryCreate,
    CountryInDB,
    CountryFind,
    CountryUpdate,
    Object_ID,
    PaginationBase,
)
from typing import Optional, List
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.db import CountryRepository


class CountryService:
    def __init__(self, repository: CountryRepository):
        self.repository = repository

    async def get_by_abbreviation(
        self, abbreviation: CountryFind
    ) -> Optional[CountryInDB]:
        return await self.repository.get_by_abbreviation(abbreviation)

    async def create_country(
        self, country_data: CountryCreate
    ) -> Optional[CountryInDB]:
        return await self.repository.create_entity(country_data)

    async def delete_country(self, country_id: Object_ID) -> bool:
        return await self.repository.delete_model(country_id)

    async def update_country(
        self, country_id: Object_ID, country_data_update: CountryUpdate
    ) -> Optional[CountryInDB]:
        return await self.repository.update_model(country_id, country_data_update)

    async def get_countries(self, pagination: PaginationBase) -> List[CountryInDB]:
        return await self.repository.get_models(pagination)
