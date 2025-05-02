from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import (
    CountryInDB,
    CountryFind,
)
from app.db import Country
from .repository import BaseRepository
from typing import Optional


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
