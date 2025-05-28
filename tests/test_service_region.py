import pytest
from app.schemas import (
    PaginationBase,
    RegionCreate,
    SubregionCreate,
    RegionUpdate,
    SubregionUpdate,
)
from app.service import create_region_service
from tests.test_data import region_test, test_subregion


class TestCreate:

    @pytest.mark.asyncio
    async def test_check_region_1(self, db_session):
        service = create_region_service(db_session)
        async with db_session.begin():
            assert len(await service.get_regions(PaginationBase())) == 0
            assert len(await service.get_subregions(PaginationBase())) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("region_data", region_test)
    async def test_create_region(self, db_session, region_data):
        service = create_region_service(db_session)
        async with db_session.begin():
            region = await service.create_region(RegionCreate(**region_data))
            assert region

    @pytest.mark.asyncio
    @pytest.mark.parametrize("subregion_data", test_subregion)
    async def test_create_subregion(self, db_session, subregion_data):
        service = create_region_service(db_session)
        async with db_session.begin():
            region = await service.get_region_by_name(subregion_data.get("name_region"))
            assert region
            create_subregion = {
                "id_region": region.id,
                "name_subregion": subregion_data.get("name_subregion"),
            }
            await service.create_subregion(SubregionCreate(**create_subregion))


class TestGet:

    @pytest.mark.asyncio
    async def test_get_region(self, db_session):
        service = create_region_service(db_session)
        async with db_session.begin():
            regions = await service.get_regions(PaginationBase())
            assert len(regions) != 0
            region = region_test[0]
            region_db = await service.get_region_by_name(region.get("name_region"))
            assert region_db
            assert region_db.name_region == region.get("name_region")
            region_id = region_db.id
            assert region_id
            region_get_by_id = await service.get_region_by_id(region_id)
            assert region_get_by_id
            assert region_get_by_id.name_region == region.get("name_region")
            assert region_get_by_id.id == region_id

    @pytest.mark.asyncio
    async def test_get_subregion(self, db_session):
        service = create_region_service(db_session)
        async with db_session.begin():
            subregions = await service.get_subregions(PaginationBase())
            assert len(subregions) != 0
            subregion = test_subregion[0]
            subregion_db = await service.get_subregion_by_name(
                subregion.get("name_subregion")
            )
            assert subregion_db
            assert subregion_db.name_subregion == subregion.get("name_subregion")
            subregion_id = subregion_db.id
            assert subregion_id
            subregion_get_by_id = await service.get_subregion_by_id(subregion_id)
            assert subregion_get_by_id
            assert subregion_get_by_id.name_subregion == subregion.get("name_subregion")
            assert subregion_get_by_id.id == subregion_id

    async def test_get_invalid(self, db_session):
        service = create_region_service(db_session)
        async with db_session.begin():
            region_id = -1
            assert not await service.get_region_by_id(region_id)
            region_name = "A" * 150
            assert not await service.get_region_by_name(region_name)
            assert not await service.get_subregion_by_name(region_name)

    async def test_get_region_by_subregion_id(self, db_session):
        service = create_region_service(db_session)
        async with db_session.begin():
            subregion_name = "Texas"
            region_name = "USA"
            subregion_db = await service.get_subregion_by_name(subregion_name)
            assert subregion_db.name_subregion == subregion_name
            region_subregions = await service.get_region_by_subregion_id(
                subregion_db.id
            )
            assert region_subregions.name_region == region_name

    async def test_get_subregion_by_region_id(self, db_session):
        service = create_region_service(db_session)
        async with db_session.begin():
            region_name = "USA"
            subregions_name = [
                "Texas",
                "New York",
                "California",
                "Las Vegas",
                "Florida",
            ]
            region_db = await service.get_region_by_name(region_name)
            assert region_db.name_region == region_name
            subregions = await service.get_subregions_by_region_id(region_db.id)
            assert subregions
            assert len(subregions_name) == len(subregions)
            for subregion in subregions:
                assert subregion.name_subregion in subregions_name


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_region(self, db_session):
        service = create_region_service(db_session)
        async with db_session.begin():
            region_update = RegionUpdate(name_region="US")
            region_id = (await service.get_region_by_name("USA")).id
            assert await service.update_region(region_id, region_update)

        async with db_session.begin():
            assert (await service.get_region_by_id(region_id)).name_region == "US"

    @pytest.mark.asyncio
    async def test_update_region_invalid(self, db_session):
        service = create_region_service(db_session)
        async with db_session.begin():
            region_update = RegionUpdate(name_region="Russia")
            region_id = (await service.get_region_by_name("US")).id
            assert not await service.update_region(region_id, region_update)

        async with db_session.begin():
            assert (await service.get_region_by_id(region_id)).name_region == "US"

    @pytest.mark.asyncio
    async def test_update_subregion(self, db_session):
        service = create_region_service(db_session)
        async with db_session.begin():
            update_data = {"name_subregion": "NY"}
            subregion_id = (await service.get_subregion_by_name("New York")).id
            assert await service.update_subregion(
                subregion_id, SubregionUpdate(**update_data)
            )
        async with db_session.begin():
            assert (
                await service.get_subregion_by_id(subregion_id)
            ).name_subregion == "NY"

    @pytest.mark.asyncio
    async def test_update_subregion_invalid(self, db_session):
        service = create_region_service(db_session)
        async with db_session.begin():
            update_data = {"name_subregion": "Moscow"}
            subregion_id = (await service.get_subregion_by_name("NY")).id
            assert not await service.update_subregion(
                subregion_id, SubregionUpdate(**update_data)
            )

        async with db_session.begin():
            assert (
                await service.get_subregion_by_id(subregion_id)
            ).name_subregion == "NY"


class TestDelete:

    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        service = create_region_service(db_session)
        async with db_session.begin():
            regions = await service.get_regions(PaginationBase())
            assert len(regions) == len(region_test)
            assert not await service.delete_region(regions[0].id)

        async with db_session.begin():
            subregions = await service.get_subregions(PaginationBase())
            assert len(subregions) == len(test_subregion)
        for subregion in subregions:
            async with db_session.begin():
                assert await service.delete_subregion(subregion.id)
        async with db_session.begin():
            assert len(await service.get_subregions(PaginationBase())) == 0

        async with db_session.begin():
            regions = await service.get_regions(PaginationBase())
            assert len(regions) == len(region_test)
        for region in regions:
            async with db_session.begin():
                assert await service.delete_region(region.id)
        async with db_session.begin():
            assert len(await service.get_regions(PaginationBase())) == 0
