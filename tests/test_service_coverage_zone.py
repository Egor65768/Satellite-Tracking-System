import pytest
from app.schemas import (
    CountryCreate,
    SatelliteCreate,
    PaginationBase,
    CoverageZoneCreate,
    RegionBase,
    SubregionCreate,
    SubregionBase,
    CoverageZoneUpdate,
)
from app.service import (
    create_country_service,
    create_satellite_service,
    create_coverage_zone_service,
    create_region_service,
)
from app.s3_service import S3Service

from tests.test_data import country_test_data, satellite_test_date, test_create_data
import aiofiles
from typing import Optional


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
@pytest.mark.parametrize("country_data", country_test_data)
async def test_create_country(db_session, country_data):
    service = create_country_service(db_session)
    async with db_session.begin():
        country = await service.create_country(CountryCreate(**country_data))
        assert country is not None


@pytest.mark.asyncio
@pytest.mark.parametrize("satellite_data", satellite_test_date)
async def test_create_satellite(db_session, satellite_data):
    service = create_satellite_service(db_session)
    async with db_session.begin():
        satellite = await service.create_satellite_base(
            SatelliteCreate(**satellite_data)
        )
        assert satellite is not None


class TestCreate:
    @pytest.mark.asyncio
    async def test_check_count_coverage_zone_1(self, db_session):
        service = create_coverage_zone_service(
            db_session,
        )
        async with db_session.begin():
            assert len(await service.get_coverage_zones(PaginationBase())) == 0
            assert await service.get_count_coverage_zone_in_db() == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("coverage_zone_data", test_create_data)
    async def test_create_coverage_zone(self, db_session, coverage_zone_data):
        service = create_coverage_zone_service(db_session)
        async with db_session.begin():
            coverage_zone_data["satellite_code"] = satellite_test_date[0].get(
                "international_code"
            )
            coverage_zone_create = CoverageZoneCreate(
                id=coverage_zone_data.get("id"),
                image_data=await get_data_image(coverage_zone_data.get("image")),
                satellite_code=satellite_test_date[0].get("international_code"),
                transmitter_type=coverage_zone_data.get("transmitter_type"),
            )
            assert await service.create_coverage_zone(coverage_zone_create)
        async with db_session.begin():
            assert await service.get_by_id(coverage_zone_data.get("id"))

    @pytest.mark.asyncio
    async def test_check_count_coverage_zone_2(self, db_session):
        service = create_coverage_zone_service(db_session)
        async with db_session.begin():
            assert len(await service.get_coverage_zones(PaginationBase())) == len(
                test_create_data
            )
            assert await service.get_count_coverage_zone_in_db() == len(
                test_create_data
            )

    @pytest.mark.asyncio
    async def test_add_region(self, db_session):
        service = create_coverage_zone_service(db_session)
        region_1 = RegionBase(name_region="USA")
        region_2 = RegionBase(name_region="New Zeland")
        region_3 = RegionBase(name_region="Russia")
        coverage_zone_data = test_create_data[0]
        coverage_zone_id = coverage_zone_data.get("id")
        async with db_session.begin():
            assert await service.add_region_by_coverage_zone_id(
                coverage_zone_id, region_1
            )
        async with db_session.begin():
            assert await service.add_region_by_coverage_zone_id(
                coverage_zone_id, region_2
            )
        async with db_session.begin():
            assert await service.add_region_by_coverage_zone_id(
                coverage_zone_id, region_3
            )

        async with db_session.begin():
            region_list = await service.get_region_list_by_id(coverage_zone_id)
            assert len(region_list) == 3
            for region in region_list:
                assert region.name_region in ["New Zeland", "USA", "Russia"]
                assert len(region.subregion_list) == 0

    async def test_add_subregion(self, db_session):
        service = create_coverage_zone_service(db_session)
        coverage_zone_data = test_create_data[1]
        coverage_zone_id = coverage_zone_data.get("id")
        region_service = create_region_service(db_session)
        async with db_session.begin():
            subregion_data = [
                {
                    "name_subregion": "UTA",
                    "id_region": (await region_service.get_region_by_name("USA")).id,
                },
                {
                    "name_subregion": "Wellington",
                    "id_region": (
                        await region_service.get_region_by_name("New Zeland")
                    ).id,
                },
                {
                    "name_subregion": "California",
                    "id_region": (await region_service.get_region_by_name("USA")).id,
                },
                {
                    "name_subregion": "Auckland",
                    "id_region": (
                        await region_service.get_region_by_name("New Zeland")
                    ).id,
                },
                {
                    "name_subregion": "Moscow",
                    "id_region": (await region_service.get_region_by_name("Russia")).id,
                },
            ]
        for subregion in subregion_data:
            assert await service.add_subregion_by_coverage_zone_id(
                coverage_zone_id, SubregionCreate(**subregion)
            )

        async with db_session.begin():
            region_list = await service.get_region_list_by_id(coverage_zone_id)
            for region in region_list:
                assert region.name_region in ["USA", "New Zeland", "Russia"]
                if region.name_region == "New Zeland":
                    assert len(region.subregion_list) == 2
                    assert region.subregion_list[0].name_subregion in [
                        "Wellington",
                        "Auckland",
                    ]
                elif region.name_region == "USA":
                    for subregion in region.subregion_list:
                        assert subregion.name_subregion in ["UTA", "California"]
                elif region.name_region == "Russia":
                    assert len(region.subregion_list) == 1
                    assert region.subregion_list[0].name_subregion == "Moscow"

    async def test_add_invalid_region(self, db_session):
        service = create_coverage_zone_service(db_session)
        async with db_session.begin():
            assert not await service.add_region_by_coverage_zone_id(
                "ajdkfehwugf", RegionBase(name_region="Ukrain")
            )
        async with db_session.begin():
            region_1 = RegionBase(name_region="USA")
            coverage_zone_data = test_create_data[0]
            coverage_zone_id = coverage_zone_data.get("id")
            assert await service.add_region_by_coverage_zone_id(
                coverage_zone_id, region_1
            )


class TestGet:
    @pytest.mark.asyncio
    async def test_get_coverage_zones_by_satellite(self, db_session):
        service = create_coverage_zone_service(db_session)
        async with db_session.begin():
            satellite_international_code = satellite_test_date[0].get(
                "international_code"
            )
            zones = await service.get_coverage_zones_by_satellite_international_code(
                satellite_international_code
            )
            assert len(zones) == 2
            for zone in zones:
                assert zone.id
                assert zone.transmitter_type
                assert zone.satellite_code
                assert zone.image_data

    @pytest.mark.asyncio
    async def test_get_coverage_zones_by_satellite_invalid(self, db_session):
        service = create_coverage_zone_service(db_session)
        async with db_session.begin():
            zones = await service.get_coverage_zones_by_satellite_international_code(
                "AAAA"
            )
            assert zones is None

    @pytest.mark.asyncio
    async def test_get_region_list_by_id(self, db_session):
        service = create_coverage_zone_service(db_session)
        coverage_zone_id = test_create_data[0].get("id")
        async with db_session.begin():
            regions = await service.get_region_list_by_id(coverage_zone_id)
            assert len(regions) == 3
            for region in regions:
                assert region.name_region in ["USA", "New Zeland", "Russia"]
                if region.name_region == "New Zeland":
                    for subregion in region.subregion_list:
                        assert subregion.name_subregion in ["Wellington", "Auckland"]
                elif region.name_region == "USA":
                    for subregion in region.subregion_list:
                        assert subregion.name_subregion in ["UTA", "California"]
                # elif region.name_region == "Russia":
                #     assert region.subregion_list[0].name_subregion == "Moscow"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("coverage_zone_data", test_create_data)
    async def test_get_satellite(self, db_session, coverage_zone_data):
        service = create_coverage_zone_service(db_session)
        async with db_session.begin():
            satellite = await service.get_satellite(coverage_zone_data.get("id"))
            assert satellite.international_code == satellite_test_date[0].get(
                "international_code"
            )

    @pytest.mark.asyncio
    async def test_get_satellite_invalid(self, db_session):
        service = create_coverage_zone_service(db_session)
        async with db_session.begin():
            assert await service.get_satellite("akakaksssd") is None

    @pytest.mark.asyncio
    async def test_get_coverage_zones(self, db_session):
        service = create_coverage_zone_service(db_session)
        async with db_session.begin():
            zones = await service.get_coverage_zones(PaginationBase())
            for zone in zones:
                assert zone.id in ["2021-12bd-23730", "2001-1234-24670"]
            assert await service.get_count_coverage_zone_in_db() == len(zones)


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_coverage_zone_1(self, db_session):
        coverage_zone_id = test_create_data[0].get("id")
        service = create_coverage_zone_service(db_session)
        s3_service = S3Service()
        async with db_session.begin():
            zone = await service.get_by_id(coverage_zone_id)
            assert zone.transmitter_type == test_create_data[0].get("transmitter_type")
            assert zone.satellite_code == satellite_test_date[0].get(
                "international_code"
            )
            assert zone.id == test_create_data[0].get("id")
            local_data = await get_data_image(test_create_data[0].get("image"))
            assert local_data is not None
            s3_data = await s3_service.get_file(coverage_zone_id)
            assert s3_data is not None
            assert s3_data == local_data
        update_data_dict = {
            "transmitter_type": "TEST_TEST",
            "satellite_code": satellite_test_date[1].get("international_code"),
        }
        async with db_session.begin():
            assert await service.update_coverage_zone(
                coverage_zone_id, CoverageZoneUpdate(**update_data_dict)
            )
        async with db_session.begin():
            zone = await service.get_by_id(coverage_zone_id)
            assert zone.transmitter_type == "TEST_TEST"
            assert zone.satellite_code == satellite_test_date[1].get(
                "international_code"
            )
            assert zone.id == test_create_data[0].get("id")

        update_data_dict = {
            "image_data": await get_data_image("tests/test/test3.jpg"),
        }
        async with db_session.begin():
            assert await service.update_coverage_zone(
                coverage_zone_id, CoverageZoneUpdate(**update_data_dict)
            )

        local_data = await get_data_image("tests/test/test3.jpg")
        assert local_data is not None
        s3_data = await s3_service.get_file(coverage_zone_id)
        assert s3_data is not None
        assert s3_data == local_data

    @pytest.mark.asyncio
    async def test_update_coverage_zone_2(self, db_session):
        coverage_zone_id = test_create_data[0].get("id")
        service = create_coverage_zone_service(db_session)
        s3_service = S3Service()
        async with db_session.begin():
            zone = await service.get_by_id(coverage_zone_id)
            assert zone.transmitter_type == "TEST_TEST"
            assert zone.satellite_code == satellite_test_date[1].get(
                "international_code"
            )
            assert zone.id == test_create_data[0].get("id")
            local_data = await get_data_image("tests/test/test3.jpg")
            assert local_data is not None
            s3_data = await s3_service.get_file(coverage_zone_id)
            assert s3_data is not None
            assert s3_data == local_data

        update_data_dict = {
            "transmitter_type": test_create_data[0].get("transmitter_type"),
            "satellite_code": satellite_test_date[0].get("international_code"),
            "image_data": await get_data_image("tests/test/test1.jpg"),
        }
        async with db_session.begin():
            assert await service.update_coverage_zone(
                coverage_zone_id, CoverageZoneUpdate(**update_data_dict)
            )

        async with db_session.begin():
            zone = await service.get_by_id(coverage_zone_id)
            assert zone.transmitter_type == test_create_data[0].get("transmitter_type")
            assert zone.satellite_code == satellite_test_date[0].get(
                "international_code"
            )
            assert zone.id == test_create_data[0].get("id")
            local_data = await get_data_image("tests/test/test1.jpg")
            assert local_data is not None
            s3_data = await s3_service.get_file(coverage_zone_id)
            assert s3_data is not None
            assert s3_data == local_data


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete_region_by_coverage_zone_id(self, db_session):
        coverage_zone_id = test_create_data[1].get("id")
        service = create_coverage_zone_service(db_session)
        async with db_session.begin():
            assert await service.delete_region_by_coverage_zone(
                coverage_zone_id, RegionBase(name_region="New Zeland")
            )
        async with db_session.begin():
            assert not await service.delete_region_by_coverage_zone(
                coverage_zone_id, RegionBase(name_region="England")
            )
        async with db_session.begin():
            regions = await service.get_region_list_by_id(coverage_zone_id)
        for region in regions:
            assert region.name_region in ["USA", "Russia"]

    @pytest.mark.asyncio
    async def test_delete_subregion_by_coverage_zone_id(self, db_session):
        coverage_zone_id = test_create_data[1].get("id")
        service = create_coverage_zone_service(db_session)
        async with db_session.begin():
            assert not await service.delete_subregion_by_coverage_zone(
                coverage_zone_id, SubregionBase(name_subregion="Wellington")
            )
        async with db_session.begin():
            assert not await service.delete_subregion_by_coverage_zone(
                coverage_zone_id, SubregionBase(name_subregion="Wellington")
            )
        async with db_session.begin():
            assert await service.delete_subregion_by_coverage_zone(
                coverage_zone_id, SubregionBase(name_subregion="UTA")
            )
        async with db_session.begin():
            regions = await service.get_region_list_by_id(coverage_zone_id)
        for region in regions:
            assert region.name_region in ["USA", "Russia"]
            if region.name_region == "USA":
                assert len(region.subregion_list) == 1
                assert region.subregion_list[0].name_subregion == "California"

    @pytest.mark.asyncio
    async def test_delete_coverage_zone(self, db_session):
        service = create_coverage_zone_service(db_session)
        async with db_session.begin():
            coverage_zone_list = await service.get_coverage_zones(PaginationBase())
        for zone in coverage_zone_list:
            assert await service.delete_coverage_zone(zone.id)

    async def test_check_count_coverage_zone_3(self, db_session):
        service = create_coverage_zone_service(
            db_session,
        )
        async with db_session.begin():
            assert len(await service.get_coverage_zones(PaginationBase())) == 0
            assert await service.get_count_coverage_zone_in_db() == 0


@pytest.mark.asyncio
async def test_delete_satellite(db_session):
    service = create_satellite_service(db_session)
    async with db_session.begin():
        sat_list = await service.get_satellites(PaginationBase(limit=100))
    for sat in sat_list:
        async with db_session.begin():
            assert await service.delete_satellite(sat.international_code)


@pytest.mark.asyncio
@pytest.mark.parametrize("country_data", country_test_data)
async def test_delete_country(db_session, country_data):
    service = create_country_service(db_session)
    async with db_session.begin():
        country_abbreviation = country_data.get("abbreviation")
        country = await service.get_by_abbreviation(country_abbreviation)
        assert country is not None
        assert await service.delete_country(country.id)


@pytest.mark.asyncio
async def test_delete_region(db_session):
    service = create_region_service(db_session)
    async with db_session.begin():
        regions = await service.get_regions(PaginationBase())
    for region in regions:
        await service.delete_region(region.id)


@pytest.mark.asyncio
async def test_check_count_region(db_session):
    service = create_region_service(db_session)
    async with db_session.begin():
        assert len(await service.get_regions(PaginationBase())) == 0
