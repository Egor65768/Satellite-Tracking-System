from sqlalchemy.util import await_only

from .repository import BaseRepository
from app.db import Region, Subregion
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import RegionInDB, RegionBase, SubregionInDB, SubregionBase
from typing import Optional


class RegionRepository(BaseRepository[Region]):
    def __init__(self, session: AsyncSession):
        super().__init__(Region, session)
        self.in_db_type = RegionInDB

    async def get_region_by_name(self, region: RegionBase) -> Optional[RegionInDB]:
        return await self.get_by_field(
            field_name="name_region", field_value=region.name_region
        )


class SubregionRepository(BaseRepository[Subregion]):
    def __init__(self, session: AsyncSession):
        super().__init__(Region, session)
        self.in_db_type = SubregionInDB

    async def get_subregion_by_name(
        self, subregion: SubregionBase
    ) -> Optional[SubregionInDB]:
        return await self.get_by_field(
            field_name="name_subregion", field_value=subregion.name_subregion
        )
