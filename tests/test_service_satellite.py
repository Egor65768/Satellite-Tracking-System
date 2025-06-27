import pytest
from tests.test_data import (
    satellite_test_date,
    country_test_data,
    satellite_characteristic_test_date,
    satellite_characteristic_test_date_1,
)
from app.service import create_satellite_service, create_country_service
from app.schemas import (
    PaginationBase,
    CountryCreate,
    SatelliteCreate,
    SatelliteCharacteristicCreate,
    SatelliteUpdate,
    SatelliteCharacteristicUpdate,
)


class TestCreate:

    @pytest.mark.asyncio
    async def test_check_country_1(self, db_session):
        service = create_country_service(db_session)
        async with db_session.begin():
            assert len(await service.get_countries(PaginationBase())) == 0

    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data", country_test_data)
    async def test_create_country(self, db_session, country_data):
        service = create_country_service(db_session)
        async with db_session.begin():
            country = await service.create_country(CountryCreate(**country_data))
            assert country is not None

    @pytest.mark.asyncio
    async def test_check_country_2(self, db_session):
        service = create_country_service(db_session)
        async with db_session.begin():
            assert len(await service.get_countries(PaginationBase())) == 3

    @pytest.mark.asyncio
    @pytest.mark.parametrize("satellite_data", satellite_test_date)
    async def test_create_satellite(self, db_session, satellite_data):
        service = create_satellite_service(db_session)
        async with db_session.begin():
            satellite = await service.create_satellite_base(
                SatelliteCreate(**satellite_data)
            )
            assert satellite is not None
        async with db_session.begin():
            satellite = await service.get_satellite_by_id(
                satellite_data.get("international_code")
            )
            assert satellite is not None
            assert satellite.name_satellite == satellite_data.get("name_satellite")
            assert satellite.launch_date == satellite_data.get("launch_date")
            assert satellite.country_id == satellite_data.get("country_id")

    @pytest.mark.asyncio
    async def test_create_satellite_invalid(self, db_session):
        service = create_satellite_service(db_session)
        new_sat = satellite_test_date[0]
        async with db_session.begin():
            sat_len_list = len(await service.get_satellites(PaginationBase(limit=100)))
            assert not await service.create_satellite_base(SatelliteCreate(**new_sat))
        async with db_session.begin():
            assert (
                len(await service.get_satellites(PaginationBase(limit=100)))
                == sat_len_list
            )


class TestGetInvalid:
    @pytest.mark.asyncio
    async def test_get_satellite_invalid_1(self, db_session):
        service = create_satellite_service(db_session)
        async with db_session.begin():
            for satellite in satellite_test_date:
                characteristic = await service.get_satellite_characteristics(
                    satellite.get("international_code")
                )
                assert characteristic is None
                satellite_complete_info = await service.get_satellite_complete_info(
                    satellite.get("international_code")
                )
                assert satellite_complete_info is None

    @pytest.mark.asyncio
    async def test_get_satellite_invalid_2(self, db_session):
        service = create_satellite_service(db_session)
        int_code = "12" * 50
        async with db_session.begin():
            assert await service.get_satellite_characteristics(int_code) is None
            assert await service.get_satellite_by_id(int_code) is None


class TestCreateFull:
    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "satellite_characteristic_data", satellite_characteristic_test_date
    )
    async def test_create_satellite_characteristic(
        self, db_session, satellite_characteristic_data
    ):
        service = create_satellite_service(db_session)
        async with db_session.begin():
            assert await service.create_satellite_characteristic(
                SatelliteCharacteristicCreate(**satellite_characteristic_data)
            )
        async with db_session.begin():
            sat_data = await service.get_satellite_characteristics(
                satellite_characteristic_data.get("international_code")
            )
            assert sat_data is not None
            assert sat_data.launch_mass == satellite_characteristic_data.get(
                "launch_mass"
            )
            assert sat_data.period == satellite_characteristic_data.get("period")
            assert sat_data.manufacturer == satellite_characteristic_data.get(
                "manufacturer"
            )

            sat_data = await service.get_satellite_complete_info(
                satellite_characteristic_data.get("international_code")
            )

            assert sat_data is not None
            assert sat_data.name_satellite is not None
            assert sat_data.launch_mass == satellite_characteristic_data.get(
                "launch_mass"
            )
            assert sat_data.period == satellite_characteristic_data.get("period")
            assert sat_data.manufacturer == satellite_characteristic_data.get(
                "manufacturer"
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "satellite_characteristic_data", satellite_characteristic_test_date
    )
    async def test_delete_satellite_characteristic(
        self, db_session, satellite_characteristic_data
    ):
        service = create_satellite_service(db_session)
        international_code = satellite_characteristic_data.get("international_code")
        async with db_session.begin():
            assert await service.delete_characteristic(international_code)
        async with db_session.begin():
            assert await service.get_satellite_complete_info(international_code) is None
            assert (
                await service.get_satellite_characteristics(international_code) is None
            )
            assert await service.get_satellite_by_id(international_code) is not None
            assert await service.delete_satellite(international_code)
        async with db_session.begin():
            assert await service.get_satellite_by_id(international_code) is None

    @pytest.mark.asyncio
    async def test_create_satellite_complete(self, db_session):
        service = create_satellite_service(db_session)
        for satellite_date, satellite_characteristic in zip(
            satellite_test_date, satellite_characteristic_test_date
        ):
            international_code = satellite_date.get("international_code")
            async with db_session.begin():
                assert await service.create_full_satellite(
                    SatelliteCreate(**satellite_date),
                    SatelliteCharacteristicCreate(**satellite_characteristic),
                )
            async with db_session.begin():
                assert await service.get_satellite_by_id(international_code) is not None
                assert (
                    await service.get_satellite_characteristics(international_code)
                    is not None
                )
                assert (
                    await service.get_satellite_complete_info(international_code)
                    is not None
                )

    @pytest.mark.asyncio
    async def test_create_satellite_complete_invalid(self, db_session):
        service = create_satellite_service(db_session)
        sat_char = satellite_characteristic_test_date[1]
        international_code = satellite_characteristic_test_date_1.get(
            "international_code"
        )
        async with db_session.begin():
            assert (
                await service.create_satellite_characteristic(
                    SatelliteCharacteristicCreate(
                        **satellite_characteristic_test_date_1
                    )
                )
                is None
            )
        async with db_session.begin():
            sat_data = await service.get_satellite_complete_info(international_code)
            assert sat_data is not None
            assert sat_data.launch_mass == sat_char.get("launch_mass")
            assert sat_data.model == sat_char.get("model")


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_satellite_1(self, db_session):
        service = create_satellite_service(db_session)
        satellite_1 = satellite_test_date[0]
        international_code_1 = satellite_1.get("international_code")
        async with db_session.begin():
            sat_1 = await service.get_satellite_by_id(international_code_1)
            assert sat_1
            assert sat_1.name_satellite == satellite_1.get("name_satellite")
            assert sat_1.norad_id == satellite_1.get("norad_id")
            update_data = {"name_satellite": "Viking 1"}
            assert await service.update_satellite(
                international_code_1, SatelliteUpdate(**update_data)
            )
        async with db_session.begin():
            sat_1 = await service.get_satellite_by_id(international_code_1)
            assert sat_1
            assert sat_1.name_satellite == update_data.get("name_satellite")
            assert sat_1.norad_id == satellite_1.get("norad_id")

        async with db_session.begin():
            international_code_2 = satellite_test_date[1].get("international_code")
            assert not await service.update_satellite(
                international_code_2, SatelliteUpdate(**update_data)
            )

        async with db_session.begin():
            sat_1 = await service.get_satellite_by_id(international_code_1)
            assert sat_1
            assert sat_1.name_satellite == update_data.get("name_satellite")
            assert sat_1.norad_id == satellite_1.get("norad_id")

            sat_2 = await service.get_satellite_by_id(international_code_2)
            assert sat_2
            assert sat_2.name_satellite == satellite_test_date[1].get("name_satellite")

    @pytest.mark.asyncio
    async def test_update_satellite_2(self, db_session):
        service = create_satellite_service(db_session)
        sat_char = satellite_characteristic_test_date[0]
        international_code = sat_char.get("international_code")
        async with db_session.begin():
            sat_char_db = await service.get_satellite_characteristics(
                international_code
            )
            assert sat_char_db
            assert sat_char_db.manufacturer == sat_char.get("manufacturer")
            assert sat_char_db.model == sat_char.get("model")
            update_data = {"model": "1hh3i1 c1xdsgb f"}
            assert await service.update_satellite_characteristic(
                international_code, SatelliteCharacteristicUpdate(**update_data)
            )
        async with db_session.begin():
            sat_char_db = await service.get_satellite_characteristics(
                international_code
            )
            assert sat_char_db
            assert sat_char_db.manufacturer == sat_char.get("manufacturer")
            assert sat_char_db.model == update_data.get("model")


class TestDelete:
    @pytest.mark.asyncio
    async def test_check_country_count_satellite(self, db_session):
        service = create_country_service(db_session)
        async with db_session.begin():
            assert len(await service.get_satellites_by_country_id(2)) == 2

    @pytest.mark.asyncio
    async def test_check_satellite_1(self, db_session):
        service = create_satellite_service(db_session)
        async with db_session.begin():
            assert len(await service.get_satellites(PaginationBase())) != 0

    @pytest.mark.asyncio
    async def test_delete_satellite(self, db_session):
        service = create_satellite_service(db_session)
        async with db_session.begin():
            sat_list = await service.get_satellites(PaginationBase(limit=100))
        for sat in sat_list:
            async with db_session.begin():
                assert await service.delete_satellite(sat.international_code)

    @pytest.mark.asyncio
    async def test_check_satellite_2(self, db_session):
        service = create_satellite_service(db_session)
        async with db_session.begin():
            assert len(await service.get_satellites(PaginationBase())) == 0
            assert (
                len(await service.get_satellites_characteristics_list(PaginationBase()))
                == 0
            )

    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data", country_test_data)
    async def test_delete_country(self, db_session, country_data):
        service = create_country_service(db_session)
        async with db_session.begin():
            country_abbreviation = country_data.get("abbreviation")
            country = await service.get_by_abbreviation(country_abbreviation)
            assert country is not None
            assert await service.delete_country(country.id)

    @pytest.mark.asyncio
    async def test_check_country_3(self, db_session):
        service = create_country_service(db_session)
        async with db_session.begin():
            assert len(await service.get_countries(PaginationBase())) == 0
