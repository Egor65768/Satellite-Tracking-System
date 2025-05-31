from app.db import CoverageZoneRepository
from app.schemas import (
    CoverageZoneInDB,
    Object_str_ID,
    ZoneRegionDetails,
    SatelliteInDB,
    CoverageZoneCreate,
    RegionBase,
    SubregionCreate,
    SubregionBase,
    CoverageZoneUpdate,
    PaginationBase,
)
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
    ) -> Optional[List[ZoneRegionDetails]]:
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

    async def get_coverage_zones(
        self, pagination: PaginationBase
    ) -> List[CoverageZoneInDB]:
        return await self.repository.get_models(pagination)

    async def get_count_coverage_zone_in_db(self) -> Optional[int]:
        return await self.repository.get_count()

    async def create_coverage_zone(
        self, coverage_zone_create: CoverageZoneCreate
    ) -> Optional[CoverageZoneInDB]:
        res = await self.repository.create_entity(coverage_zone_create)
        if res is not None:
            await self.repository.session.commit()
        return res

    async def add_region_by_coverage_zone_id(
        self, coverage_zone_id: str, region: RegionBase
    ) -> bool:
        coverage_zone_id = await self._get_validated_object_id(coverage_zone_id)
        if coverage_zone_id is None:
            return False
        res = await self.repository.add_region(region=region, zone_id=coverage_zone_id)
        if res:
            await self.repository.session.commit()
        return res

    async def delete_region_by_coverage_zone(
        self, coverage_zone_id: str, region: RegionBase
    ) -> bool:
        coverage_zone_id = await self._get_validated_object_id(coverage_zone_id)
        if coverage_zone_id is None:
            return False
        res = await self.repository.delete_region(
            region=region, zone_id=coverage_zone_id
        )
        if res:
            await self.repository.session.commit()
        return res

    async def add_subregion_by_coverage_zone_id(
        self, coverage_zone_id: str, subregion: SubregionCreate
    ) -> bool:
        coverage_zone_id = await self._get_validated_object_id(coverage_zone_id)
        if coverage_zone_id is None:
            return False
        res = await self.repository.add_subregion(
            subregion=subregion, zone_id=coverage_zone_id
        )
        if res:
            await self.repository.session.commit()
        return res

    async def delete_subregion_by_coverage_zone(
        self, coverage_zone_id: str, subregion: SubregionBase
    ) -> bool:
        coverage_zone_id = await self._get_validated_object_id(coverage_zone_id)
        if coverage_zone_id is None:
            return False
        res = await self.repository.delete_subregion(
            subregion=subregion, zone_id=coverage_zone_id
        )
        if res:
            await self.repository.session.commit()
        return res

    async def update_coverage_zone(
        self, coverage_zone_id: str, coverage_zone_update: CoverageZoneUpdate
    ) -> Optional[CoverageZoneInDB]:
        coverage_zone_id = await self._get_validated_object_id(coverage_zone_id)
        return (
            await self.repository.update_model(coverage_zone_id, coverage_zone_update)
            if coverage_zone_id is not None
            else None
        )

    async def delete_coverage_zone(self, coverage_zone_id: str) -> Optional[bool]:
        coverage_zone_id = await self._get_validated_object_id(coverage_zone_id)
        if not coverage_zone_id:
            return None
        region_list = await self.get_region_list_by_id(coverage_zone_id.id)
        for region in region_list:
            await self.delete_region_by_coverage_zone(
                coverage_zone_id.id, RegionBase(name_region=region.name_region)
            )
        res = await self.repository.delete_model(coverage_zone_id)
        if res:
            await self.repository.session.commit()
        return res
