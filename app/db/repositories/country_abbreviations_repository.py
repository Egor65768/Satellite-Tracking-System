from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import (
    CountryUpdate,
    CountryCreate,
    CountryInDB,
    Object_ID,
    PaginationBase,
)
from app.db import Country
from .repository import Repository
from typing import Optional, List


class CountryRepository(Repository[Country]):

    def __init__(self, session: AsyncSession):
        super().__init__(Country, session)

    async def create_country(self, country: CountryCreate) -> Optional[CountryInDB]:
        country_db = await self.create(**country.model_dump())
        if country_db is None:
            return None
        return CountryInDB(**country_db.__dict__)

    async def get_country_by_id(self, country_id: Object_ID) -> Optional[CountryInDB]:
        country_db = await self.get_by_id(**country_id.model_dump())
        return CountryInDB(**country_db.__dict__) if country_db is not None else None

    async def get_countries(self, pagination: PaginationBase) -> List[CountryInDB]:
        countries_db = await self.get_multi(**pagination.model_dump())
        return [CountryInDB(**country.__dict__) for country in countries_db]
