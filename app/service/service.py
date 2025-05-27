from app.db import CountryRepository
from app.service import CountryService
from app.service import SatelliteService
from app.service import RegionService
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import (
    SatelliteRepository,
    SatelliteCharacteristicRepository,
    RegionRepository,
    SubregionRepository,
)


def create_country_service(session: AsyncSession) -> CountryService:
    repo = CountryRepository(session)
    return CountryService(repo)


def create_satellite_service(session: AsyncSession) -> SatelliteService:
    sat_repo = SatelliteRepository(session)
    sat_char_repo = SatelliteCharacteristicRepository(session)
    return SatelliteService(sat_repo, sat_char_repo)


def create_region_service(session: AsyncSession) -> RegionService:
    region_repo = RegionRepository(session)
    subregion_repo = SubregionRepository(session)
    return RegionService(region_repo, subregion_repo)
