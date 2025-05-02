from .repository import BaseRepository
from app.db import Region, Subregion
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import RegionInDB, RegionBase, SubregionInDB, SubregionBase, Object_ID
from typing import Optional, List


class RegionRepository(BaseRepository[Region]):
    def __init__(self, session: AsyncSession):
        super().__init__(Region, session)
        self.in_db_type = RegionInDB

    async def get_region_by_name(self, region: RegionBase) -> Optional[RegionInDB]:
        return await self.get_by_field(
            field_name="name_region", field_value=region.name_region
        )

    async def get_subregions(
        self, region_id: Object_ID
    ) -> Optional[List[SubregionInDB]]:
        db_region = await self.get_by_id(region_id.id)
        if db_region is None:
            return None
        db_subregions: List[Subregion] = db_region.subregions
        subregions = []
        for subregion in db_subregions:
            subregions.append(SubregionInDB(**subregion.__dict__))
        return subregions


class SubregionRepository(BaseRepository[Subregion]):
    def __init__(self, session: AsyncSession):
        super().__init__(Subregion, session)
        self.in_db_type = SubregionInDB

    async def get_subregion_by_name(
        self, subregion: SubregionBase
    ) -> Optional[SubregionInDB]:
        return await self.get_by_field(
            field_name="name_subregion", field_value=subregion.name_subregion
        )

    async def get_region(self, subregion_id: Object_ID) -> Optional[RegionInDB]:
        db_subregion = await self.get_by_id(subregion_id.id)
        if db_subregion is None:
            return None
        db_region: Region = db_subregion.region
        return RegionInDB(**db_region.__dict__)
