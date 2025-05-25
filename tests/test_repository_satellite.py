from typing import Optional

import pytest
from app.db import (
    SatelliteRepository,
    SatelliteCharacteristicRepository,
    CountryRepository,
)
from app.schemas import (
    Object_ID,
    Object_str_ID,
    CountryCreate,
    PaginationBase,
    CountryInDB,
    SatelliteCreate,
    SatelliteCharacteristicCreate,
    CountryFind,
    SatelliteUpdate,
    SatelliteCharacteristicUpdate,
)

from tests.test_data import satellite_test_date, satellite_characteristic_test_date

satellite_complete_data = [
    (sat_data, sat_characteristic)
    for sat_data, sat_characteristic in zip(
        satellite_test_date, satellite_characteristic_test_date
    )
]


class TestCreate:
    @pytest.mark.asyncio
    async def test_create_country(self, db_session):
        country_repo = CountryRepository(db_session)
        country_data = {"abbreviation": "FA", "full_name": "Франция"}
        async with db_session.begin():
            assert len(await country_repo.get_models(PaginationBase())) == 0
            assert await country_repo.create_entity(CountryCreate(**country_data))
            assert len(await country_repo.get_models(PaginationBase())) == 1
            country_db = await country_repo.get_by_abbreviation(
                CountryFind(abbreviation="FA")
            )
            country_id = country_db.id
            country: Optional[CountryInDB] = await country_repo.get_as_model(
                Object_ID(id=country_db.id)
            )
            assert country.abbreviation == country_data["abbreviation"]
        for i in range(len(satellite_test_date)):
            satellite_test_date[i]["country_id"] = country_id

    @pytest.mark.asyncio
    @pytest.mark.parametrize("satellite_date", satellite_test_date)
    async def test_create_satellite(self, db_session, satellite_date):
        repo = SatelliteRepository(db_session)
        async with db_session.begin():
            assert await repo.create_entity(SatelliteCreate(**satellite_date))

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "satellite_characteristic", satellite_characteristic_test_date
    )
    async def test_create_characteristic_satellite(
        self, db_session, satellite_characteristic
    ):
        repo = SatelliteCharacteristicRepository(db_session)
        async with db_session.begin():
            assert await repo.create_entity(
                SatelliteCharacteristicCreate(**satellite_characteristic)
            )


class TestGet:
    @pytest.mark.asyncio
    async def test_get_satellite(self, db_session):
        repo_sat = SatelliteRepository(db_session)
        repo_characteristic = SatelliteCharacteristicRepository(db_session)
        async with db_session.begin():
            assert len(await repo_sat.get_models(PaginationBase())) == 2
            assert len(await repo_characteristic.get_models(PaginationBase())) == 2

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "satellite_date, satellite_characteristic", satellite_complete_data
    )
    async def test_get_satellite_complete_info(
        self, db_session, satellite_date: dict, satellite_characteristic: dict
    ):
        repo_sat = SatelliteRepository(db_session)
        async with db_session.begin():
            int_code = Object_str_ID(id=satellite_date["international_code"])
            sat_db_date = await repo_sat.get_complete_info(int_code)
            dict_sat_data = sat_db_date.model_dump()
            for key, value in dict_sat_data.items():
                test_value = (
                    satellite_date.get(key)
                    if satellite_date.get(key) is not None
                    else satellite_characteristic.get(key)
                )
                assert test_value == value

    @pytest.mark.asyncio
    async def test_get_satellite_from_country(self, db_session):
        country_repo = CountryRepository(db_session)
        async with db_session.begin():
            country_db = await country_repo.get_by_abbreviation(
                CountryFind(abbreviation="FA")
            )
            country_id = country_db.id
            sat_list = await country_repo.get_satellite_list(Object_ID(id=country_id))
            assert len(sat_list) == 2
            for satellite in sat_list:
                assert satellite.international_code in ["123_A_123_A", "321_B_123_A"]
                assert satellite.country_id == country_db.id
        async with db_session.begin():
            sat_list = await country_repo.get_satellite_list(Object_ID(id=312434))
            assert sat_list is None


class TestDelete:

    @pytest.mark.asyncio
    async def test_delete_1(self, db_session):
        repo_sat = SatelliteRepository(db_session)
        async with db_session.begin():
            sat_id = Object_str_ID(id="123_A_123_A")
            assert len(await repo_sat.get_models(PaginationBase())) == 2
            assert await repo_sat.delete_model(sat_id)
            assert len(await repo_sat.get_models(PaginationBase())) == 1
            sat_id = Object_str_ID(id="123_A_123_B")
            assert not await repo_sat.delete_model(sat_id)
            assert len(await repo_sat.get_models(PaginationBase())) == 1
            sat_id = Object_str_ID(id="321_B_123_A")
            assert await repo_sat.delete_model(sat_id)
            assert len(await repo_sat.get_models(PaginationBase())) == 0


class TestCreateComplete:
    @pytest.mark.asyncio
    async def test_create_complete_satellite_2(self, db_session):
        repo_sat = SatelliteRepository(db_session)
        repo_sat_char = SatelliteCharacteristicRepository(db_session)
        async with db_session.begin():
            satellite_data = SatelliteCreate(**satellite_test_date[0])
            satellite_characteristic = SatelliteCharacteristicCreate(
                **satellite_characteristic_test_date[0]
            )
            assert await repo_sat.create_satellite(
                satellite_data, satellite_characteristic
            )
            sat_list = await repo_sat.get_models(PaginationBase())
            assert len(sat_list) == 1
            assert sat_list[0].international_code == "123_A_123_A"
            sat_char_list = await repo_sat_char.get_models(PaginationBase())
            assert len(sat_char_list) == 1
            assert sat_char_list[0].international_code == "123_A_123_A"
            int_code = Object_str_ID(id="123_A_123_A")
            satellite_info = await repo_sat.get_complete_info(int_code)
            assert satellite_info is not None
            assert satellite_info.international_code == "123_A_123_A"
            assert satellite_info.launch_mass == satellite_characteristic.launch_mass
            assert satellite_info.norad_id == satellite_data.norad_id


class TestUpdate:

    @pytest.mark.asyncio
    async def test_update_satellite(self, db_session):
        repo_sat = SatelliteRepository(db_session)
        international_code = "123_A_123_A"
        sat_data = satellite_test_date[0]
        async with db_session.begin():
            object_id = Object_str_ID(id=international_code)
            sat = await repo_sat.get_by_field(
                field_name="international_code", field_value="123_A_123_A"
            )
            assert sat is not None
            assert sat.name_satellite == sat_data.get("name_satellite")
            assert sat.norad_id == sat_data.get("norad_id")
            assert sat.launch_date == sat_data.get("launch_date")
            update_data = {"norad_id": 1234, "name_satellite": "test_name"}
            assert await repo_sat.update_satellite(
                object_id=object_id, update_satellite=SatelliteUpdate(**update_data)
            )
            sat = await repo_sat.get_by_field(
                field_name="international_code", field_value="123_A_123_A"
            )
            assert sat.name_satellite == update_data.get("name_satellite")
            assert sat.norad_id == update_data.get("norad_id")
            assert sat.launch_date == sat_data.get("launch_date")
            object_id = Object_str_ID(id="PAMPAM")
            assert not await repo_sat.update_satellite(
                object_id=object_id, update_satellite=SatelliteUpdate(**update_data)
            )
            update_data = {"norad_id": satellite_test_date[1].get("norad_id")}
            assert not await repo_sat.update_satellite(
                object_id=object_id, update_satellite=SatelliteUpdate(**update_data)
            )
        async with db_session.begin():
            sat = await repo_sat.get_by_field(
                field_name="international_code", field_value="123_A_123_A"
            )
            assert sat.norad_id == 1234

    @pytest.mark.asyncio
    async def test_update_satellite_characteristic(self, db_session):
        repo_sat_char = SatelliteCharacteristicRepository(db_session)
        international_code = "123_A_123_A"
        object_id = Object_str_ID(id=international_code)
        sat_data = satellite_characteristic_test_date[0]
        async with db_session.begin():
            sat_characteristic = await repo_sat_char.get_by_field(
                field_name="international_code", field_value="123_A_123_A"
            )
            assert sat_characteristic
            assert sat_characteristic.international_code == international_code
            assert sat_characteristic.launch_site == sat_data.get("launch_site")
            assert sat_characteristic.manufacturer == sat_data.get("manufacturer")
            update_data = {"manufacturer": "New_manufacturer"}
            assert await repo_sat_char.update_characteristic_satellite(
                object_id, SatelliteCharacteristicUpdate(**update_data)
            )

            sat_characteristic = await repo_sat_char.get_by_field(
                field_name="international_code", field_value="123_A_123_A"
            )
            assert sat_characteristic
            assert sat_characteristic.international_code == international_code
            assert sat_characteristic.launch_site == sat_data.get("launch_site")
            assert sat_characteristic.manufacturer != sat_data.get("manufacturer")
            assert sat_characteristic.manufacturer == update_data.get("manufacturer")


@pytest.mark.asyncio
async def test_delete_satellite(db_session):
    repo = SatelliteRepository(db_session)
    async with db_session.begin():
        satellite_list = await repo.get_models(PaginationBase())
        assert len(satellite_list) != 0
        for satellite in satellite_list:
            assert await repo.delete_model(
                Object_str_ID(id=satellite.international_code)
            )
        assert len(await repo.get_models(PaginationBase())) == 0
    repo = SatelliteCharacteristicRepository(db_session)
    async with db_session.begin():
        assert len(await repo.get_models(PaginationBase())) == 0


@pytest.mark.asyncio
async def test_delete_country(db_session):
    repo = CountryRepository(db_session)
    async with db_session.begin():
        country_list = await repo.get_models(PaginationBase())
        assert len(country_list) != 0
        for country in country_list:
            assert len(await repo.get_satellite_list(Object_ID(id=country.id))) == 0
            assert await repo.delete_model(Object_ID(id=country.id))
        assert len(await repo.get_models(PaginationBase())) == 0
