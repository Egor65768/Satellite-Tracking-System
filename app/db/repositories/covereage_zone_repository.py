from .repository import BaseRepository
from typing import Optional, List
from app.db import CoverageZone, Region
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import (
    CoverageZoneInDB,
    CoverageZoneCreate,
    Object_str_ID,
    ZoneRegionDetails,
    Subregion,
    RegionBase,
)
from app.service import S3Service
from sqlalchemy import select


class CoverageZoneRepository(BaseRepository[CoverageZone]):
    def __init__(self, session: AsyncSession):
        super().__init__(CoverageZone, session)
        self.in_db_type = CoverageZoneInDB
        self.s3 = S3Service()
        self.base_endpoint = (
            "https://s3.ru-7.storage.selcloud.ru/satellite-tracking-system/"
        )

    async def create_entity(
        self, entity_create: CoverageZoneCreate
    ) -> Optional[CoverageZoneInDB]:
        file_key = f"zone/{entity_create.id}.jpg"
        if not await self.s3.upload_file(
            file_data=entity_create.image_data, file_key=file_key
        ):
            return None
        coverage_zone = CoverageZoneInDB(
            id=entity_create.id,
            transmitter_type=entity_create.transmitter_type,
            image_data=self.base_endpoint + file_key,
        )
        return await super().create_entity(coverage_zone)

    async def delete_model(self, object_id: Object_str_ID) -> bool:
        if not await super().delete_model(object_id):
            return False
        file_key = f"zone/{object_id.id}.jpg"
        await self.s3.delete_file(file_key)
        return True

    async def get_region_list(
        self, object_id: Object_str_ID
    ) -> Optional[List[ZoneRegionDetails]]:
        db_obj = await self.get_by_id(object_id.id)
        if db_obj is None:
            return None

        return [
            ZoneRegionDetails(
                id=region.id,
                name_region=region.name_region,
                subregion_list=[
                    Subregion(id=sr.id, name_subregion=sr.name_subregion)
                    for sr in db_obj.subregions
                    if sr.id_region == region.id
                ],
            )
            for region in db_obj.regions
        ]

    async def add_region(self, region: RegionBase, zone_id: Object_str_ID) -> bool:
        zone_db = await self.get_by_id(zone_id.id)
        if zone_db is None:
            return False
        if any(region.name_region == r.name_region for r in zone_db.regions):
            return True
        db_region = (
            await self.session.execute(
                select(Region).where(Region.name_region == region.name_region)
            )
        ).scalar_one_or_none()

        if db_region is None:
            db_region = Region(name_region=region.name_region)
            self.session.add(db_region)
            await self.session.flush()
        zone_db.regions.append(db_region)
        await self.session.flush()
        return True

    async def delete_region(self, region: RegionBase, zone_id: Object_str_ID) -> bool:
        zone_db = await self.get_by_id(zone_id.id)
        if not zone_db:
            return False
        region_to_remove = next(
            (r for r in zone_db.regions if r.name_region == region.name_region), None
        )
        if not region_to_remove:
            return False
        zone_db.regions.remove(region_to_remove)
        await self.session.flush()
        return True
