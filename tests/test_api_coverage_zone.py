import pytest
from tests.test_data import country_test_data, satellite_test_date, test_create_data
from fastapi import status
from copy import copy


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
