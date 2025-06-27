import pytest
from fastapi import status
from copy import copy
from tests.test_data import (
    country_test_data,
    satellite_test_date,
    test_create_data,
    region_test,
    region_list,
    subregion_list,
    headers_auth,
)
from tests.test_service_coverage_zone import get_data_image
from app.s3_service import S3Service


@pytest.mark.asyncio
async def test_check_count_country_1(async_client):
    assert len((await async_client.get("/country/list/")).json()) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("country_data", country_test_data)
async def test_create_country(country_data, async_client):
    create_response = await async_client.post(
        "/country/", json=country_data, headers=headers_auth
    )
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
    async def test_get_coverage_zone(self):
        coverage_zone_data = test_create_data[0]
        response = await self.client.get("/coverage_zone/invalid_id_coverage_zone")
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = await self.client.get(
            f"/coverage_zone/{coverage_zone_data.get("id")}"
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data is not None
        assert response_data.get("id") == coverage_zone_data.get("id")
        assert response_data.get("transmitter_type") == coverage_zone_data.get(
            "transmitter_type"
        )
        assert response_data.get("satellite_code") == satellite_test_date[0].get(
            "international_code"
        )

        s3_service = S3Service()
        local_data = await get_data_image(coverage_zone_data.get("image"))
        assert local_data is not None
        s3_data = await s3_service.get_file(coverage_zone_data.get("id"))
        assert s3_data is not None
        assert s3_data == local_data

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
    async def test_add_regions_list_by_coverage_zone_invalid(self):
        coverage_zone_id = test_create_data[1].get("id")

        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_test)
        new_invalid_region = copy(region_list)
        new_invalid_region.append(region_test[0])

        response = await self.client.post(
            f"/coverage_zone/regions/{coverage_zone_id}", json=region_test
        )

        assert response.status_code == status.HTTP_409_CONFLICT
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
            assert response.status_code == status.HTTP_409_CONFLICT

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
    async def test_add_subregion_by_coverage_zone(self):
        coverage_zone_id = test_create_data[1].get("id")
        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_list) + len(region_test)
        region_list_local = response.json()
        for region in region_list_local:
            assert len(region.get("subregion_list")) == 0
        data_subregion = {
            "name_subregion": "test_subregion_1",
            "id_region": (await self.client.get(f"/region/name/USA")).json().get("id"),
        }
        response = await self.client.post(
            f"/coverage_zone/subregion/{coverage_zone_id}", json=data_subregion
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_list) + len(region_test)
        region_list_local = response.json()
        for region in region_list_local:
            if region.get("name_region") != "USA":
                assert len(region.get("subregion_list")) == 0
            else:
                assert len(region.get("subregion_list")) == 1
                assert (
                    region.get("subregion_list")[0].get("name_subregion")
                    == "test_subregion_1"
                )

        response = await self.client.post(
            f"/coverage_zone/subregion/{coverage_zone_id}", json=data_subregion
        )
        assert response.status_code == status.HTTP_409_CONFLICT

        coverage_zone_id_invalid = "invalid_id_zone"
        response = await self.client.post(
            f"/coverage_zone/subregion/{coverage_zone_id_invalid}", json=data_subregion
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_add_subregion_by_coverage_zone_list(self):
        coverage_zone_id = test_create_data[0].get("id")
        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_list)
        region_list_local = response.json()
        for region in region_list_local:
            assert len(region.get("subregion_list")) == 0

        create_subregion_data = list()
        for subregion in subregion_list:
            create_subregion_data.append(
                {
                    "name_subregion": subregion.get("name_subregion"),
                    "id_region": (
                        await self.client.get(
                            f"/region/name/{subregion.get("name_region")}"
                        )
                    )
                    .json()
                    .get("id"),
                }
            )
        response = await self.client.post(
            f"/coverage_zone/subregions/{coverage_zone_id}", json=create_subregion_data
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_list)
        region_list_local = response.json()
        for region in region_list_local:
            assert region.get("subregion_list") is not None

    @pytest.mark.asyncio
    async def test_add_subregion_by_coverage_zone_list_invalid(self):
        coverage_zone_id = test_create_data[0].get("id")
        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        regions_list_local = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(regions_list_local) != 0
        region = regions_list_local[0]
        assert region is not None
        assert len(region.get("subregion_list")) != 0
        subregion_name = region.get("subregion_list")[0].get("name_subregion")
        region_id = region.get("id")
        new_subregions_data = [
            {"name_subregion": subregion_name, "id_region": region_id},
            {"name_subregion": "new_subregion_test_1", "id_region": region_id},
            {"name_subregion": "new_subregion_test_2", "id_region": region_id},
            {"name_subregion": "new_subregion_test_3", "id_region": region_id},
        ]
        response = await self.client.post(
            f"/coverage_zone/subregions/{coverage_zone_id}", json=new_subregions_data
        )
        assert response.status_code == status.HTTP_409_CONFLICT
        result = response.json().get("detail").get("result")
        for i, r in enumerate(result):
            if i == 0:
                assert not r
            else:
                assert r

    @pytest.mark.asyncio
    async def test_add_subregion_by_coverage_zone_2(self):
        coverage_zone_data_request = {
            "coverage_zone_id": "2121-1424-24270",
            "transmitter_type": "Kuku-Band",
            "satellite_code": satellite_test_date[0].get("international_code"),
        }
        files = {
            "image": (
                "tests/test/test4.png",
                await get_data_image("tests/test/test4.png"),
                "image/png",
            )
        }
        response = await self.client.post(
            "/coverage_zone/", data=coverage_zone_data_request, files=files
        )
        assert response.status_code == status.HTTP_200_OK
        coverage_zone_id = "2121-1424-24270"

        region_list_test = [
            {"name_region": "USA"},
            {"name_region": "New Zeland"},
            {"name_region": "Russia"},
        ]

        for region in region_list_test:
            response = await self.client.post(
                f"/coverage_zone/region/{coverage_zone_id}", json=region
            )
            assert response.status_code == status.HTTP_204_NO_CONTENT

        subregion_data = [
            {
                "name_subregion": "UTA",
                "id_region": (await self.client.get(f"/region/name/USA"))
                .json()
                .get("id"),
            },
            {
                "name_subregion": "Wellington",
                "id_region": (await self.client.get(f"/region/name/New Zeland"))
                .json()
                .get("id"),
            },
            {
                "name_subregion": "California",
                "id_region": (await self.client.get(f"/region/name/USA"))
                .json()
                .get("id"),
            },
            {
                "name_subregion": "Auckland",
                "id_region": (await self.client.get(f"/region/name/New Zeland"))
                .json()
                .get("id"),
            },
            {
                "name_subregion": "Moscow",
                "id_region": (await self.client.get(f"/region/name/Russia"))
                .json()
                .get("id"),
            },
        ]
        for subregion in subregion_data:
            response = await self.client.post(
                f"/coverage_zone/subregion/{coverage_zone_id}", json=subregion
            )
            assert response.status_code == status.HTTP_204_NO_CONTENT
        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        assert response.status_code == status.HTTP_200_OK
        regions_list = response.json()
        for region in regions_list:
            if region.get("name_region") == "USA":
                subregion_region_list = region.get("subregion_list")
                assert len(subregion_region_list) == 2
                for subregion in subregion_region_list:
                    assert subregion.get("name_subregion") in ["UTA", "California"]
            elif region.get("name_region") == "New Zeland":
                subregion_region_list = region.get("subregion_list")
                assert len(subregion_region_list) == 2
                for subregion in subregion_region_list:
                    assert subregion.get("name_subregion") in ["Auckland", "Wellington"]
            if region.get("name_region") == "Russia":
                subregion_region_list = region.get("subregion_list")
                assert len(subregion_region_list) == 1
                for subregion in subregion_region_list:
                    assert subregion.get("name_subregion") in ["Moscow"]

    @pytest.mark.asyncio
    async def test_delete_region_coverage_zone(self):
        coverage_zone_id_1 = test_create_data[0].get("id")
        coverage_zone_id_2 = test_create_data[1].get("id")

        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id_1}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_list)

        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id_2}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_list) + len(region_test)

        delete_data = {"name_region": "region_1"}
        response = await self.client.delete(
            f"/coverage_zone/{coverage_zone_id_1}/region_name/{delete_data.get("name_region")}"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id_1}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_list) - 1

        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id_2}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == len(region_list) + len(region_test)

        response = await self.client.delete(
            f"/coverage_zone/{coverage_zone_id_1}/region_name/{delete_data.get("name_region")}"
        )
        assert response.status_code == status.HTTP_409_CONFLICT

        coverage_zone_id_fake = "fake_id_2u9u4flkd"
        response = await self.client.delete(
            f"/coverage_zone/{coverage_zone_id_fake}/region_name/{delete_data.get("name_region")}"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_subregion_coverage_zone(self):
        coverage_zone_id = "2121-1424-24270"
        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        assert response.status_code == status.HTTP_200_OK
        region_list_local = response.json()
        for region in region_list_local:
            if region.get("name_region") == "Russia":
                assert len(region.get("subregion_list")) == 1
                assert region.get("subregion_list")[0].get("name_subregion") == "Moscow"

        delete_data = {"subname_region": "Moscow"}

        coverage_zone_id_fake = "fake_id_fake_2131"
        response = await self.client.delete(
            f"/coverage_zone/{coverage_zone_id_fake}/subregion_name/{delete_data.get("subname_region")}"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

        response = await self.client.delete(
            f"/coverage_zone/{coverage_zone_id}/subregion_name/{delete_data.get("subname_region")}"
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        response = await self.client.delete(
            f"/coverage_zone/{coverage_zone_id}/subregion_name/{delete_data.get("subname_region")}"
        )
        assert response.status_code == status.HTTP_409_CONFLICT

        response = await self.client.get(f"/coverage_zone/regions/{coverage_zone_id}")
        assert response.status_code == status.HTTP_200_OK
        region_list_local = response.json()
        for region in region_list_local:
            if region.get("name_region") == "Russia":
                assert len(region.get("subregion_list")) == 0

    @pytest.mark.asyncio
    async def test_update_coverage_zone_1(self):
        s3_service = S3Service()
        coverage_zone_data = test_create_data[1]
        response = await self.client.get(
            f"/coverage_zone/{coverage_zone_data.get("id")}"
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data is not None
        assert response_data.get("id") == coverage_zone_data.get("id")
        assert response_data.get("transmitter_type") == coverage_zone_data.get(
            "transmitter_type"
        )
        assert response_data.get("satellite_code") == satellite_test_date[0].get(
            "international_code"
        )

        update_data = {"transmitter_type": "Tu-Band"}
        response = await self.client.put(
            f"/coverage_zone/{coverage_zone_data.get("id")}", data=update_data
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data.get("transmitter_type") == "Tu-Band"

        response = await self.client.get(
            f"/coverage_zone/{coverage_zone_data.get("id")}"
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data is not None
        assert response_data.get("id") == coverage_zone_data.get("id")
        assert response_data.get("transmitter_type") == "Tu-Band"
        assert response_data.get("satellite_code") == satellite_test_date[0].get(
            "international_code"
        )

        local_data = await get_data_image(coverage_zone_data.get("image"))
        assert local_data is not None
        s3_data = await s3_service.get_file(coverage_zone_data.get("id"))
        assert s3_data is not None
        assert s3_data == local_data

        image_new = "tests/test/test4.png"
        local_data_image_new = await get_data_image(image_new)
        files = {
            "image": (
                image_new,
                local_data_image_new,
                "image/png",
            )
        }
        response = await self.client.put(
            f"/coverage_zone/{coverage_zone_data.get("id")}", files=files
        )
        assert response.status_code == status.HTTP_200_OK

        local_data = await get_data_image(image_new)
        assert local_data is not None
        s3_data = await s3_service.get_file(coverage_zone_data.get("id"))
        assert s3_data is not None
        assert s3_data == local_data

    @pytest.mark.asyncio
    async def test_update_coverage_zone_2(self):
        s3_service = S3Service()
        coverage_zone_data = test_create_data[1]
        update_data = {
            "transmitter_type": "Kuku-Band",
            "satellite_code": satellite_test_date[1].get("international_code"),
        }
        image_new = "tests/test/test1.jpg"
        local_data_image_new = await get_data_image(image_new)
        files = {
            "image": (
                image_new,
                local_data_image_new,
                "image/png",
            )
        }
        response = await self.client.put(
            f"/coverage_zone/{coverage_zone_data.get("id")}",
            data=update_data,
            files=files,
        )
        assert response.status_code == status.HTTP_200_OK

        response = await self.client.get(
            f"/coverage_zone/{coverage_zone_data.get("id")}"
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()

        assert response_data is not None
        assert response_data.get("id") == coverage_zone_data.get("id")
        assert response_data.get("transmitter_type") == "Kuku-Band"
        assert response_data.get("satellite_code") == satellite_test_date[1].get(
            "international_code"
        )

        local_data = await get_data_image(image_new)
        assert local_data is not None
        s3_data = await s3_service.get_file(coverage_zone_data.get("id"))
        assert s3_data is not None
        assert s3_data == local_data

    @pytest.mark.asyncio
    async def test_delete_coverage_zone(self):
        response = await self.client.get(
            "/coverage_zone/coverage_zones/count/",
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {"number_of_coverage_zones": 3}

        response = await self.client.get(
            "/coverage_zone/coverage_zones/",
        )
        assert response.status_code == status.HTTP_200_OK
        zones = response.json()
        zone_1_id = zones[0].get("id")
        for zone in zones:
            zone_id = zone.get("id")
            response = await self.client.delete(f"/coverage_zone/{zone_id}")
            assert response.status_code == status.HTTP_204_NO_CONTENT

        response = await self.client.delete(f"/coverage_zone/{zone_1_id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND

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
        delete_response = await async_client.delete(
            f"/country/{country_id}", headers=headers_auth
        )
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
