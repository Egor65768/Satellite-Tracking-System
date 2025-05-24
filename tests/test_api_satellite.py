import pytest
from fastapi import status
from datetime import date
from app.schemas import (
    SatelliteCreate,
    SatelliteCharacteristicCreate,
    SatelliteUpdate,
    SatelliteCharacteristicUpdate,
)
from tests.test_data import country_test_data, satellite_test_date
from copy import copy


@pytest.mark.asyncio
async def test_check_count_country_1(async_client):
    assert len((await async_client.get("/country/list/")).json()) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("country_data", country_test_data)
async def test_create_and_get_country_by_id(country_data, async_client):
    create_response = await async_client.post("/country/", json=country_data)
    assert create_response.status_code == 200


@pytest.mark.asyncio
async def test_check_count_country_2(async_client):
    assert len((await async_client.get("/country/list/")).json()) == len(
        country_test_data
    )


@pytest.mark.usefixtures("async_client")
class TestSatelliteAPI:

    @pytest.fixture(autouse=True)
    def _setup_client(self, async_client):
        self.client = async_client

    @pytest.mark.asyncio
    async def test_create_and_get_satellite(self):
        satellite_data = copy(satellite_test_date[0])
        satellite_data["launch_date"] = satellite_data["launch_date"].isoformat()
        # Создаем спутник
        create_response = await self.client.post("/satellite/", json=satellite_data)
        assert create_response.status_code == status.HTTP_200_OK
        assert create_response.json()
        print(create_response.json())

        # Получаем созданный спутник
        print(satellite_data.get("international_code"))
        get_response = await self.client.get(
            f"/satellite/{satellite_data.get("international_code")}"
        )
        satellite = get_response.json()
        print(satellite)

        assert get_response.status_code == status.HTTP_200_OK

        # Проверяем соответствие данных
        assert satellite["international_code"] == satellite_data.get(
            "international_code"
        )
        assert satellite["name_satellite"] == satellite_data.get("name_satellite")

    #
    # async def test_get_nonexistent_satellite(self, client: AsyncClient):
    #     # Тест получения несуществующего спутника
    #     response = await client.get("/satellite/NONEXISTENT-CODE")
    #     assert response.status_code == status.HTTP_404_NOT_FOUND
    #
    # async def test_create_satellite_duplicate(self, client: AsyncClient):
    #     # Тест создания дубликата спутника
    #     satellite_data = SatelliteCreate(
    #         international_code="2023-002A",
    #         name_satellite="Duplicate Test",
    #         norad_id=99998,
    #         launch_date=date.today(),
    #         country_id=1
    #     )
    #
    #     # Первое создание - должно быть успешным
    #     response1 = await client.post("/satellite/", json=satellite_data.dict())
    #     assert response1.status_code == status.HTTP_200_OK
    #
    #     # Второе создание с теми же данными - должно вернуть ошибку
    #     response2 = await client.post("/satellite/", json=satellite_data.dict())
    #     assert response2.status_code == status.HTTP_409_CONFLICT
    #
    # async def test_create_and_get_satellite_characteristics(self, client: AsyncClient):
    #     # Тест создания и получения характеристик спутника
    #     # Сначала создаем спутник
    #     satellite_data = SatelliteCreate(
    #         international_code="2023-003A",
    #         name_satellite="Test With Characteristics",
    #         norad_id=99997,
    #         launch_date=date.today(),
    #         country_id=1
    #     )
    #     satellite_response = await client.post("/satellite/", json=satellite_data.dict())
    #     assert satellite_response.status_code == status.HTTP_200_OK
    #
    #     # Создаем характеристики
    #     characteristics_data = SatelliteCharacteristicCreate(
    #         international_code=satellite_data.international_code,
    #         longitude=45.0,
    #         period=90.5,
    #         launch_site="Baikonur",
    #         rocket="Proton-M",
    #         launch_mass=3500.5,
    #         manufacturer="RSC Energia",
    #         model="Test Model",
    #         expected_lifetime=15,
    #         remaining_lifetime=10,
    #         details="Test satellite characteristics"
    #     )
    #
    #     char_response = await client.post(
    #         "/satellite/characteristic",
    #         json=characteristics_data.dict()
    #     )
    #     assert char_response.status_code == status.HTTP_200_OK
    #
    #     # Получаем характеристики
    #     get_response = await client.get(
    #         f"/satellite/{satellite_data.international_code}/characteristics"
    #     )
    #     assert get_response.status_code == status.HTTP_200_OK
    #     characteristics = get_response.json()
    #
    #     # Проверяем данные
    #     assert characteristics["longitude"] == characteristics_data.longitude
    #     assert characteristics["rocket"] == characteristics_data.rocket
    #
    # async def test_create_complete_satellite(self, client: AsyncClient):
    #     # Тест создания спутника с полной информацией
    #     satellite_data = SatelliteCreate(
    #         international_code="2023-004A",
    #         name_satellite="Complete Test",
    #         norad_id=99996,
    #         launch_date=date.today(),
    #         country_id=1
    #     )
    #
    #     characteristics_data = SatelliteCharacteristicCreate(
    #         international_code=satellite_data.international_code,
    #         longitude=30.0,
    #         period=95.5,
    #         launch_site="Vostochny",
    #         rocket="Soyuz-2",
    #         launch_mass=2800.0,
    #         manufacturer="ISS Reshetnev",
    #         model="Complete Model",
    #         expected_lifetime=12,
    #         remaining_lifetime=8,
    #         details="Complete test satellite"
    #     )
    #
    #     response = await client.post(
    #         "/satellite/complete",
    #         json={
    #             "satellite_create": satellite_data.dict(),
    #             "satellite_characteristic": characteristics_data.dict()
    #         }
    #     )
    #     assert response.status_code == status.HTTP_200_OK
    #     complete_data = response.json()
    #
    #     # Проверяем, что данные спутника и характеристики верны
    #     assert complete_data["satellite"]["international_code"] == satellite_data.international_code
    #     assert complete_data["characteristics"]["rocket"] == characteristics_data.rocket
    #
    # async def test_get_satellite_list(self, client: AsyncClient):
    #     # Тест получения списка спутников
    #     # Создаем несколько спутников для теста
    #     for i in range(5):
    #         satellite_data = SatelliteCreate(
    #             international_code=f"2023-10{i}A",
    #             name_satellite=f"Test Satellite {i}",
    #             norad_id=90000 + i,
    #             launch_date=date.today(),
    #             country_id=1
    #         )
    #         await client.post("/satellite/", json=satellite_data.dict())
    #
    #     # Получаем список с пагинацией
    #     response = await client.get("/satellite/list/", params={"limit": 3, "offset": 1})
    #     assert response.status_code == status.HTTP_200_OK
    #     satellites = response.json()
    #
    #     # Проверяем пагинацию
    #     assert len(satellites) == 3
    #
    # async def test_update_satellite(self, client: AsyncClient):
    #     # Тест обновления данных спутника
    #     # Создаем спутник для обновления
    #     satellite_data = SatelliteCreate(
    #         international_code="2023-005A",
    #         name_satellite="Before Update",
    #         norad_id=99995,
    #         launch_date=date.today(),
    #         country_id=1
    #     )
    #     create_response = await client.post("/satellite/", json=satellite_data.dict())
    #     assert create_response.status_code == status.HTTP_200_OK
    #
    #     # Обновляем данные
    #     update_data = SatelliteUpdate(
    #         name_satellite="After Update",
    #         norad_id=88888,
    #         country_id=2
    #     )
    #
    #     update_response = await client.put(
    #         f"/satellite/{satellite_data.international_code}",
    #         json=update_data.dict()
    #     )
    #     assert update_response.status_code == status.HTTP_200_OK
    #     updated_satellite = update_response.json()
    #
    #     # Проверяем обновленные данные
    #     assert updated_satellite["name_satellite"] == update_data.name_satellite
    #     assert updated_satellite["norad_id"] == update_data.norad_id
    #     assert updated_satellite["country_id"] == update_data.country_id
    #
    # async def test_update_satellite_characteristics(self, client: AsyncClient):
    #     # Тест обновления характеристик спутника
    #     # Создаем спутник и характеристики
    #     satellite_data = SatelliteCreate(
    #         international_code="2023-006A",
    #         name_satellite="Char Update Test",
    #         norad_id=99994,
    #         launch_date=date.today(),
    #         country_id=1
    #     )
    #     await client.post("/satellite/", json=satellite_data.dict())
    #
    #     characteristics_data = SatelliteCharacteristicCreate(
    #         international_code=satellite_data.international_code,
    #         longitude=10.0,
    #         period=100.0,
    #         launch_site="Kourou",
    #         rocket="Ariane 5",
    #         manufacturer="Airbus",
    #         model="Old Model",
    #         expected_lifetime=10,
    #         remaining_lifetime=5
    #     )
    #     await client.post("/satellite/characteristic", json=characteristics_data.dict())
    #
    #     # Обновляем характеристики
    #     update_data = SatelliteCharacteristicUpdate(
    #         longitude=15.0,
    #         period=105.5,
    #         model="New Model",
    #         remaining_lifetime=4
    #     )
    #
    #     update_response = await client.put(
    #         f"/satellite/characteristic/{satellite_data.international_code}",
    #         json=update_data.dict()
    #     )
    #     assert update_response.status_code == status.HTTP_200_OK
    #     updated_chars = update_response.json()
    #
    #     # Проверяем обновленные данные
    #     assert updated_chars["longitude"] == update_data.longitude
    #     assert updated_chars["model"] == update_data.model
    #     # Проверяем, что неизмененные поля остались прежними
    #     assert updated_chars["rocket"] == characteristics_data.rocket
    #
    # async def test_delete_satellite(self, client: AsyncClient):
    #     # Тест удаления спутника
    #     # Создаем спутник для удаления
    #     satellite_data = SatelliteCreate(
    #         international_code="2023-007A",
    #         name_satellite="To Be Deleted",
    #         norad_id=99993,
    #         launch_date=date.today(),
    #         country_id=1
    #     )
    #     create_response = await client.post("/satellite/", json=satellite_data.dict())
    #     assert create_response.status_code == status.HTTP_200_OK
    #
    #     # Удаляем спутник
    #     delete_response = await client.delete(
    #         f"/satellite/{satellite_data.international_code}"
    #     )
    #     assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    #
    #     # Проверяем, что спутник больше не доступен
    #     get_response = await client.get(f"/satellite/{satellite_data.international_code}")
    #     assert get_response.status_code == status.HTTP_404_NOT_FOUND
    #
    # async def test_delete_satellite_characteristics(self, client: AsyncClient):
    #     # Тест удаления характеристик спутника
    #     # Создаем спутник и характеристики
    #     satellite_data = SatelliteCreate(
    #         international_code="2023-008A",
    #         name_satellite="Char Delete Test",
    #         norad_id=99992,
    #         launch_date=date.today(),
    #         country_id=1
    #     )
    #     await client.post("/satellite/", json=satellite_data.dict())
    #
    #     characteristics_data = SatelliteCharacteristicCreate(
    #         international_code=satellite_data.international_code,
    #         launch_site="Tanegashima",
    #         rocket="H-IIA",
    #         manufacturer="Mitsubishi",
    #         model="Delete Model",
    #         expected_lifetime=8,
    #         remaining_lifetime=3
    #     )
    #     await client.post("/satellite/characteristic", json=characteristics_data.dict())
    #
    #     # Удаляем характеристики
    #     delete_response = await client.delete(
    #         f"/satellite/characteristic/{satellite_data.international_code}"
    #     )
    #     assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    #
    #     # Проверяем, что характеристики больше не доступны
    #     get_response = await client.get(
    #         f"/satellite/{satellite_data.international_code}/characteristics"
    #     )
    #     assert get_response.status_code == status.HTTP_404_NOT_FOUND
    #
    # async def test_get_complete_satellite_info(self, client: AsyncClient):
    #     # Тест получения полной информации о спутнике
    #     # Создаем спутник с полной информацией
    #     satellite_data = SatelliteCreate(
    #         international_code="2023-009A",
    #         name_satellite="Complete Info Test",
    #         norad_id=99991,
    #         launch_date=date.today(),
    #         country_id=1
    #     )
    #
    #     characteristics_data = SatelliteCharacteristicCreate(
    #         international_code=satellite_data.international_code,
    #         longitude=25.5,
    #         period=92.3,
    #         launch_site="Satish Dhawan",
    #         rocket="PSLV",
    #         manufacturer="ISRO",
    #         model="Info Model",
    #         expected_lifetime=7,
    #         remaining_lifetime=2
    #     )
    #
    #     await client.post(
    #         "/satellite/complete",
    #         json={
    #             "satellite_create": satellite_data.dict(),
    #             "satellite_characteristic": characteristics_data.dict()
    #         }
    #     )
    #
    #     # Получаем полную информацию
    #     response = await client.get(
    #         f"/satellite/{satellite_data.international_code}/complete"
    #     )
    #     assert response.status_code == status.HTTP_200_OK
    #     complete_info = response.json()
    #
    #     # Проверяем, что данные совпадают
    #     assert complete_info["satellite"]["international_code"] == satellite_data.international_code
    #     assert complete_info["characteristics"]["rocket"] == characteristics_data.rocket

    @pytest.mark.asyncio
    async def test_delete_satellite(self):

        create_response = await self.client.get("/satellite/list/")
        assert create_response.status_code == status.HTTP_200_OK
        satellite_list = create_response.json()
        assert len(satellite_list) != 0

        for satellite in satellite_list:
            create_response = await self.client.delete(
                f"/satellite/{satellite.get("international_code")}"
            )
            assert create_response.status_code == status.HTTP_204_NO_CONTENT

        create_response = await self.client.get("/satellite/list/")
        assert create_response.status_code == status.HTTP_200_OK
        satellite_list = create_response.json()
        assert len(satellite_list) == 0


@pytest.mark.asyncio
async def test_delete_country(async_client):
    create_response = await async_client.get("/country/list/")
    assert create_response.status_code == 200
    country_list = create_response.json()
    assert len(country_list) == len(country_test_data)
    for country in country_list:
        country_id = country["id"]
        delete_response = await async_client.delete(f"/country/{country_id}")
        assert delete_response.status_code == 204
    create_response = await async_client.get("/country/list/")
    assert create_response.status_code == 200
    country_list = create_response.json()
    assert len(country_list) == 0
