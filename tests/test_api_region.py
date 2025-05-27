import pytest
from app.schemas import RegionInDB, SubregionInDB
from tests.test_data import region_test, test_subregion, country_test_data
from fastapi import status


@pytest.mark.asyncio
async def test_check_count_region_1(async_client):
    assert len((await async_client.get("/region/regions/")).json()) == 0


@pytest.mark.asyncio
async def test_check_count_subregion_1(async_client):
    assert len((await async_client.get("/region/subregions/")).json()) == 0


@pytest.mark.usefixtures("async_client")
class TestRegionAPI:

    @pytest.fixture(autouse=True)
    def _setup_client(self, async_client):
        self.client = async_client

    @pytest.mark.asyncio
    async def test_get_region_by_id_not_found(self):
        response = await self.client.get("/region/id/999999")
        assert response.status_code == 404

    @pytest.mark.asyncio
    async def test_get_subregion_by_id_not_found(self):
        response = await self.client.get("/region/subregion/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Subregion not found"

    @pytest.mark.asyncio
    async def test_get_region_by_name_not_found(self):
        response = await self.client.get("/region/name/nonexistent_region")
        assert response.status_code == 404
        assert response.json()["detail"] == "Region not found"

    @pytest.mark.asyncio
    async def test_get_subregion_by_name_not_found(self):
        response = await self.client.get("/region/subregion/name/nonexistent_subregion")
        assert response.status_code == 404

    @pytest.mark.asyncio
    @pytest.mark.parametrize("region_data", region_test)
    async def test_create_and_get_region(self, region_data):
        response = await self.client.post(f"/region/", json=region_data)
        assert response.status_code == 200

        get_response = await self.client.get(
            f"/region/name/{region_data.get("name_region")}"
        )
        assert get_response.status_code == 200
        region = RegionInDB(**get_response.json())
        assert region.name_region == region_data["name_region"]
        region_id = region.id
        get_response = await self.client.get(f"/region/{region_id}")
        assert get_response.status_code == 200
        region = RegionInDB(**get_response.json())
        assert region.name_region == region_data["name_region"]
        assert region.id == region_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize("subregion_data", test_subregion)
    async def test_create_and_get_subregion(self, subregion_data):
        get_response = await self.client.get(
            f"/region/name/{subregion_data.get("name_region")}"
        )
        subregion_data["id_region"] = get_response.json().get("id")
        response = await self.client.post(f"/region/subregion", json=subregion_data)
        assert response.status_code == 200

        get_response = await self.client.get(
            f"/region/subregion/name/{subregion_data.get("name_subregion")}"
        )
        assert get_response.status_code == 200
        subregion = SubregionInDB(**get_response.json())
        assert subregion.name_subregion == subregion_data["name_subregion"]
        subregion_id = subregion.id
        get_response = await self.client.get(f"/region/subregion/{subregion_id}")
        assert get_response.status_code == 200
        subregion = SubregionInDB(**get_response.json())
        assert subregion.name_subregion == subregion_data["name_subregion"]
        assert subregion.id == subregion_id

    @pytest.mark.asyncio
    async def test_delete_region_invalid(self):
        # Мы не можем удалить регион так как у него есть субрегионы
        region = (await self.client.get("/region/name/Russia")).json()
        assert region
        response = await self.client.delete(f"/region/{region.get("id")}")
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_delete_subregion(self):
        subregions = (await self.client.get("/region/subregions/")).json()
        assert len(subregions) != 0
        for subregion in subregions:
            subregion_id = subregion.get("id")
            print(subregion_id)
            response = await self.client.delete(f"/region/subregion/{subregion_id}")
            assert response.status_code == 204

        regions = (await self.client.get("/region/subregions/")).json()
        assert len(regions) == 0

    @pytest.mark.asyncio
    async def test_delete_region(self):
        regions = (await self.client.get("/region/regions/")).json()
        assert len(regions) != 0
        for region in regions:
            response = await self.client.delete(f"/region/{region.get("id")}")
            assert response.status_code == 204

        regions = (await self.client.get("/region/regions/")).json()
        assert len(regions) == 0
