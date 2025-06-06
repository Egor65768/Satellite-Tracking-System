import pytest
from fastapi import status
from copy import copy
from tests.test_data import (
    country_test_data,
    satellite_test_date,
    test_create_data,
    region_test,
    region_list,
)
from tests.test_service_coverage_zone import get_data_image


@pytest.mark.asyncio
async def test_check_count_country_1(async_client):
    assert len((await async_client.get("/country/list/")).json()) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("country_data", country_test_data)
async def test_create_country(country_data, async_client):
    create_response = await async_client.post("/country/", json=country_data)
    assert create_response.status_code == 200


@pytest.mark.asyncio
async def test_check_count_country_2(async_client):
    assert len((await async_client.get("/country/list/")).json()) == 3


@pytest.mark.asyncio
async def test_check_count_satellite_1(async_client):
    assert len((await async_client.get("/satellite/list/")).json()) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("satellite_date", satellite_test_date)
async def test_create_satellite(satellite_date, async_client):
    satellite_date_test = copy(satellite_date)
    satellite_date_test["launch_date"] = satellite_date.get("launch_date").isoformat()
    create_response = await async_client.post("/satellite/", json=satellite_date_test)
    assert create_response.status_code == 200


@pytest.mark.asyncio
async def test_check_count_satellite_2(async_client):
    assert len((await async_client.get("/satellite/list/")).json()) == len(
        satellite_test_date
    )


@pytest.mark.usefixtures("async_client")
class TestCoverageZoneAPI:

    @pytest.fixture(autouse=True)
    def _setup_client(self, async_client):
        self.client = async_client

    @pytest.mark.asyncio
    async def test_get_zone_by_id_not_found(self):
        response = await self.client.get("/coverage_zone/id/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_list_coverage_zone_by_satellite_international_code_not_found(
        self,
    ):
        response = await self.client.get(
            "/coverage_zone/satellite/satellite_international_code/1234"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_list_coverage_zone_by_satellite_international_code_found(self):
        sat_int_code = satellite_test_date[0].get("international_code")
        response = await self.client.get(
            f"/coverage_zone/satellite/satellite_international_code/{sat_int_code}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

    @pytest.mark.asyncio
    async def test_get_regions_by_coverage_zone_id_not_found(self):
        response = await self.client.get("/coverage_zone/regions/1234554")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_satellite_by_coverage_zone_id_not_found(self):
        response = await self.client.get(
            "/coverage_zone/satellite/coverage_zone_id/99ddad99"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    @pytest.mark.parametrize("coverage_zone_data", test_create_data)
    async def test_create_coverage_zone(self, coverage_zone_data):
        coverage_zone_data_request = {
            "coverage_zone_id": coverage_zone_data.get("id"),
            "transmitter_type": coverage_zone_data.get("transmitter_type"),
            "satellite_code": satellite_test_date[0].get("international_code"),
        }
        files = {
            "image": (
                coverage_zone_data.get("image"),
                await get_data_image(coverage_zone_data.get("image")),
                "image/jpeg",
            )
        }
        response = await self.client.post(
            "/coverage_zone/", data=coverage_zone_data_request, files=files
        )
        assert response.status_code == status.HTTP_200_OK

        response = await self.client.post(
            "/coverage_zone/", data=coverage_zone_data_request, files=files
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_add_region_by_coverage_zone(self):

        coverage_zone_id = test_create_data[0].get("id")

        response = await self.client.post(
            f"/coverage_zone/region/invalid_id", json=region_list[0]
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0
        for region in region_list:
            response = await self.client.post(
                f"/coverage_zone/region/{coverage_zone_id}", json=region
            )
            assert response.status_code == status.HTTP_204_NO_CONTENT
        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_list)
        for region in response.json():
            assert region.get("name_region") in [
                "region_1",
                "region_2",
                "region_3",
                "region_4",
                "region_5",
            ]

    @pytest.mark.asyncio
    async def test_add_regions_list_by_coverage_zone(self):
        coverage_zone_id = test_create_data[1].get("id")

        response = await self.client.post(
            f"/coverage_zone/regions/invalid_id", json=region_test
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0

        response = await self.client.post(
            f"/coverage_zone/regions/{coverage_zone_id}", json=region_test
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT
        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_test)

    @pytest.mark.asyncio
    async def test_add_region_2(self):
        coverage_zone_id_1 = test_create_data[0].get("id")
        coverage_zone_id_2 = test_create_data[1].get("id")
        for region in region_list:
            response = await self.client.post(
                f"/coverage_zone/region/{coverage_zone_id_1}", json=region
            )
            assert response.status_code == status.HTTP_204_NO_CONTENT

            response = await self.client.post(
                f"/coverage_zone/region/{coverage_zone_id_2}", json=region
            )
            assert response.status_code == status.HTTP_204_NO_CONTENT
        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id_1}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_list)

        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id_2}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_list) + len(region_test)

        regions = (
            await self.client.get("/region/regions/", params={"limit": 100})
        ).json()
        assert len(regions) == len(region_list) + len(region_test)

    @pytest.mark.asyncio
    async def test_delete_coverage_zone(self):
        response = await self.client.get(
            "/coverage_zone/coverage_zones/count/",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"number_of_coverage_zones": 2}

        response = await self.client.get(
            "/coverage_zone/coverage_zones/",
        )
        assert response.status_code == status.HTTP_200_OK
        zones = response.json()
        for zone in zones:
            zone_id = zone.get("id")
            response = await self.client.delete(f"/coverage_zone/{zone_id}")
            assert response.status_code == status.HTTP_204_NO_CONTENT

        response = await self.client.get(
            "/coverage_zone/coverage_zones/count/",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"number_of_coverage_zones": 0}


@pytest.mark.asyncio
async def test_delete_satellite(async_client):
    create_response = await async_client.get("/satellite/list/")
    assert create_response.status_code == 200
    satellite_list = create_response.json()
    assert len(satellite_list) == len(satellite_test_date)
    for satellite in satellite_list:
        satellite_id = satellite["international_code"]
        delete_response = await async_client.delete(f"/satellite/{satellite_id}")
        assert delete_response.status_code == 204
    create_response = await async_client.get("/satellite/list/")
    assert create_response.status_code == 200
    country_list = create_response.json()
    assert len(country_list) == 0


@pytest.mark.asyncio
async def test_delete_country(async_client):
    create_response = await async_client.get("/country/list/")
    assert create_response.status_code == 200
    country_list = create_response.json()
    assert len(country_list) == 3
    for country in country_list:
        country_id = country["id"]
        delete_response = await async_client.delete(f"/country/{country_id}")
        assert delete_response.status_code == 204
    create_response = await async_client.get("/country/list/")
    assert create_response.status_code == 200
    country_list = create_response.json()
    assert len(country_list) == 0


@pytest.mark.asyncio
async def test_delete_region(async_client):
    regions = (await async_client.get("/region/regions/", params={"limit": 100})).json()
    assert len(regions) != 0
    for region in regions:
        print(region.get("name_region"))
        response = await async_client.delete(f"/region/{region.get("id")}")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    regions = (await async_client.get("/region/regions/")).json()
    assert len(regions) == 0
