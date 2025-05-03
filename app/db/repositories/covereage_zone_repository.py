from .repository import BaseRepository
from typing import Optional
from app.db import CoverageZone
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import CoverageZoneInDB, CoverageZoneCreate, Object_str_ID
from app.service import S3Service


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
