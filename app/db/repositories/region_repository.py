from .repository import BaseRepository
from app.db import Region, Subregion
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import RegionCreate, RegionInDB
from typing import Optional


class RegionRepository(BaseRepository[Region]):
    def __init__(self, session: AsyncSession):
        super().__init__(Region, session)
        self.in_db_type = RegionInDB
