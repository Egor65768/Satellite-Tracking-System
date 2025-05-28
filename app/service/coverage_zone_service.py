from app.db import CoverageZoneRepository
from app.schemas import CoverageZoneInDB, Object_str_ID, RegionInDB, SatelliteInDB
from typing import Optional, List
from pydantic import ValidationError


class CoverageZoneService:
    def __init__(self, repository: CoverageZoneRepository):
        self.repository = repository

    @staticmethod
    async def _get_validated_object_id(
        coverage_zone_id: str,
    ) -> Optional[Object_str_ID]:
        try:
            return Object_str_ID(id=coverage_zone_id)
        except ValidationError:
            return None

    async def get_by_id(self, coverage_zone_id: str) -> Optional[CoverageZoneInDB]:
        coverage_zone_id = await self._get_validated_object_id(coverage_zone_id)
        return (
            await self.repository.get_as_model(coverage_zone_id)
            if coverage_zone_id is not None
            else None
        )

    async def get_coverage_zones_by_satellite_international_code(
        self, satellite_international_code: str
    ) -> Optional[List[CoverageZoneInDB]]:
        satellite_international_code = await self._get_validated_object_id(
            satellite_international_code
        )
        return (
            await self.repository.get_zone_list_by_satellite_id(
                satellite_international_code
            )
            if satellite_international_code is not None
            else None
        )

    async def get_region_list_by_id(
        self, coverage_zone_id: str
    ) -> Optional[RegionInDB]:
        coverage_zone_id = await self._get_validated_object_id(coverage_zone_id)
        return (
            await self.repository.get_region_list(coverage_zone_id)
            if coverage_zone_id is not None
            else None
        )

    async def get_satellite(self, coverage_zone_id: str) -> Optional[SatelliteInDB]:
        coverage_zone_id = await self._get_validated_object_id(coverage_zone_id)
        return (
            await self.repository.get_satellite(coverage_zone_id)
            if coverage_zone_id is not None
            else None
        )
