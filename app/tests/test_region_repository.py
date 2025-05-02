import pytest
from app.db import RegionRepository, SubregionRepository
from app.schemas import (
    RegionCreate,
    RegionInDB,
    SubregionCreate,
    SubregionInDB,
    Object_ID,
    RegionUpdate,
    SubregionUpdate,
)
from typing import Optional
from sqlalchemy.exc import InvalidRequestError

region_test_data = [
    {"id": 1, "name_region": "China"},
    {"id": 2, "name_region": "Russia"},
    {"id": 3, "name_region": "USA"},
    {"id": 4, "name_region": "EU"},
    {"id": 5, "name_region": "South Africa"},
]

subregion_test_data = [
    {"name_subregion": "Wuhan", "id": 1, "id_region": 1},
    {"id": 2, "name_subregion": "Moscow", "id_region": 2},
    {"id": 3, "name_subregion": "Stavropol", "id_region": 2},
    {"id": 4, "name_subregion": "Saint Petersburg", "id_region": 2},
]
region_invalid_data = [
    {"id": 1, "name_region": "China"},
    {"id": 50, "name_region": "China"},
    {"id": 1, "name_region": "Norway"},
]

subregion_invalid_data = [
    {"id": 2, "name_subregion": "Moscow", "id_region": 2},
    {"id": 99, "name_subregion": "Moscow", "id_region": 2},
    {"id": 2, "name_subregion": "New York", "id_region": 2},
    {"id": 242, "name_subregion": "New York", "id_region": 15},
]


class TestCreate:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("region_data", region_test_data)
    async def test_create_region(self, db_session, region_data):
        async with db_session.begin():
            repo = RegionRepository(db_session)
            region: Optional[RegionInDB] = await repo.create_entity(
                RegionCreate(**region_data)
            )
            assert region is not None
            assert region.name_region == region_data["name_region"]
            assert region.id == region_data["id"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("subregion_data", subregion_test_data)
    async def test_create_subregion(self, db_session, subregion_data):
        async with db_session.begin():
            repo = SubregionRepository(db_session)
            repo_region = RegionRepository(db_session)
            region: Optional[RegionInDB] = await repo_region.get_as_model(
                Object_ID(id=subregion_data["id_region"])
            )
            assert region is not None
            subregion: Optional[SubregionInDB] = await repo.create_entity(
                SubregionCreate(**subregion_data)
            )
            assert subregion is not None
            assert subregion.name_subregion == subregion_data["name_subregion"]
            assert subregion.id == subregion_data["id"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("region_data", region_invalid_data)
    async def test_create_region_invalid(self, db_session, region_data):
        repo_region = RegionRepository(db_session)
        async with db_session.begin():
            region_db = await repo_region.create_entity(RegionCreate(**region_data))
            assert region_db is None
            with pytest.raises(InvalidRequestError):
                await repo_region.get_as_model(Object_ID(id=1))

    @pytest.mark.asyncio
    @pytest.mark.parametrize("subregion_data", subregion_invalid_data)
    async def test_create_region_invalid(self, db_session, subregion_data):
        repo_subregion = SubregionRepository(db_session)
        async with db_session.begin():
            subregion_db = await repo_subregion.create_entity(
                SubregionCreate(**subregion_data)
            )
            assert subregion_db is None
            with pytest.raises(InvalidRequestError):
                await repo_subregion.get_as_model(Object_ID(id=1))


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_region(self, db_session):
        repo = RegionRepository(db_session)
        async with db_session.begin():
            region_update = RegionUpdate(name_region="US")
            id_region = Object_ID(id=3)
            await repo.update_model(object_id=id_region, object_update=region_update)
            region: Optional[RegionInDB] = await repo.get_as_model(id_region)
            assert region.id == 3
            assert region.name_region == "US"
        async with db_session.begin():
            region_update = RegionUpdate(name_region="Russia")
            id_region = Object_ID(id=3)
            region = await repo.update_model(
                object_id=id_region, object_update=region_update
            )
            assert region is None
            with pytest.raises(InvalidRequestError):
                await repo.get_as_model(id_region)

    @pytest.mark.asyncio
    async def test_update_subregion(self, db_session):
        repo = SubregionRepository(db_session)
        async with db_session.begin():
            subregion_update = SubregionUpdate(name_subregion="Saratov")
            id_subregion = Object_ID(id=2)
            await repo.update_model(
                object_id=id_subregion, object_update=subregion_update
            )
            subregion: Optional[SubregionInDB] = await repo.get_as_model(id_subregion)
            assert subregion.id == 2
            assert subregion.name_subregion == subregion_update.name_subregion
        async with db_session.begin():
            subregion_update = SubregionUpdate(name_subregion="Saratov")
            id_subregion = Object_ID(id=3)
            await repo.update_model(
                object_id=id_subregion, object_update=subregion_update
            )
            with pytest.raises(InvalidRequestError):
                await repo.get_as_model(id_subregion)
        async with db_session.begin():
            subregion_update = SubregionUpdate(name_subregion="Serv")
            id_subregion = Object_ID(id=100)
            subregion = await repo.update_model(
                object_id=id_subregion, object_update=subregion_update
            )
            assert subregion is None
            assert await repo.get_as_model(id_subregion) is None
