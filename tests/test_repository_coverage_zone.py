import pytest
import aiofiles
from typing import Optional, List

from app.db import (
    CoverageZoneRepository,
    RegionRepository,
    SubregionRepository,
    CountryRepository,
    SatelliteRepository,
)
from app.schemas import (
    CoverageZoneCreate,
    CoverageZoneInDB,
    PaginationBase,
    Object_ID,
    Object_str_ID,
    RegionInDB,
    RegionCreate,
    SubregionInDB,
    SubregionCreate,
    RegionBase,
    SubregionBase,
    ZoneRegionDetails,
    CountryCreate,
    SatelliteCreate,
    CoverageZoneUpdate,
)

from tests.test_data import (
    satellite_test_date,
    test_create_data,
    test_get_data,
    region_test_data,
    subregion_test_data,
)


async def get_data_image(path_img: str) -> Optional[bytes]:
    try:
        async with aiofiles.open(path_img, "rb") as f:
            image_date = await f.read()
        return image_date
    except FileNotFoundError:
        return None
    except PermissionError:
        return None


@pytest.mark.asyncio
async def test_create_country(db_session):
    country_repo = CountryRepository(db_session)
    country_data = {"abbreviation": "FA", "full_name": "Франция"}
    async with db_session.begin():
        assert await country_repo.create_entity(CountryCreate(**country_data))
        assert len(await country_repo.get_models(PaginationBase())) == 1


@pytest.mark.asyncio
@pytest.mark.parametrize("satellite_date", satellite_test_date)
async def test_create_satellite(db_session, satellite_date):
    repo = SatelliteRepository(db_session)
    async with db_session.begin():
        assert await repo.create_entity(SatelliteCreate(**satellite_date))


@pytest.mark.asyncio
@pytest.mark.parametrize("region_data", region_test_data)
async def test_create_regions(db_session, region_data):
    async with db_session.begin():
        repo = RegionRepository(db_session)
        region: Optional[RegionInDB] = await repo.create_entity(
            RegionCreate(**region_data)
        )
        assert region is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("subregion_data", subregion_test_data)
async def test_create_subregions(db_session, subregion_data):
    async with db_session.begin():
        repo = SubregionRepository(db_session)
        subregion: Optional[SubregionInDB] = await repo.create_entity(
            SubregionCreate(**subregion_data)
        )
        assert subregion is not None


class TestCreate:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("zone_data", test_create_data)
    async def test_create_1(self, db_session, zone_data):
        local_data = await get_data_image(zone_data["image"])
        coverage_zone = CoverageZoneCreate(
            id=zone_data["id"],
            transmitter_type=zone_data["transmitter_type"],
            image_data=local_data,
            satellite_code=satellite_test_date[0]["international_code"],
        )
        repo = CoverageZoneRepository(db_session)
        async with db_session.begin():
            zone: CoverageZoneInDB = await repo.create_entity(coverage_zone)
            assert zone is not None
            assert zone.id == zone_data["id"]
            assert zone.transmitter_type == zone_data["transmitter_type"]
            async with await repo.s3._get_client() as client:
                response = await client.get_object(
                    Bucket=repo.s3.bucket_name, Key=f"zone/{zone.id}.jpg"
                )
                s3_image_data = await response["Body"].read()
                assert local_data == s3_image_data


class TestGet:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("object_id,notNone", test_get_data)
    async def test_get_1(self, db_session, object_id, notNone):
        repo = CoverageZoneRepository(db_session)
        zone_id = Object_str_ID(id=object_id)
        async with db_session.begin():
            zone: Optional[CoverageZoneInDB] = await repo.get_as_model(zone_id)
            if notNone:
                assert zone is not None
                assert zone.id == object_id
                satellite = await repo.get_satellite(zone_id)
                assert satellite is not None
                assert satellite.norad_id == satellite_test_date[0]["norad_id"]
                assert (
                    satellite.name_satellite == satellite_test_date[0]["name_satellite"]
                )
            else:
                assert zone is None

    @pytest.mark.asyncio
    async def test_get_zones_by_satellite_int_code(self, db_session):
        international_code = satellite_test_date[0]["international_code"]
        repo = CoverageZoneRepository(db_session)
        async with db_session.begin():
            zones: Optional[List[CoverageZoneInDB]] = (
                await repo.get_zone_list_by_satellite_id(
                    Object_str_ID(id=international_code)
                )
            )
            assert zones is not None
            assert len(zones) == len(test_create_data)
            for zone in zones:
                assert zone.id in ["2021-12bd-23730", "2001-1234-24670"]
                assert zone.transmitter_type == "Ku-Band"

        async with db_session.begin():
            international_code = satellite_test_date[1]["international_code"]
            zones: Optional[List[CoverageZoneInDB]] = (
                await repo.get_zone_list_by_satellite_id(
                    Object_str_ID(id=international_code)
                )
            )
            assert len(zones) == 0

        async with db_session.begin():
            international_code = "dkljfejjreifj"
            zones: Optional[List[CoverageZoneInDB]] = (
                await repo.get_zone_list_by_satellite_id(
                    Object_str_ID(id=international_code)
                )
            )
            assert zones is None


class TestZoneRelationship:
    @pytest.mark.asyncio
    async def test_add_region(self, db_session):
        repo = CoverageZoneRepository(db_session)
        repo_region = RegionRepository(db_session)
        async with db_session.begin():
            assert len(await repo_region.get_models(PaginationBase())) == 3
            region_1 = RegionBase(name_region="Russia")
            zone_1_id = Object_str_ID(id="2021-12bd-23730")
            assert await repo.add_region(region_1, zone_1_id)
            reg_list = await repo.get_region_list(zone_1_id)
            assert len(await repo.get_region_list(zone_1_id)) == 1
            assert reg_list[0].name_region == "Russia"
            region_2 = RegionBase(name_region="Nigeria")
            assert await repo.add_region(region_2, zone_1_id)
            assert len(await repo.get_region_list(zone_1_id)) == 2
            assert len(await repo_region.get_models(PaginationBase())) == 4
            assert await repo.delete_region(region_1, zone_1_id)
            reg_list = await repo.get_region_list(zone_1_id)
            assert len(await repo.get_region_list(zone_1_id)) == 1
            assert reg_list[0].name_region == "Nigeria"
            assert await repo.delete_region(region_2, zone_1_id)
            assert len(await repo.get_region_list(zone_1_id)) == 0
            nigeria_id = Object_ID(
                id=(
                    await repo_region.get_region_by_name(
                        RegionBase(name_region="Nigeria")
                    )
                ).id
            )
            await repo_region.delete_model(nigeria_id)

    async def test_invalid_delete_region(self, db_session):
        repo = CoverageZoneRepository(db_session)
        region_1 = RegionBase(name_region="Russia")
        zone_1_id = Object_str_ID(id="20qqe-12bd-23730")
        async with db_session.begin():
            assert not await repo.delete_region(region_1, zone_1_id)
        async with db_session.begin():
            zone_1_id = Object_str_ID(id="2021-12bd-23730")
            region_1 = RegionBase(name_region="kussia")
            assert not await repo.delete_region(region_1, zone_1_id)

    @pytest.mark.asyncio
    async def test_add_subregion(self, db_session):
        repo = CoverageZoneRepository(db_session)
        repo_subregion = SubregionRepository(db_session)
        zone_2_id = Object_str_ID(id="2001-1234-24670")
        async with db_session.begin():
            assert len(await repo_subregion.get_models(PaginationBase())) == 4
            zone_2: Optional[SubregionInDB] = await repo.get_as_model(zone_2_id)
            assert zone_2 is not None
            assert len(await repo.get_region_list(zone_2_id)) == 0
            subregion_test_1 = SubregionCreate(
                name_subregion="Москва", id=None, id_region=2
            )
            subregion_test_2 = SubregionCreate(
                name_subregion="Питер", id=None, id_region=2
            )
            assert await repo.add_subregion(subregion_test_1, zone_2_id)
            assert len(await repo.get_region_list(zone_2_id)) == 1
            assert await repo.add_subregion(subregion_test_2, zone_2_id)
            assert len(await repo.get_region_list(zone_2_id)) == 1
            subregion_1: Optional[SubregionInDB] = (
                await repo_subregion.get_subregion_by_name(
                    SubregionBase(name_subregion="Москва")
                )
            )
            assert subregion_1 is not None
            assert subregion_1.id_region == 2
            subregion_2: Optional[SubregionInDB] = (
                await repo_subregion.get_subregion_by_name(
                    SubregionBase(name_subregion="Питер")
                )
            )
            assert subregion_2 is not None
            assert subregion_2.id_region == 2
            region_list: List[ZoneRegionDetails] = await repo.get_region_list(zone_2_id)
            assert len(region_list) == 1
            assert len(region_list[0].subregion_list) == 2
            subregion_base = SubregionBase(name_subregion="Москва")
            assert await repo.delete_subregion(subregion_base, zone_2_id)
            region_list: List[ZoneRegionDetails] = await repo.get_region_list(zone_2_id)
            assert len(region_list) == 1
            assert len(region_list[0].subregion_list) == 1
            subregion_base = SubregionBase(name_subregion="Питер")
            assert await repo.delete_subregion(subregion_base, zone_2_id)
            region_list: List[ZoneRegionDetails] = await repo.get_region_list(zone_2_id)
            assert len(region_list) == 0

    @pytest.mark.asyncio
    async def test_add_invalid(self, db_session):
        repo = CoverageZoneRepository(db_session)
        repo_subregion = SubregionRepository(db_session)
        repo_region = RegionRepository(db_session)
        zone_2_id = Object_str_ID(id="2001-1234-24670")
        async with db_session.begin():
            assert len(await repo_region.get_models(PaginationBase())) == 3
            region_1 = RegionBase(name_region="England")
            assert len(await repo.get_region_list(zone_2_id)) == 0
            assert await repo.add_region(region_1, zone_2_id)
            assert len(await repo_region.get_models(PaginationBase())) == 4
            assert len(await repo.get_region_list(zone_2_id)) == 1
            assert not await repo.add_region(region_1, zone_2_id)
            assert len(await repo_region.get_models(PaginationBase())) == 4
            assert len(await repo.get_region_list(zone_2_id)) == 1
        async with db_session.begin():
            assert len(await repo_subregion.get_models(PaginationBase())) == 6
            subregion_test_1 = SubregionCreate(
                name_subregion="Урюпинск", id=None, id_region=7
            )
            assert not await repo.add_subregion(subregion_test_1, zone_2_id)
            assert len((await repo.get_region_list(zone_2_id))[0].subregion_list) == 0
            assert len(await repo_subregion.get_models(PaginationBase())) == 6
            subregion_test_1 = SubregionCreate(
                name_subregion="Урюпинск", id=None, id_region=5
            )
            assert await repo.add_subregion(subregion_test_1, zone_2_id)
            assert len(await repo_region.get_models(PaginationBase())) == 4
            assert len(await repo_subregion.get_models(PaginationBase())) == 7
        async with db_session.begin():
            assert len(await repo_region.get_models(PaginationBase())) == 4
            assert not await repo_region.delete_model(Object_ID(id=5))
        async with db_session.begin():
            assert len(await repo_region.get_models(PaginationBase())) == 4
        async with db_session.begin():
            assert len(await repo_subregion.get_models(PaginationBase())) == 7
            assert await repo_subregion.delete_model(Object_ID(id=7))
        async with db_session.begin():
            assert len(await repo_subregion.get_models(PaginationBase())) == 6
        async with db_session.begin():
            assert len(await repo.get_region_list(zone_2_id)) == 1
            assert await repo.delete_region(region_1, zone_2_id)
            assert len(await repo.get_region_list(zone_2_id)) == 0
        async with db_session.begin():
            assert not await repo_subregion.delete_model(Object_ID(id=7))
        async with db_session.begin():
            assert len(await repo_subregion.get_models(PaginationBase())) == 6
            assert len(await repo_region.get_models(PaginationBase())) == 4
            assert await repo_region.delete_model(Object_ID(id=5))
            assert len(await repo_region.get_models(PaginationBase())) == 3


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_1(self, db_session):
        repo = CoverageZoneRepository(db_session)
        data_zone = test_create_data[0]
        zone_id = Object_str_ID(id=data_zone.get("id"))
        async with db_session.begin():
            zone_data_in_db: Optional[CoverageZoneInDB] = await repo.get_as_model(
                zone_id
            )
            async with await repo.s3._get_client() as client:
                response = await client.get_object(
                    Bucket=repo.s3.bucket_name, Key=f"zone/{zone_data_in_db.id}.jpg"
                )
                s3_image_data = await response["Body"].read()
                assert (
                    await get_data_image(test_create_data[0].get("image"))
                    == s3_image_data
                )
            assert zone_data_in_db.id == test_create_data[0].get("id")
            assert zone_data_in_db.transmitter_type == test_create_data[0].get(
                "transmitter_type"
            )
            assert zone_data_in_db.satellite_code == satellite_test_date[0].get(
                "international_code"
            )
            update_data = {
                "transmitter_type": "KUKU-Band",
                "satellite_code": satellite_test_date[1].get("international_code"),
            }
            assert await repo.update_model(zone_id, CoverageZoneUpdate(**update_data))
        async with db_session.begin():
            zone_data_in_db: Optional[CoverageZoneInDB] = await repo.get_as_model(
                zone_id
            )
            assert zone_data_in_db.id == test_create_data[0].get("id")
            assert zone_data_in_db.transmitter_type == "KUKU-Band"
            assert zone_data_in_db.satellite_code == satellite_test_date[1].get(
                "international_code"
            )

        async with db_session.begin():
            update_data = {"image_data": await get_data_image("tests/test/test3.jpg")}
            assert await repo.update_model(zone_id, CoverageZoneUpdate(**update_data))

        async with db_session.begin():
            zone_data_in_db: Optional[CoverageZoneInDB] = await repo.get_as_model(
                zone_id
            )
            assert zone_data_in_db.id == test_create_data[0].get("id")
            assert zone_data_in_db.transmitter_type == "KUKU-Band"
            assert zone_data_in_db.satellite_code == satellite_test_date[1].get(
                "international_code"
            )
            async with await repo.s3._get_client() as client:
                response = await client.get_object(
                    Bucket=repo.s3.bucket_name, Key=f"zone/{zone_data_in_db.id}.jpg"
                )
                s3_image_data = await response["Body"].read()
                assert await get_data_image("tests/test/test3.jpg") == s3_image_data

    @pytest.mark.asyncio
    async def test_update_2(self, db_session):
        repo = CoverageZoneRepository(db_session)
        zone_data = test_create_data[0]
        zone_id = Object_str_ID(id=zone_data.get("id"))
        async with db_session.begin():
            update_data = {
                "image_data": await get_data_image(zone_data["image"]),
                "transmitter_type": test_create_data[0].get("transmitter_type"),
                "satellite_code": satellite_test_date[0].get("international_code"),
            }
            await repo.update_model(zone_id, CoverageZoneUpdate(**update_data))

        async with db_session.begin():
            zone_data_in_db: Optional[CoverageZoneInDB] = await repo.get_as_model(
                zone_id
            )
            async with await repo.s3._get_client() as client:
                response = await client.get_object(
                    Bucket=repo.s3.bucket_name, Key=f"zone/{zone_data_in_db.id}.jpg"
                )
                s3_image_data = await response["Body"].read()
                assert (
                    await get_data_image(test_create_data[0].get("image"))
                    == s3_image_data
                )
            assert zone_data_in_db.id == test_create_data[0].get("id")
            assert zone_data_in_db.transmitter_type == test_create_data[0].get(
                "transmitter_type"
            )
            assert zone_data_in_db.satellite_code == satellite_test_date[0].get(
                "international_code"
            )


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_1(self, db_session):
        repo = CoverageZoneRepository(db_session)
        id_list = [
            Object_str_ID(id="2021-12bd-23730"),
            Object_str_ID(id="2001-1234-24670"),
        ]
        numbers_in_db = 2
        async with db_session.begin():
            for id_obj in id_list:
                zone_list = await repo.get_models(PaginationBase())
                assert len(zone_list) == numbers_in_db
                await repo.delete_model(id_obj)
                zone_list = await repo.get_models(PaginationBase())
                numbers_in_db -= 1
                assert len(zone_list) == numbers_in_db


@pytest.mark.asyncio
async def test_delete_subregions(db_session):
    async with db_session.begin():
        repo = SubregionRepository(db_session)
        subregion_list: List = await repo.get_models(PaginationBase())
        for subregion in subregion_list:
            object_id = Object_ID(id=subregion.id)
            assert await repo.delete_model(object_id)


@pytest.mark.asyncio
async def test_delete_regions(db_session):
    async with db_session.begin():
        repo = RegionRepository(db_session)
        region_list: List = await repo.get_models(PaginationBase())
        for region in region_list:
            object_id = Object_ID(id=region.id)
            assert await repo.delete_model(object_id)


@pytest.mark.asyncio
async def test_numbers_region(db_session):
    async with db_session.begin():
        region_repo = RegionRepository(db_session)
        subregion_repo = SubregionRepository(db_session)
        assert len(await region_repo.get_models(PaginationBase())) == 0
        assert len(await subregion_repo.get_models(PaginationBase())) == 0


@pytest.mark.asyncio
async def test_delete_satellite(db_session):
    async with db_session.begin():
        satellite_repo = SatelliteRepository(db_session)
        satellite_list = await satellite_repo.get_models(PaginationBase())
        assert len(satellite_list) != 0
        for satellite in satellite_list:
            assert await satellite_repo.delete_model(
                Object_str_ID(id=satellite.international_code)
            )
        assert len(await satellite_repo.get_models(PaginationBase())) == 0


@pytest.mark.asyncio
async def test_delete_country(db_session):
    async with db_session.begin():
        country_repo = CountryRepository(db_session)
        country_list = await country_repo.get_models(PaginationBase())
        assert len(country_list) != 0
        for country in country_list:
            assert await country_repo.delete_model(Object_ID(id=country.id))
        assert len(await country_repo.get_models(PaginationBase())) == 0
