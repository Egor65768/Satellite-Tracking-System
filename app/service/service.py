from app.db import CountryRepository
from app.service import CountryService
from sqlalchemy.ext.asyncio import AsyncSession


def create_country_service(session: AsyncSession) -> CountryService:
    repo = CountryRepository(session)
    return CountryService(repo)
