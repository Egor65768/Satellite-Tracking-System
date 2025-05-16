import pytest
from app.tests.test_data import (
    country_test_data,
    country_test_get,
    country_test_data_invalid,
    country_update_test_data,
)
from app.service import CountryService
from app.db import CountryRepository
from app.schemas import (
    CountryUpdate,
    CountryInDB,
    CountryCreate,
    CountryFind,
    Object_ID,
    PaginationBase,
)


class TestCreate:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data", country_test_data)
    async def test_create_country(self, db_session, country_data):
        async with db_session.begin():
            repo = CountryRepository(db_session)
            country_service = CountryService(repo)
            country = await country_service.create_country(
                CountryCreate(**country_data)
            )
            assert country is not None
            assert country.abbreviation == country_data["abbreviation"]
            assert country.full_name == country_data["full_name"]
            assert country.id == country_data["id"]

    @pytest.mark.asyncio
    async def test_create_country_invalid_1(self, db_session):
        repo = CountryRepository(db_session)
        country_service = CountryService(repo)
        country_data = country_test_data[0]
        async with db_session.begin():
            country = await country_service.create_country(
                CountryCreate(**country_data)
            )
            assert country is None

        async with db_session.begin():
            assert len(await country_service.get_countries(PaginationBase())) == 3

    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data,isNone", country_test_data_invalid)
    async def test_create_country_invalid_2(self, db_session, country_data, isNone):
        repo = CountryRepository(db_session)
        country_service = CountryService(repo)
        async with db_session.begin():
            country = await country_service.create_country(
                CountryCreate(**country_data)
            )
            if not isNone:
                assert country is not None
                assert country.abbreviation == country_data["abbreviation"]
            else:
                assert country is None


class TestUpdate:
    @pytest.mark.asyncio
    async def test_update_country_1(self, db_session):
        repo = CountryRepository(db_session)
        country_service = CountryService(repo)
        country_data = country_test_data[0]
        country_id = Object_ID(id=country_data.get("id"))
        update_data = {"abbreviation": "UA"}
        async with db_session.begin():
            country = await country_service.update_country(
                country_id, CountryUpdate(**update_data)
            )
            assert country is not None
            assert country.abbreviation == "UA"
            assert country.id == 1
            assert country.full_name == country_data.get("full_name")

            update_data = {"full_name": "Никорагуа"}
            await country_service.update_country(
                country_id, CountryUpdate(**update_data)
            )
            country = await country_service.get_by_abbreviation(
                CountryFind(abbreviation="UA")
            )
            assert country is not None
            assert country.abbreviation == "UA"
            assert country.id == 1
            assert country.full_name == "Никорагуа"

    @pytest.mark.asyncio
    async def test_update_invalid_1(self, db_session):
        repo = CountryRepository(db_session)
        country_service = CountryService(repo)
        country_data = country_test_data[0]
        country_id = Object_ID(id=country_data.get("id"))
        update_data = {"full_name": country_test_data[1].get("full_name")}
        async with db_session.begin():
            country = await country_service.update_country(
                country_id, CountryUpdate(**update_data)
            )
            assert country is None
        async with db_session.begin():
            country = await country_service.get_by_abbreviation(
                CountryFind(abbreviation="UA")
            )
            assert country is not None
            assert country.abbreviation == "UA"


class TestDelete:
    @pytest.mark.asyncio
    async def test_delete(self, db_session):
        repo = CountryRepository(db_session)
        country_service = CountryService(repo)
        async with db_session.begin():
            country_id = Object_ID(id=52)
            assert not await country_service.delete_country(country_id)
        async with db_session.begin():
            country_list = await country_service.get_countries(PaginationBase())
            assert len(country_list) == 5
            for country in country_list:
                assert await country_service.delete_country(Object_ID(id=country.id))
            country_list = await country_service.get_countries(PaginationBase())
            assert len(country_list) == 0
