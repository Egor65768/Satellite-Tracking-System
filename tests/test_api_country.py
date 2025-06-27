import pytest
from fastapi import status
from tests.test_data import country_test_data, token_data, admin_data, headers_auth
from app.schemas import CountryInDB, AdminPassword
from app.core import settings


# @pytest.mark.asyncio
# async def test_create_user(async_client):
#     admin_password = AdminPassword(password=settings.ADMIN_SECRET_KEY)
#     response = await async_client.post(
#         "/user/",
#         json={
#             "user_create": admin_data,
#             "admin_password": admin_password.model_dump(),
#         },
#     )
#     assert response.status_code == status.HTTP_200_OK
#
#
# @pytest.mark.asyncio
# async def test_create_token(async_client):
#     login_data = {
#         "username": admin_data.get("email"),
#         "password": admin_data.get("password"),
#     }
#     response = await async_client.post(
#         "/auth/tokens",
#         data=login_data,
#     )
#     assert response.status_code == status.HTTP_200_OK
#     data_t = response.json()
#     assert data_t
#     token_data["access_token"] = data_t.get("access_token")
#     token_data["refresh_token"] = data_t.get("refresh_token")
#     token_data["token_type"] = data_t.get("token_type")
#     headers_auth["Authorization"] = f"Bearer {token_data['access_token']}"
#


@pytest.mark.usefixtures("async_client")
class TestCountryAPI:
    # Автоматически запускает _setup_client перед каждым тестом, передавая туда async_client.
    @pytest.fixture(autouse=True)
    def _setup_client(self, async_client):
        self.client = async_client

    @pytest.mark.asyncio
    async def test_get_country_by_id_not_found(self):
        response = await self.client.get("/country/id/999999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Country not found"

    @pytest.mark.asyncio
    async def test_get_country_by_abbreviation_not_found(self):
        response = await self.client.get("/country/abbreviation/?abbreviation=UA")
        assert response.status_code == 404
        assert response.json()["detail"] == "Country not found"

    @pytest.mark.asyncio
    async def test_get_invalid(self):
        response = await self.client.get("/country/id/3.1415")
        assert response.status_code == 422

        response = await self.client.get("/country/id/ABNS")
        assert response.status_code == 422

        response = await self.client.get(
            "/country/abbreviation/?abbreviation=AAAAAAAAAAAAAAAA"
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data", country_test_data)
    async def test_create_and_get_country_by_id(self, country_data):
        create_response = await self.client.post(
            "/country/", json=country_data, headers=headers_auth
        )
        assert create_response.status_code == 200
        created_country = create_response.json()
        get_response = await self.client.get(f"/country/id/{created_country['id']}")
        assert get_response.status_code == 200
        country = CountryInDB(**get_response.json())

        assert country.full_name == country_data["full_name"]
        assert country.abbreviation == country_data["abbreviation"]
        assert country.id == country_data["id"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data", country_test_data)
    async def test_get_country_by_abbreviation(self, country_data):
        get_response = await self.client.get(
            f"/country/abbreviation/?abbreviation={country_data['abbreviation']}"
        )
        assert get_response.status_code == 200
        country = CountryInDB(**get_response.json())
        assert country.abbreviation == country_data["abbreviation"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data", country_test_data)
    async def test_get_country_by_id(self, country_data):
        get_response = await self.client.get(f"/country/id/{country_data['id']}")
        assert get_response.status_code == 200
        country = CountryInDB(**get_response.json())
        assert country.abbreviation == country_data["abbreviation"]

    @pytest.mark.asyncio
    async def test_create_invalid(self):
        country_data = country_test_data[0]
        create_response = await self.client.post(
            "/country/", json=country_data, headers=headers_auth
        )
        assert create_response.status_code == 409

    @pytest.mark.asyncio
    async def test_update(self):
        country_data = {"abbreviation": "CAM"}
        response = await self.client.put(
            "/country/1", json=country_data, headers=headers_auth
        )
        assert response.status_code == 200

        get_response = await self.client.get(f"/country/id/1")
        assert get_response.status_code == 200
        country = CountryInDB(**get_response.json())
        assert country.abbreviation == country_data["abbreviation"]

        country_data = {"abbreviation": "IRL", "full_name": "Irland"}
        response = await self.client.put(
            "/country/1", json=country_data, headers=headers_auth
        )
        assert response.status_code == 200

        get_response = await self.client.get(f"/country/id/1")
        assert get_response.status_code == 200
        country = CountryInDB(**get_response.json())
        assert country.abbreviation == country_data["abbreviation"]
        assert country.full_name == country_data["full_name"]

        country_data = {"abbreviation": "IRL", "full_name": "Irland"}
        response = await self.client.put(
            "/country/15", json=country_data, headers=headers_auth
        )
        assert response.status_code == 404

        country_data = {"abbreviation": "RU"}
        response = await self.client.put(
            "/country/1", json=country_data, headers=headers_auth
        )
        assert response.status_code == 409

        country_data = {"full_name": "Россия"}
        response = await self.client.put(
            "/country/1", json=country_data, headers=headers_auth
        )
        assert response.status_code == 409

    @pytest.mark.asyncio
    async def test_delete_country(self):
        create_response = await self.client.get("/country/list/")
        assert create_response.status_code == 200
        country_list = create_response.json()
        assert len(country_list) == 3
        for country in country_list:
            country_id = country["id"]
            delete_response = await self.client.delete(
                f"/country/{country_id}", headers=headers_auth
            )
            assert delete_response.status_code == 204
        create_response = await self.client.get("/country/list/")
        assert create_response.status_code == 200
        country_list = create_response.json()
        assert len(country_list) == 0
