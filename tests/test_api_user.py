import pytest
from fastapi import status
from tests.test_data import user_data_tests, user_data_admin
from app.core import settings
from app.schemas import AdminPassword


@pytest.mark.usefixtures("async_client")
class TestUserAPI:

    @pytest.fixture(autouse=True)
    def _setup_client(self, async_client):
        self.client = async_client

    @pytest.mark.asyncio
    async def test_get_user_not_found(self):
        get_response = await self.client.get(f"/user/12")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
        get_response = await self.client.get(
            "/user/", params={"user_mail": "nkh2uhdu@gmail.com"}
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND

        get_response = await self.client.get(
            "/user/", params={"user_mail": "nkh2uhduail.com"}
        )
        assert get_response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    @pytest.mark.parametrize("user_data", user_data_tests)
    async def test_create_1(self, user_data):
        response = await self.client.post(
            "/user/",
            json={"user_create": user_data},
        )
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.asyncio
    async def test_create_2_invalid(self):
        user_data = user_data_tests[0]
        response = await self.client.post(
            "/user/",
            json={"user_create": user_data},
        )
        assert response.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_create_3_admin_invalid(self):
        admin_password = AdminPassword(password="invalid_password1jdjSJK")
        response = await self.client.post(
            "/user/",
            json={"user_create": user_data_admin},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN
        response = await self.client.post(
            "/user/",
            json={
                "user_create": user_data_admin,
                "admin_password": admin_password.model_dump(),
            },
        )
        print(response.json())
        assert response.status_code == status.HTTP_403_FORBIDDEN

        get_response = await self.client.get(
            "/user/users/",
        )
        assert get_response.status_code == status.HTTP_200_OK
        users = get_response.json()
        assert len(users) == len(user_data_tests) + 1

    @pytest.mark.asyncio
    async def test_create_4_admin(self):
        admin_password = AdminPassword(password=settings.ADMIN_SECRET_KEY)
        response = await self.client.post(
            "/user/",
            json={
                "user_create": user_data_admin,
                "admin_password": admin_password.model_dump(),
            },
        )
        assert response.status_code == status.HTTP_200_OK

        get_response = await self.client.get(
            "/user/users/",
        )
        assert get_response.status_code == status.HTTP_200_OK
        users = get_response.json()
        assert len(users) == len(user_data_tests) + 1 + 1

    @pytest.mark.asyncio
    async def test_delete_admin(self):
        get_response = await self.client.get(
            "/user/users/",
        )
        assert get_response.status_code == status.HTTP_200_OK
        users = get_response.json()
        assert len(users) == len(user_data_tests) + 1 + 1

        delete_response = await self.client.delete(
            "/user/", params={"user_mail": user_data_admin.get("email")}
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        get_response = await self.client.get(
            "/user/users/",
        )
        assert get_response.status_code == status.HTTP_200_OK
        users = get_response.json()
        assert len(users) == len(user_data_tests) + 1

    @pytest.mark.asyncio
    async def test_delete_users(self):
        get_response = await self.client.get(
            "/user/users/",
        )
        assert get_response.status_code == status.HTTP_200_OK
        users = get_response.json()
        assert len(users) == len(user_data_tests) + 1
        for user in user_data_tests:
            user_email = user.get("email")
            delete_response = await self.client.delete(
                "/user/", params={"user_mail": user_email}
            )
            assert delete_response.status_code == status.HTTP_204_NO_CONTENT
        get_response = await self.client.get(
            "/user/users/",
        )
        assert get_response.status_code == status.HTTP_200_OK
        users = get_response.json()
        assert len(users) == 1

        delete_response = await self.client.delete(
            "/user/", params={"user_mail": "not_found_email@mail.ru"}
        )
        assert delete_response.status_code == status.HTTP_404_NOT_FOUND
