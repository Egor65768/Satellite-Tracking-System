from typing import Optional, List

import pytest
from app.db import (
    SatelliteRepository,
    SatelliteCharacteristicRepository,
    CountryRepository,
)
from datetime import date
from app.schemas import (
    Object_ID,
    Object_str_ID,
    CountryCreate,
    PaginationBase,
    CountryInDB,
    SatelliteCreate,
    SatelliteCharacteristicCreate,
    SatelliteCompleteInfo,
    CountryFind,
)
from app.db.models import Satellite, SatelliteCharacteristic

satellite_test_date = [
    {
        "international_code": "123_A_123_A",
        "name_satellite": "Yaml-5012",
        "norad_id": 318420,
        "launch_date": date(2012, 1, 7),
        "country_id": 4,
    },
    {
        "international_code": "321_B_123_A",
        "name_satellite": "Yaml-5011",
        "norad_id": 318421,
        "launch_date": date(1999, 12, 7),
        "country_id": 4,
    },
]
satellite_characteristic_test_date = [
    {
        "international_code": "123_A_123_A",
        "longitude": 112.1,
        "period": 1311.2,
        "launch_site": "Cape Canaveral",
        "rocket": "Falcon 9",
        "launch_mass": 100097.9,
        "manufacturer": "Spacex",
        "model": "dj3rw534",
        "expected_lifetime": 16,
        "remaining_lifetime": 3,
        "details": "Ra sdk qhl chl cnelnlanljb jcbekj bkjbcb",
    },
    {
        "international_code": "321_B_123_A",
        "longitude": 171.1,
        "period": 1731.1,
        "launch_site": "Cape Canaveral",
        "rocket": "Falcon 9",
        "launch_mass": 123847.9,
        "manufacturer": "Spacex",
        "model": "dj3ij3334",
        "expected_lifetime": 20,
        "remaining_lifetime": 5,
        "details": "nfhehdlhvefoihouefhouhofd",
    },
]
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
            assert await country_repo.create_entity(CountryCreate(**country_data))
            assert len(await country_repo.get_models(PaginationBase())) == 3
            country_db = await country_repo.get_by_abbreviation(
                CountryFind(abbreviation="FA")
            )
            country: Optional[CountryInDB] = await country_repo.get_as_model(
                Object_ID(id=country_db.id)
            )
            assert country.abbreviation == country_data["abbreviation"]

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
            sat_db_date: Optional[SatelliteCompleteInfo] = (
                await repo_sat.get_complete_info(int_code)
            )
            dict_sat_data = sat_db_date.model_dump()
            for key, value in dict_sat_data.items():
                test_value = (
                    satellite_date.get(key)
                    if satellite_date.get(key) is not None
                    else satellite_characteristic.get(key)
                )
                assert test_value == value


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
