import pytest
from app.schemas import RegionInDB, SubregionInDB
from tests.test_data import region_test, test_subregion
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
        response = await self.client.get("/region/id/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_subregion_by_id_not_found(self):
        response = await self.client.get("/region/subregion/9999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Subregion not found"

    @pytest.mark.asyncio
    async def test_get_region_by_name_not_found(self):
        response = await self.client.get("/region/name/nonexistent_region")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json()["detail"] == "Region not found"

    @pytest.mark.asyncio
    async def test_get_subregion_by_name_not_found(self):
        response = await self.client.get("/region/subregion/name/nonexistent_subregion")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    @pytest.mark.parametrize("region_data", region_test)
    async def test_create_and_get_region(self, region_data):
        response = await self.client.post(f"/region/", json=region_data)
        assert response.status_code == status.HTTP_200_OK

        get_response = await self.client.get(
            f"/region/name/{region_data.get("name_region")}"
        )
        assert get_response.status_code == status.HTTP_200_OK
        region = RegionInDB(**get_response.json())
        assert region.name_region == region_data["name_region"]
        region_id = region.id
        get_response = await self.client.get(f"/region/{region_id}")
        assert get_response.status_code == status.HTTP_200_OK
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
        assert response.status_code == status.HTTP_200_OK

        get_response = await self.client.get(
            f"/region/subregion/name/{subregion_data.get("name_subregion")}"
        )
        assert get_response.status_code == status.HTTP_200_OK
        subregion = SubregionInDB(**get_response.json())
        assert subregion.name_subregion == subregion_data["name_subregion"]
        subregion_id = subregion.id
        get_response = await self.client.get(f"/region/subregion/{subregion_id}")
        assert get_response.status_code == status.HTTP_200_OK
        subregion = SubregionInDB(**get_response.json())
        assert subregion.name_subregion == subregion_data["name_subregion"]
        assert subregion.id == subregion_id

    @pytest.mark.asyncio
    async def test_update_region_1(self):
        get_response = await self.client.get("/region/name/USA")
        assert get_response.status_code == status.HTTP_200_OK
        region = RegionInDB(**get_response.json())
        assert region.name_region == "USA"
        region_id = region.id
        update_data = {"name_region": "US"}

        update_response = await self.client.put(
            f"/region/{region_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK
        update_region = RegionInDB(**update_response.json())
        assert update_region.name_region == "US"
        assert update_region.id == region_id

        get_response = await self.client.get("/region/name/US")
        assert get_response.status_code == status.HTTP_200_OK
        region = RegionInDB(**get_response.json())
        assert region.name_region == "US"
        assert region.id == region_id

    @pytest.mark.asyncio
    async def test_update_region_invalid(self):
        get_response = await self.client.get("/region/name/US")
        assert get_response.status_code == status.HTTP_200_OK
        region = RegionInDB(**get_response.json())
        assert region.name_region == "US"
        region_id = region.id
        update_data = {"name_region": "Russia"}
        update_response = await self.client.put(
            f"/region/{region_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_409_CONFLICT

        get_response = await self.client.get("/region/name/US")
        assert get_response.status_code == status.HTTP_200_OK
        region = RegionInDB(**get_response.json())
        assert region.name_region == "US"
        assert region.id == region_id

        region_id = 1101
        update_response = await self.client.put(
            f"/region/{region_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_subregion_1(self):
        get_response = await self.client.get("/region/subregion/name/Texas")
        assert get_response.status_code == status.HTTP_200_OK
        subregion = SubregionInDB(**get_response.json())
        assert subregion.name_subregion == "Texas"
        subregion_id = subregion.id
        region_id = subregion.id_region

        update_data = {"name_subregion": "UTA"}
        update_response = await self.client.put(
            f"/region/subregion/{subregion_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK
        update_subregion = SubregionInDB(**update_response.json())
        assert update_subregion.name_subregion == "UTA"
        assert update_subregion.id == subregion_id
        assert update_subregion.id_region == region_id

        update_response = await self.client.get(f"/region/subregion/{subregion_id}")
        assert update_response.status_code == status.HTTP_200_OK
        update_subregion = SubregionInDB(**update_response.json())
        assert update_subregion.name_subregion == "UTA"
        assert update_subregion.id == subregion_id
        assert update_subregion.id_region == region_id

        get_response = await self.client.get("/region/name/Russia")
        assert get_response.status_code == status.HTTP_200_OK
        region = RegionInDB(**get_response.json())
        assert region.name_region == "Russia"
        region_russia_id = region.id

        update_data = {"id_region": region_russia_id}
        update_response = await self.client.put(
            f"/region/subregion/{subregion_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK
        update_subregion = SubregionInDB(**update_response.json())
        assert update_subregion.name_subregion == "UTA"
        assert update_subregion.id == subregion_id
        assert update_subregion.id_region == region_russia_id

        update_response = await self.client.get(f"/region/subregion/{subregion_id}")
        assert update_response.status_code == status.HTTP_200_OK
        update_subregion = SubregionInDB(**update_response.json())
        assert update_subregion.name_subregion == "UTA"
        assert update_subregion.id == subregion_id
        assert update_subregion.id_region == region_russia_id

        update_data = {"id_region": region_id, "name_subregion": "Texas"}
        update_response = await self.client.put(
            f"/region/subregion/{subregion_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_200_OK
        update_subregion = SubregionInDB(**update_response.json())
        assert update_subregion.name_subregion == "Texas"
        assert update_subregion.id == subregion_id
        assert update_subregion.id_region == region_id

        update_response = await self.client.get(f"/region/subregion/{subregion_id}")
        assert update_response.status_code == status.HTTP_200_OK
        update_subregion = SubregionInDB(**update_response.json())
        assert update_subregion.name_subregion == "Texas"
        assert update_subregion.id == subregion_id
        assert update_subregion.id_region == region_id

    @pytest.mark.asyncio
    async def test_update_subregion_invalid(self):
        get_response = await self.client.get("/region/subregion/name/Texas")
        assert get_response.status_code == status.HTTP_200_OK
        subregion = SubregionInDB(**get_response.json())
        assert subregion.name_subregion == "Texas"
        subregion_id = subregion.id

        update_data = {}
        update_response = await self.client.put(
            f"/region/subregion/{subregion_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_409_CONFLICT

        update_data = {"name_subregion": "Florida"}
        update_response = await self.client.put(
            f"/region/subregion/{subregion_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_409_CONFLICT

        update_response = await self.client.put(
            "/region/subregion/1011", json=update_data
        )
        assert update_response.status_code == status.HTTP_404_NOT_FOUND

        update_data = {"id_region": 1131}
        update_response = await self.client.put(
            f"/region/subregion/{subregion_id}", json=update_data
        )
        assert update_response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_delete_region_invalid(self):
        # Мы не можем удалить регион так как у него есть субрегионы
        region = (await self.client.get("/region/name/Russia")).json()
        assert region
        response = await self.client.delete(f"/region/{region.get("id")}")
        assert response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_delete_subregion(self):
        subregions = (await self.client.get("/region/subregions/")).json()
        assert len(subregions) != 0
        for subregion in subregions:
            subregion_id = subregion.get("id")
            print(subregion_id)
            response = await self.client.delete(f"/region/subregion/{subregion_id}")
            assert response.status_code == status.HTTP_204_NO_CONTENT

        regions = (await self.client.get("/region/subregions/")).json()
        assert len(regions) == 0

    @pytest.mark.asyncio
    async def test_delete_region(self):
        regions = (await self.client.get("/region/regions/")).json()
        assert len(regions) != 0
        for region in regions:
            response = await self.client.delete(f"/region/{region.get("id")}")
            assert response.status_code == status.HTTP_204_NO_CONTENT

        regions = (await self.client.get("/region/regions/")).json()
        assert len(regions) == 0
