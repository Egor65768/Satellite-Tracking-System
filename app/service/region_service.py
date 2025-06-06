from app.db import RegionRepository, SubregionRepository
from app.schemas import (
    RegionInDB,
    SubregionInDB,
    Object_ID,
    RegionBase,
    SubregionBase,
    RegionCreate,
    SubregionCreate,
    RegionUpdate,
    SubregionUpdate,
    PaginationBase,
)
from typing import Optional, List
from pydantic import ValidationError


class RegionService:
    def __init__(
        self,
        region_repository: RegionRepository,
        subregion_repository: SubregionRepository,
    ):
        self.region_repository = region_repository
        self.subregion_repository = subregion_repository

    @staticmethod
    async def _get_validated_id(satellite_id: int) -> Optional[Object_ID]:
        try:
            return Object_ID(id=satellite_id)
        except ValidationError:
            return None

    async def get_region_by_id(self, region_id: int) -> Optional[RegionInDB]:
        object_id = await self._get_validated_id(region_id)
        return (
            await self.region_repository.get_as_model(object_id)
            if object_id is not None
            else None
        )

    async def get_subregion_by_id(self, subregion_id: int) -> Optional[SubregionInDB]:
        object_id = await self._get_validated_id(subregion_id)
        return (
            await self.subregion_repository.get_as_model(object_id)
            if object_id is not None
            else None
        )

    async def get_region_by_name(self, region_name: str) -> Optional[RegionInDB]:
        try:
            return await self.region_repository.get_region_by_name(
                RegionBase(name_region=region_name)
            )
        except ValidationError:
            return None

    async def get_subregion_by_name(
        self, subregion_name: str
    ) -> Optional[SubregionInDB]:
        try:
            return await self.subregion_repository.get_subregion_by_name(
                SubregionBase(name_subregion=subregion_name)
            )
        except ValidationError:
            return None

    async def get_regions(self, pagination: PaginationBase) -> List[RegionInDB]:
        return await self.region_repository.get_models(pagination)

    async def get_subregions(self, pagination: PaginationBase) -> List[SubregionInDB]:
        return await self.subregion_repository.get_models(pagination)

    async def create_region(self, region_create: RegionCreate) -> Optional[RegionInDB]:
        region = await self.region_repository.create_entity(region_create)
        if region is not None:
            await self.region_repository.session.commit()
        return region

    async def create_subregion(
        self, subregion_create: SubregionCreate
    ) -> Optional[SubregionInDB]:
        subregion = await self.subregion_repository.create_entity(subregion_create)
        if subregion is not None:
            await self.subregion_repository.session.commit()
        return subregion

    async def delete_region(self, region_id: int) -> bool:
        object_id = await self._get_validated_id(region_id)
        if not object_id:
            return False
        subregion_list = await self.get_subregions_by_region_id(object_id.id)
        if subregion_list is not None:
            for subregion in subregion_list:
                if not await self.delete_subregion(subregion.id):
                    return False
        result = await self.region_repository.delete_model(object_id)
        if result:
            await self.region_repository.session.commit()
        return result

    async def delete_subregion(self, subregion_id: int) -> bool:
        object_id = await self._get_validated_id(subregion_id)
        if not object_id:
            return False
        result = await self.subregion_repository.delete_model(object_id)
        if result:
            await self.region_repository.session.commit()
        return result

    async def update_region(
        self, region_id: int, region_update_data: RegionUpdate
    ) -> Optional[RegionInDB]:
        object_id = await self._get_validated_id(region_id)
        if not object_id:
            return None
        update_object = await self.region_repository.update_model(
            object_id, region_update_data
        )
        if update_object:
            await self.region_repository.session.commit()
        return update_object

    async def update_subregion(
        self, subregion_id: int, subregion_update: SubregionUpdate
    ) -> Optional[SubregionInDB]:
        if (
            subregion_update.id_region is None
            and subregion_update.name_subregion is None
        ):
            return None
        object_id = await self._get_validated_id(subregion_id)
        if not object_id:
            return None
        update_object = await self.subregion_repository.update_model(
            object_id, subregion_update
        )
        if update_object:
            await self.region_repository.session.commit()
        return update_object

    async def get_subregions_by_region_id(
        self, region_id: int
    ) -> Optional[List[SubregionInDB]]:
        object_id = await self._get_validated_id(region_id)
        return (
            await self.region_repository.get_subregions(object_id)
            if object_id is not None
            else None
        )

    async def get_region_by_subregion_id(
        self, subregion_id: int
    ) -> Optional[RegionInDB]:
        object_id = await self._get_validated_id(subregion_id)
        return (
            await self.subregion_repository.get_region(object_id)
            if object_id is not None
            else None
        )
