import pytest
from app.db import CountryRepository
from app.schemas import (
    CountryCreate,
    Object_ID,
    PaginationBase,
    CountryFind,
    CountryUpdate,
)
from sqlalchemy.exc import InvalidRequestError

country_test_data = [
    {"abbreviation": "CA", "full_name": "Канада", "id": 1},
    {"abbreviation": "US", "full_name": "США", "id": 2},
    {"abbreviation": "RU", "full_name": "Россия", "id": 3},
]

country_test_data_invalid = [
    ({"abbreviation": "NOR", "full_name": "Норвегия", "id": 4}, False),
    ({"abbreviation": "NO", "full_name": "Англия", "id": 1}, True),
    ({"abbreviation": "NOR", "full_name": "Англия", "id": 5}, True),
    ({"abbreviation": "NOR", "full_name": "Норвегия", "id": 5}, True),
    ({"abbreviation": "ISR", "full_name": "Израиль", "id": 5}, False),
]

country_test_get = [
    ({"abbreviation": "CA", "full_name": "Канада", "id": 1}, True),
    ({"abbreviation": "US", "full_name": "США", "id": 2}, True),
    ({"abbreviation": "RU", "full_name": "Россия", "id": 3}, True),
    ({"id": 10}, False),
    ({"id": 6}, False),
    ({"abbreviation": "NOR", "full_name": "Норвегия", "id": 4}, True),
    ({"abbreviation": "ISR", "full_name": "Израиль", "id": 5}, True),
]

country_update_test_data = [
    ({"abbreviation": "CAC"}, 1, False),
    ({"abbreviation": "CC", "full_name": "Англия"}, 2, False),
    ({"abbreviation": "CA", "full_name": "США"}, 101, True),
    ({"abbreviation": "CA", "full_name": "ENNNNN"}, 3, False),
    ({"abbreviation": "CA", "full_name": "Ftd"}, 4, True),
    ({"abbreviation": "KSJSL", "full_name": "ENNNNN"}, 4, True),
]


class TestCreate:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data", country_test_data)
    async def test_create_country(self, db_session, country_data):
        async with db_session.begin():
            repo = CountryRepository(db_session)
            country = await repo.create_entity(CountryCreate(**country_data))
            assert country is not None
            assert country.abbreviation == country_data["abbreviation"]
            assert country.full_name == country_data["full_name"]
            assert country.id is not None
            assert country.id == country_data["id"]

    @pytest.mark.asyncio
    async def test_create_country_invalid_1(self, db_session):
        test_country = {"abbreviation": "SAS", "full_name": "Сьера-Леоне", "id": 52}
        country_id = Object_ID(id=test_country["id"])
        repo = CountryRepository(db_session)
        async with db_session.begin():
            await repo.create_entity(CountryCreate(**test_country))
            country = await repo.get_as_model(country_id)
            assert country.abbreviation == test_country["abbreviation"]
            assert country.full_name == test_country["full_name"]
            assert country.id == test_country["id"]
        async with db_session.begin():
            new_country = await repo.create_entity(CountryCreate(**test_country))
            assert new_country is None
            with pytest.raises(InvalidRequestError):
                await db_session.commit()
        async with db_session.begin():
            country = await repo.get_as_model(country_id)
            assert country.abbreviation == test_country["abbreviation"]
            assert country.full_name == test_country["full_name"]
            assert country.id == test_country["id"]
            assert await repo.delete_model(country_id)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data,isNone", country_test_data_invalid)
    async def test_create_country_invalid_2(self, db_session, country_data, isNone):
        async with db_session.begin():
            repo = CountryRepository(db_session)
            country = await repo.create_entity(CountryCreate(**country_data))
            if not isNone:
                assert country is not None
                assert country.abbreviation == country_data["abbreviation"]
                assert country.full_name == country_data["full_name"]
                assert country.id == country_data["id"]
            else:
                assert country is None


class TestGet:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data,inTable", country_test_get)
    async def test_1_get_country_by_id(self, db_session, country_data, inTable):
        async with db_session.begin():
            repo = CountryRepository(db_session)
            country = await repo.get_as_model(Object_ID(id=int(country_data["id"])))
            if inTable:
                assert country is not None
                assert country.abbreviation == country_data["abbreviation"]
                assert country.full_name == country_data["full_name"]
                assert country.id is not None
                assert country.id == country_data["id"]
            else:
                assert country is None

    @pytest.mark.asyncio
    async def test_get_country(self, db_session):
        async with db_session.begin():
            repo = CountryRepository(db_session)
            country_list = await repo.get_models(PaginationBase())
            assert len(country_list) == 5

    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data", country_test_data)
    async def test_get_by_abbreviation_country(self, db_session, country_data):
        async with db_session.begin():
            repo = CountryRepository(db_session)
            country = await repo.get_by_abbreviation(
                CountryFind(abbreviation=country_data["abbreviation"])
            )
            assert country is not None
            assert country.abbreviation == country_data["abbreviation"]
            assert country.full_name == country_data["full_name"]
            assert country.id is not None
            assert country.id == country_data["id"]


class TestDelete:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data", country_test_data)
    async def test_1_get_country_by_id(self, db_session, country_data):
        async with db_session.begin():
            repo = CountryRepository(db_session)
            country_id = Object_ID(id=int(country_data["id"]))
            country = await repo.get_as_model(country_id)
            assert country is not None
            result = await repo.delete_model(country_id)
            assert result
            country = await repo.get_as_model(country_id)
            assert country is None

    @pytest.mark.asyncio
    async def test_1_get_country_by_id(self, db_session):
        async with db_session.begin():
            repo = CountryRepository(db_session)
            country_id = Object_ID(id=150)
            result = await repo.delete_model(country_id)
            assert not result


class TestUpdate:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data,country_id,isNone", country_update_test_data)
    async def test_1_update_country(self, db_session, country_data, country_id, isNone):
        async with db_session.begin():
            repo = CountryRepository(db_session)
            country_id = Object_ID(id=country_id)
            country_before = await repo.get_as_model(country_id)
            country_after = await repo.update_model(
                country_id, CountryUpdate(**country_data)
            )
            if not isNone:
                assert country_after is not None
                country_abbreviation = country_data.get("abbreviation")
                country_full_name = country_data.get("full_name")
                assert (
                    country_after.abbreviation == country_abbreviation
                    if country_abbreviation is not None
                    else country_before.abbreviation
                )
                assert (
                    country_after.full_name == country_full_name
                    if country_full_name is not None
                    else country_before.full_name
                )

            else:
                assert country_after is None

    @pytest.mark.asyncio
    async def test_2_update_country(self, db_session):
        repo = CountryRepository(db_session)
        country_id = Object_ID(id=1)

        # Тест 1: Успешное обновление всех полей
        async with db_session.begin():
            initial_update = CountryUpdate(abbreviation="RU", full_name="Россия")

            updated_country = await repo.update_model(country_id, initial_update)

            assert updated_country is not None
            assert updated_country.abbreviation == "RU"
            assert updated_country.full_name == "Россия"
        async with db_session.begin():
            # Проверка пустого обновления
            empty_update_result = await repo.update_model(
                country_id, CountryUpdate(abbreviation=None, full_name=None)
            )
            assert empty_update_result is None
            with pytest.raises(InvalidRequestError):
                await db_session.commit()

        # Тест 2: Проверка сохранения данных после обновления
        async with db_session.begin():
            current_country = await repo.get_as_model(country_id)

            # Проверки
            assert current_country is not None
            assert current_country.abbreviation == "RU"
            assert current_country.full_name == "Россия"

            # Проверка частичного обновления
            partial_update_result = await repo.update_model(
                country_id, CountryUpdate(abbreviation="CA", full_name=None)
            )
            assert partial_update_result is None
            with pytest.raises(InvalidRequestError):
                await db_session.commit()

        # Тест 3: Финальная проверка неизменности данных
        async with db_session.begin():
            final_country = await repo.get_as_model(country_id)
            assert final_country is not None
            assert final_country.abbreviation == "RU"
            assert final_country.full_name == "Россия"

    @pytest.mark.asyncio
    async def test_3_update_country(self, db_session):
        async with db_session.begin():
            repo = CountryRepository(db_session)
            country_id = Object_ID(id=1)
            country = await repo.get_as_model(country_id)
            assert country is not None
