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
from pydantic import ValidationError

if TYPE_CHECKING:
    from app.db import CountryRepository


class CountryService:
    def __init__(self, repository: CountryRepository):
        self.repository = repository

    async def get_by_abbreviation(self, abbreviation: str) -> Optional[CountryInDB]:
        try:
            abbreviation = CountryFind(abbreviation=abbreviation)
        except ValidationError:
            return None
        return await self.repository.get_by_abbreviation(abbreviation)

    async def create_country(
        self, country_data: CountryCreate
    ) -> Optional[CountryInDB]:
        country = await self.repository.create_entity(country_data)
        if country is not None:
            await self.repository.session.commit()
        return country

    async def delete_country(self, country_id: int) -> bool:
        try:
            object_id = Object_ID(id=country_id)
        except ValidationError:
            print("ZZZZZZZZZ")
            return False
        res = await self.repository.delete_model(object_id)
        if res:
            await self.repository.session.commit()
        return res

    async def update_country(
        self, country_id: int, country_data_update: CountryUpdate
    ) -> Optional[CountryInDB]:
        try:
            country_id = Object_ID(id=country_id)
        except ValidationError:
            return None
        country = await self.repository.update_model(country_id, country_data_update)
        if country is not None:
            await self.repository.session.commit()
        return country

    async def get_countries(self, pagination: PaginationBase) -> List[CountryInDB]:
        return await self.repository.get_models(pagination)

    async def get_country(self, country_id: int) -> Optional[CountryInDB]:
        return await self.repository.get_as_model(Object_ID(id=country_id))
