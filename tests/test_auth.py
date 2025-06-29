import pytest
from fastapi import status
from tests.test_data import user_data_tests, country_test_data
from app.core import settings
from asyncio import sleep

jwt_tokens = dict()
headers_auth = dict()


@pytest.mark.usefixtures("async_client")
class TestUserAPI:

    @pytest.fixture(autouse=True)
    def _setup_client(self, async_client):
        self.client = async_client

    @pytest.mark.asyncio
    async def test_create_user(self):
        user_data = user_data_tests[0]
        response = await self.client.post(
            "/user/",
            json={"user_create": user_data},
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_create_tokens(self):
        user_data = user_data_tests[0]
        login_data = {
            "username": user_data.get("email"),
            "password": user_data.get("password"),
        }
        access_token_expire_seconds = settings.ACCESS_TOKEN_EXPIRE_SECONDS
        settings.ACCESS_TOKEN_EXPIRE_SECONDS = 2
        assert settings.ACCESS_TOKEN_EXPIRE_SECONDS == 2
        response = await self.client.post(
            "/auth/tokens",
            data=login_data,
        )
        settings.ACCESS_TOKEN_EXPIRE_SECONDS = access_token_expire_seconds
        assert response.status_code == status.HTTP_200_OK
        data_t = response.json()
        jwt_tokens["access_token"] = data_t.get("access_token")
        jwt_tokens["refresh_token"] = data_t.get("refresh_token")
        jwt_tokens["token_type"] = data_t.get("token_type")
        headers_auth["Authorization"] = f"Bearer {jwt_tokens['access_token']}"

    @pytest.mark.asyncio
    async def test_auth_1(self):
        country_data = country_test_data[0]
        create_response = await self.client.post(
            "/country/", json=country_data, headers=headers_auth
        )
        assert create_response.status_code == status.HTTP_403_FORBIDDEN
        assert create_response.json() == {"detail": "Insufficient permissions"}
        create_response = await self.client.post("/country/", json=country_data)
        assert create_response.status_code == status.HTTP_401_UNAUTHORIZED

        headers_auth_invalid = dict()
        invalid_refresh_token = (
            "eyJhbGciOiJIUzI1NiIsInR"
            "5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODk"
            "wIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWU"
            "sImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nM"
            "iGM6H9FNFUROf3wh7SmqJp-QV30"
        )
        headers_auth_invalid["Authorization"] = f"Bearer {invalid_refresh_token}"

        create_response = await self.client.post(
            "/country/", json=country_data, headers=headers_auth_invalid
        )
        assert create_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert create_response.json() == {"detail": "Invalid access token"}
        await sleep(2)
        create_response = await self.client.post(
            "/country/", json=country_data, headers=headers_auth
        )
        assert create_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert create_response.json() == {"detail": "Access token expired"}

        headers_refresh = dict()
        old_refresh_token = jwt_tokens["refresh_token"]
        headers_refresh["Authorization"] = f"Bearer {jwt_tokens['refresh_token']}"
        response = await self.client.post(
            "/auth/refresh-token",
            headers=headers_refresh,
        )
        assert response.status_code == status.HTTP_200_OK
        data_t = response.json()
        new_refresh_token = data_t.get("refresh_token")
        assert old_refresh_token != new_refresh_token
        response = await self.client.post(
            "/auth/refresh-token",
            headers=headers_refresh,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": "Refresh token not found in db"}
        headers_refresh["Authorization"] = f"Bearer {new_refresh_token}"
        response = await self.client.post(
            "/auth/refresh-token",
            headers=headers_refresh,
        )
        assert response.status_code == status.HTTP_200_OK
        data_t = response.json()
        jwt_tokens["access_token"] = data_t.get("access_token")
        jwt_tokens["refresh_token"] = data_t.get("refresh_token")
        jwt_tokens["token_type"] = data_t.get("token_type")
        new_refresh_token = data_t.get("refresh_token")
        headers_refresh["Authorization"] = f"Bearer {new_refresh_token}"
        headers_auth["Authorization"] = f"Bearer {jwt_tokens['access_token']}"

    @pytest.mark.asyncio
    async def test_delete_user(self):
        country_data = country_test_data[0]
        user_data = user_data_tests[0]
        delete_response = await self.client.delete(
            "/user/", params={"user_mail": user_data.get("email")}
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        create_response = await self.client.post(
            "/country/", json=country_data, headers=headers_auth
        )
        assert create_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert create_response.json() == {
            "detail": "The access token contains a non-existent user ID"
        }
