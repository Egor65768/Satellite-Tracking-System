import pytest
from fastapi import status
from datetime import date
from app.schemas import SatelliteCreate, SatelliteCharacteristicCreate
from tests.test_data import (
    country_test_data,
    satellite_test_date,
    satellite_characteristic_test_date,
    headers_auth,
)
from copy import copy


@pytest.mark.asyncio
async def test_check_count_country_1(async_client):
    assert len((await async_client.get("/country/list/")).json()) == 0


@pytest.mark.asyncio
@pytest.mark.parametrize("country_data", country_test_data)
async def test_create_and_get_country_by_id(country_data, async_client):
    create_response = await async_client.post(
        "/country/", json=country_data, headers=headers_auth
    )
    assert create_response.status_code == 200


@pytest.mark.asyncio
async def test_check_count_country_2(async_client):
    assert len((await async_client.get("/country/list/")).json()) == 3


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

        # Получаем созданный спутник
        get_response = await self.client.get(
            f"/satellite/{satellite_data.get("international_code")}"
        )
        satellite = get_response.json()

        assert get_response.status_code == status.HTTP_200_OK

        # Проверяем соответствие данных
        assert satellite["international_code"] == satellite_data.get(
            "international_code"
        )
        assert satellite["name_satellite"] == satellite_data.get("name_satellite")

        response = await self.client.get(
            f"/satellite/{satellite_data.get("international_code")}"
        )
        assert response.status_code == status.HTTP_200_OK
        sat_dat = response.json()
        assert sat_dat["name_satellite"] == satellite_data["name_satellite"]
        assert sat_dat["international_code"] == satellite_data["international_code"]

    @pytest.mark.asyncio
    async def test_invalid_get_satellite(self):
        international_code = "NOOOO"
        response = await self.client.get(
            f"/satellite/{international_code}/characteristic"
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_nonexistent_satellite(self):
        # Тест получения несуществующего спутника
        response = await self.client.get("/satellite/NONEXISTENT-CODE")
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_satellite_duplicate(self):
        # Тест создания дубликата спутника
        satellite_data = copy(satellite_test_date[1])
        satellite_data["launch_date"] = satellite_data["launch_date"].isoformat()

        # Первое создание - должно быть успешным
        response1 = await self.client.post("/satellite/", json=satellite_data)
        assert response1.status_code == status.HTTP_200_OK

        # Второе создание с теми же данными - должно вернуть ошибку

        response2 = await self.client.post("/satellite/", json=satellite_data)
        assert response2.status_code == status.HTTP_409_CONFLICT

    @pytest.mark.asyncio
    async def test_create_and_get_satellite_characteristics(self):
        # Тест создания и получения характеристик спутника
        # Сначала создаем спутник
        satellite_data = SatelliteCreate(
            international_code="2023-004A",
            name_satellite="Test With Characteristics",
            norad_id=99997,
            launch_date=date.today(),
            country_id=1,
        )
        satellite_data_dict = satellite_data.model_dump()
        satellite_data_dict["launch_date"] = satellite_data_dict[
            "launch_date"
        ].isoformat()
        satellite_response = await self.client.post(
            "/satellite/", json=satellite_data_dict
        )
        assert satellite_response.status_code == status.HTTP_200_OK

        # Создаем характеристики
        characteristics_data = SatelliteCharacteristicCreate(
            international_code=satellite_data.international_code,
            longitude=45.0,
            period=90.5,
            launch_site="Baikonur",
            rocket="Proton-M",
            launch_mass=3500.5,
            manufacturer="RSC Energia",
            model="Test Model",
            expected_lifetime=15,
            remaining_lifetime=10,
            details="Test satellite characteristics",
        )
        characteristics_data_dict = characteristics_data.model_dump()
        char_response = await self.client.post(
            "/satellite/characteristic", json=characteristics_data_dict
        )
        assert char_response.status_code == status.HTTP_200_OK

        # Получаем характеристики
        get_response = await self.client.get(
            f"/satellite/{satellite_data.international_code}/characteristics"
        )
        assert get_response.status_code == status.HTTP_200_OK
        characteristics = get_response.json()

        # Проверяем данные
        assert characteristics["longitude"] == characteristics_data.longitude
        assert characteristics["rocket"] == characteristics_data.rocket

    @pytest.mark.asyncio
    async def test_create_complete_satellite(self):
        # Тест создания спутника с полной информацией
        satellite_data = SatelliteCreate(
            international_code="2023-008A",
            name_satellite="Complete Test",
            norad_id=99996,
            launch_date=date.today(),
            country_id=1,
        )
        satellite_data_dict = satellite_data.model_dump()
        satellite_data_dict["launch_date"] = satellite_data_dict[
            "launch_date"
        ].isoformat()

        characteristics_data = SatelliteCharacteristicCreate(
            international_code=satellite_data.international_code,
            longitude=30.0,
            period=95.5,
            launch_site="Vostochny",
            rocket="Soyuz-2",
            launch_mass=2800.0,
            manufacturer="ISS Reshetnev",
            model="Complete Model",
            expected_lifetime=12,
            remaining_lifetime=8,
            details="Complete test satellite",
        )

        response = await self.client.post(
            "/satellite/complete",
            json={
                "satellite_create": satellite_data_dict,
                "satellite_characteristic": characteristics_data.model_dump(),
            },
        )
        assert response.status_code == status.HTTP_200_OK
        complete_data = response.json()

        # Проверяем, что данные спутника и характеристики верны
        assert complete_data["international_code"] == satellite_data.international_code
        assert complete_data["rocket"] == characteristics_data.rocket

    @pytest.mark.asyncio
    async def test_get_satellite_list(self):
        # Тест получения списка спутников

        # Получаем список с пагинацией
        response = await self.client.get(
            "/satellite/list/", params={"limit": 3, "offset": 1}
        )
        assert response.status_code == status.HTTP_200_OK
        satellites = response.json()

        # Проверяем пагинацию
        assert len(satellites) == 3

    @pytest.mark.asyncio
    async def test_get_satellite_list_2(self):
        # Тест получения списка спутников

        # Получаем список с пагинацией
        response = await self.client.get(
            "/satellite/list/", params={"limit": 4, "offset": 2}
        )
        assert response.status_code == status.HTTP_200_OK
        satellites = response.json()

        # Проверяем пагинацию
        assert len(satellites) == 2

        # Получаем список с пагинацией
        response = await self.client.get(
            "/satellite/list/", params={"limit": 4, "offset": 4}
        )
        assert response.status_code == status.HTTP_200_OK
        satellites = response.json()

        # Проверяем пагинацию
        assert len(satellites) == 0

    @pytest.mark.asyncio
    async def test_update_satellite(self):
        # Тест обновления данных спутника
        # Создаем спутник для обновления
        satellite_data = SatelliteCreate(
            international_code="2025-011A",
            name_satellite="Before Update",
            norad_id=99995,
            launch_date=date.today(),
            country_id=2,
        )
        satellite_data_dict = satellite_data.model_dump()
        satellite_data_dict["launch_date"] = satellite_data_dict[
            "launch_date"
        ].isoformat()
        create_response = await self.client.post(
            "/satellite/", json=satellite_data_dict
        )
        assert create_response.status_code == status.HTTP_200_OK

        update_data_dict = {
            "name_satellite": "After Update",
            "norad_id": 88888,
        }

        update_response = await self.client.put(
            f"/satellite/{satellite_data.international_code}", json=update_data_dict
        )
        assert update_response.status_code == status.HTTP_200_OK
        updated_satellite = update_response.json()

        # Проверяем обновленные данные
        assert updated_satellite["name_satellite"] == update_data_dict["name_satellite"]
        assert updated_satellite["norad_id"] == update_data_dict["norad_id"]
        assert updated_satellite["country_id"] == satellite_data.country_id

        response = await self.client.get(
            f"/satellite/{satellite_data.international_code}"
        )
        assert response.status_code == status.HTTP_200_OK
        satellite_update_data = response.json()
        assert (
            satellite_update_data["name_satellite"]
            == update_data_dict["name_satellite"]
        )
        assert satellite_update_data["norad_id"] == update_data_dict["norad_id"]
        assert satellite_update_data["country_id"] == satellite_data.country_id

    @pytest.mark.asyncio
    async def test_update_satellite_characteristics(self):

        # Тест обновления характеристик спутника
        international_code = satellite_test_date[1].get("international_code")
        response = await self.client.get(f"/satellite/{international_code}/complete")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        # Добавление характеристик для спутника
        satellite_test_characteristic = satellite_characteristic_test_date[1]
        response = await self.client.post(
            f"/satellite/characteristic", json=satellite_test_characteristic
        )
        assert response.status_code == status.HTTP_200_OK

        response = await self.client.get(f"/satellite/{international_code}/complete")
        assert response.status_code == status.HTTP_200_OK
        satellite_data = response.json()

        # Проверяем что данные в базе совпадают с нашими тестовыми данными
        assert satellite_data["longitude"] == satellite_test_characteristic.get(
            "longitude"
        )
        assert satellite_data["model"] == satellite_test_characteristic.get("model")
        assert satellite_data["rocket"] == satellite_test_characteristic.get("rocket")
        assert satellite_data["period"] == satellite_test_characteristic.get("period")
        assert satellite_data[
            "remaining_lifetime"
        ] == satellite_test_characteristic.get("remaining_lifetime")

        # Обновляем характеристики
        update_data = {
            "longitude": 52.0,
            "period": 152.23,
            "model": "New Model",
            "remaining_lifetime": 2,
        }

        update_response = await self.client.put(
            f"/satellite/characteristic/{satellite_data.get("international_code")}",
            json=update_data,
        )
        assert update_response.status_code == status.HTTP_200_OK

        # Проверяем обновленные данные
        response = await self.client.get(f"/satellite/{international_code}/complete")
        assert response.status_code == status.HTTP_200_OK
        satellite_data = response.json()

        assert satellite_data["longitude"] == update_data.get("longitude")
        assert satellite_data["model"] == update_data.get("model")
        assert satellite_data["period"] == update_data.get("period")
        assert satellite_data["remaining_lifetime"] == update_data.get(
            "remaining_lifetime"
        )

        # Проверяем что старые данные остались без изменений
        assert satellite_data["rocket"] == satellite_test_characteristic.get("rocket")

    @pytest.mark.asyncio
    async def test_get_satellite_list_by_country_id(self):
        create_response = await self.client.get("country/id/1/satellite")
        assert create_response.status_code == status.HTTP_200_OK
        satellite_list = create_response.json()
        assert len(satellite_list) != 0

        create_response = await self.client.get("country/id/2/satellite")
        assert create_response.status_code == status.HTTP_200_OK
        satellite_list = create_response.json()
        assert len(satellite_list) != 0

        create_response = await self.client.get("country/id/3")
        assert create_response.status_code == status.HTTP_200_OK

        create_response = await self.client.get("country/id/3/satellite")
        assert create_response.status_code == status.HTTP_200_OK
        satellite_list = create_response.json()
        assert len(satellite_list) == 0

        create_response = await self.client.get("country/id/4234/satellite")
        assert create_response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_country_invalid(self):
        response = await self.client.get("/satellite/list/")
        assert response.status_code == status.HTTP_200_OK
        sat = response.json()
        sat_county_id = sat[0].get("country_id")

        delete_response = await self.client.delete(
            f"/country/{sat_county_id}", headers=headers_auth
        )
        assert delete_response.status_code == status.HTTP_409_CONFLICT

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
