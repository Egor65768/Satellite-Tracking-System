import pytest
from app.main import app
from app.schemas import CountryInDB
from tests.test_data import country_test_data
from httpx import ASGITransport, AsyncClient


@pytest.fixture
async def async_client():
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client


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
        create_response = await self.client.post("/country/", json=country_data)
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
    async def test_delete_country(self):
        create_response = await self.client.get("/country/list/")
        assert create_response.status_code == 200
        country_list = create_response.json()
        assert len(country_list) == 3
        for country in country_list:
            country_id = country["id"]
            delete_response = await self.client.delete(f"/country/{country_id}")
            assert delete_response.status_code == 204
        create_response = await self.client.get("/country/list/")
        assert create_response.status_code == 200
        country_list = create_response.json()
        assert len(country_list) == 0


# @pytest.mark.asyncio
# async def test_get_country_by_abbreviation(db: AsyncSession, test_country_data: dict):
#     # Тест получения страны по аббревиатуре
#     # Создаем страну
#     create_response = client.post("/countries/", json=test_country_data)
#     assert create_response.status_code == 200
#
#     # Получаем страну по аббревиатуре
#     get_response = client.get(f"/countries/abbreviation/?abbreviation={test_country_data['abbreviation']}")
#     assert get_response.status_code == 200
#     country = CountryInDB(**get_response.json())
#
#     # Проверяем данные
#     assert country.abbreviation == test_country_data["abbreviation"]
#
#
# @pytest.mark.asyncio
# async def test_get_country_by_abbreviation_not_found(db: AsyncSession):
#     # Тест для несуществующей аббревиатуры
#     response = client.get("/countries/abbreviation/?abbreviation=XXX")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Country not found"
#
#
# @pytest.mark.asyncio
# async def test_create_country_conflict(db: AsyncSession, test_country_data: dict):
#     # Тест на конфликт при создании страны с существующей аббревиатурой
#     # Создаем первую страну
#     response1 = client.post("/countries/", json=test_country_data)
#     assert response1.status_code == 200
#
#     # Пытаемся создать страну с той же аббревиатурой
#     test_country_data["name"] = "Another Country"
#     response2 = client.post("/countries/", json=test_country_data)
#     assert response2.status_code == 409
#     assert "cannot be created" in response2.json()["detail"]
#
#
# @pytest.mark.asyncio
# async def test_delete_country(db: AsyncSession, test_country_data: dict):
#     # Тест удаления страны
#     # Создаем страну
#     create_response = client.post("/countries/", json=test_country_data)
#     assert create_response.status_code == 200
#     created_country = create_response.json()
#
#     # Удаляем страну
#     delete_response = client.delete(f"/countries/{created_country['id']}")
#     assert delete_response.status_code == 204
#
#     # Проверяем, что страна удалена
#     get_response = client.get(f"/countries/id/{created_country['id']}")
#     assert get_response.status_code == 404
#
#
# @pytest.mark.asyncio
# async def test_delete_country_not_found(db: AsyncSession):
#     # Тест удаления несуществующей страны
#     response = client.delete("/countries/999999")
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Country not found"
#
#
# @pytest.mark.asyncio
# async def test_get_countries_list(db: AsyncSession, test_country_data: dict):
#     # Тест получения списка стран
#     # Создаем несколько стран
#     for i in range(3):
#         country_data = test_country_data.copy()
#         country_data["name"] = f"Country {i}"
#         country_data["abbreviation"] = f"C{i}"
#         client.post("/countries/", json=country_data)
#
#     # Получаем список стран
#     response = client.get("/countries/list/?limit=10&offset=0")
#     assert response.status_code == 200
#     countries = response.json()
#
#     # Проверяем, что получили список
#     assert isinstance(countries, list)
#     assert len(countries) >= 3  # Могут быть и другие страны в базе
#
#
# @pytest.mark.asyncio
# async def test_update_country(db: AsyncSession, test_country_data: dict, test_country_update_data: dict):
#     # Тест обновления страны
#     # Создаем страну
#     create_response = client.post("/countries/", json=test_country_data)
#     assert create_response.status_code == 200
#     created_country = create_response.json()
#
#     # Обновляем страну
#     update_response = client.put(
#         f"/countries/{created_country['id']}",
#         json=test_country_update_data
#     )
#     assert update_response.status_code == 200
#     updated_country = update_response.json()
#
#     # Проверяем обновленные данные
#     assert updated_country["name"] == test_country_update_data["name"]
#     assert updated_country["abbreviation"] == test_country_update_data["abbreviation"]
#     assert updated_country["population"] == test_country_update_data["population"]
#     assert updated_country["capital"] == test_country_update_data["capital"]
#
#     # Проверяем, что ID остался тот же
#     assert updated_country["id"] == created_country["id"]
#
#
# @pytest.mark.asyncio
# async def test_update_country_not_found(db: AsyncSession, test_country_update_data: dict):
#     # Тест обновления несуществующей страны
#     response = client.put("/countries/999999", json=test_country_update_data)
#     assert response.status_code == 404
#     assert response.json()["detail"] == "Country not found"
#
#
# @pytest.mark.asyncio
# async def test_update_country_conflict(db: AsyncSession, test_country_data: dict):
#     # Тест конфликта при обновлении (например, на существующую аббревиатуру)
#     # Создаем первую страну
#     response1 = client.post("/countries/", json=test_country_data)
#     assert response1.status_code == 200
#
#     # Создаем вторую страну
#     country_data2 = test_country_data.copy()
#     country_data2["name"] = "Another Country"
#     country_data2["abbreviation"] = "AC"
#     response2 = client.post("/countries/", json=country_data2)
#     assert response2.status_code == 200
#     country2 = response2.json()
#
#     # Пытаемся обновить вторую страну с аббревиатурой первой
#     update_data = {"abbreviation": test_country_data["abbreviation"]}
#     update_response = client.put(
#         f"/countries/{country2['id']}",
#         json=update_data
#     )
#     assert update_response.status_code == 409
#     assert "cannot be updated" in update_response.json()["detail"]
