from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import CountryUpdate, CountryCreate, CountryInDB
from app.db import Country

class country_repository:

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_county(self, county_data: CountryCreate) -> CountryInDB:
        county = Country(**county_data.model_dump())
        self.db.add(county)
        await self.db.commit()
        await self.db.refresh(county)
        return CountryInDB.model_validate(county)
