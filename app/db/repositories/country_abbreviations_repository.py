from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import CountryInDB, CountryFind, SatelliteInDB, Object_ID

from .repository import BaseRepository
from typing import Optional, List
from app.db import Country


class CountryRepository(BaseRepository[Country]):

    def __init__(self, session: AsyncSession):
        super().__init__(Country, session)
        self.in_db_type = CountryInDB

    async def get_by_abbreviation(
        self, abbreviation: CountryFind
    ) -> Optional[CountryInDB]:
        return await self.get_by_field(
            field_name="abbreviation", field_value=abbreviation.abbreviation
        )

    async def get_satellite_list(
        self, country_id: Object_ID
    ) -> Optional[List[SatelliteInDB]]:
        country: Optional[Country] = await self.get_by_id(country_id.id)
        if country is None:
            return None
        sat_list = [
            SatelliteInDB(**satellite.__dict__) for satellite in country.satellites
        ]
        return sat_list
