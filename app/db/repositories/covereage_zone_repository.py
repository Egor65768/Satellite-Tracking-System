from sqlalchemy.exc import SQLAlchemyError
from .repository import BaseRepository
from typing import Optional, List
from app.db import CoverageZone, Region, Satellite, Subregion as Subregion_DB
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import (
    CoverageZoneInDB,
    CoverageZoneCreate,
    Object_str_ID,
    ZoneRegionDetails,
    Subregion,
    RegionBase,
    SubregionCreate,
    SubregionBase,
    SatelliteInDB,
    CoverageZoneUpdate,
)
from app.s3_service.s3_service import S3Service
from sqlalchemy import select
from pydantic import BaseModel


def all_fields_none(obj: BaseModel) -> bool:
    return all(v is None for v in obj.model_dump().values())


class CoverageZoneRepository(BaseRepository[CoverageZone]):
    def __init__(self, session: AsyncSession):
        super().__init__(CoverageZone, session)
        self.in_db_type = CoverageZoneInDB
        self.s3 = S3Service()
        self.S3_PREFIX = "zone/"
        self.base_endpoint = (
            "https://s3.ru-7.storage.selcloud.ru/satellite-tracking-system/"
        )

    async def get_s3_file_key(self, object_id: str) -> str:
        return f"{self.S3_PREFIX}{object_id}.jpg"

    async def create_entity(
        self, entity_create: CoverageZoneCreate
    ) -> Optional[CoverageZoneInDB]:
        file_key = await self.get_s3_file_key(entity_create.id)
        if not await self.s3.upload_file(
            file_data=entity_create.image_data, file_key=file_key
        ):
            return None
        coverage_zone = CoverageZoneInDB(
            id=entity_create.id,
            transmitter_type=entity_create.transmitter_type,
            image_data=self.base_endpoint + file_key,
            satellite_code=entity_create.satellite_code,
        )
        return await super().create_entity(coverage_zone)

    async def update_model(
        self, object_id: Object_str_ID, coverage_zone_update: CoverageZoneUpdate
    ) -> Optional[CoverageZoneInDB]:
        update = False
        res = None
        if coverage_zone_update.image_data is not None:
            update = True
            file_key = await self.get_s3_file_key(object_id.id)
            await self.s3.delete_file(file_key)
            if not await self.s3.upload_file(
                file_data=coverage_zone_update.image_data, file_key=file_key
            ):
                return None
            coverage_zone_update.image_data = None
            coverage_zone_update.model_fields_set.discard("image_data")
        if not all_fields_none(coverage_zone_update):
            res = await super().update_model(object_id, coverage_zone_update)
        elif update:
            res = await self.get_as_model(object_id)
        return res

    async def delete_model(self, object_id: Object_str_ID) -> bool:
        if not await super().delete_model(object_id):
            return False
        file_key = await self.get_s3_file_key(object_id.id)
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
        subregions_to_remove = [
            sr for sr in zone_db.subregions if sr.id_region == region_to_remove.id
        ]
        for subregion in subregions_to_remove:
            zone_db.subregions.remove(subregion)
        zone_db.regions.remove(region_to_remove)
        await self.session.flush()
        return True

    async def add_subregion(
        self, subregion: SubregionCreate, zone_id: Object_str_ID
    ) -> bool:
        zone_db = await self.get_by_id(zone_id.id)
        if not zone_db:
            return False
        if any(
            s.name_subregion == subregion.name_subregion
            for r in zone_db.regions
            if r.id == subregion.id_region
            for s in r.subregions
        ):
            return True
        if not any(subregion.id_region == r.id for r in zone_db.regions):
            region_db: Optional[Region] = await self.session.get(
                Region, subregion.id_region
            )
            if region_db is not None:
                zone_db.regions.append(region_db)
            else:
                return False

        db_subregion = (
            await self.session.execute(
                select(Subregion_DB).where(
                    Subregion_DB.name_subregion == subregion.name_subregion
                )
            )
        ).scalar_one_or_none()

        if db_subregion is None:
            db_subregion = Subregion_DB(
                name_subregion=subregion.name_subregion, id_region=subregion.id_region
            )
            self.session.add(db_subregion)
            await self.session.flush()

        zone_db.subregions.append(db_subregion)
        await self.session.flush()
        return True

    async def delete_subregion(
        self, subregion: SubregionBase, zone_id: Object_str_ID
    ) -> bool:
        zone_db = await self.get_by_id(zone_id.id)
        if not zone_db:
            return False
        subregion_to_remove = next(
            (
                s
                for s in zone_db.subregions
                if s.name_subregion == subregion.name_subregion
            ),
            None,
        )
        if not subregion_to_remove:
            return False
        region_id = subregion_to_remove.id_region
        should_remove_region = not any(
            sr.id_region == region_id
            for sr in zone_db.subregions
            if sr != subregion_to_remove  # Исключаем текущий подрегион
        )
        zone_db.subregions.remove(subregion_to_remove)
        if should_remove_region:
            region_to_remove = next(
                (r for r in zone_db.regions if r.id == region_id), None
            )
            if region_to_remove:
                zone_db.regions.remove(region_to_remove)
        try:
            await self.session.flush()
            return True
        except SQLAlchemyError:
            await self.session.rollback()
            return False

    async def get_satellite(self, zone_id: Object_str_ID) -> Optional[SatelliteInDB]:
        zone_db = await self.get_by_id(zone_id.id)
        if not zone_db:
            return None
        return SatelliteInDB(**zone_db.satellite.__dict__)

    async def get_zone_list_by_satellite_id(
        self, satellite_id: Object_str_ID
    ) -> Optional[List[CoverageZoneInDB]]:
        db_satellite: Optional[Satellite] = (
            await self.session.execute(
                select(Satellite).where(Satellite.international_code == satellite_id.id)
            )
        ).scalar_one_or_none()
        if db_satellite is None:
            return None
        Coverage_Zone_In_DB_List = list()
        coverage_zones_list = db_satellite.coverage_zones
        for coverage_zone in coverage_zones_list:
            Coverage_Zone_In_DB_List.append(CoverageZoneInDB(**coverage_zone.__dict__))
        return Coverage_Zone_In_DB_List
