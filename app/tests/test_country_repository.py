import pytest
from app.db import CountryRepository
from app.schemas import CountryCreate

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


class TestCreate:

    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data", country_test_data)
    async def test_create_country(self, db_session, country_data):
        repo = CountryRepository(db_session)

        country = await repo.create_country(CountryCreate(**country_data))
        await db_session.commit()
        assert country is not None
        assert country.abbreviation == country_data["abbreviation"]
        assert country.full_name == country_data["full_name"]
        assert country.id is not None
        assert country.id == country_data["id"]

    @pytest.mark.asyncio
    @pytest.mark.parametrize("country_data,isNone", country_test_data_invalid)
    async def test_create_country_invalid(self, db_session, country_data, isNone):
        repo = CountryRepository(db_session)
        country = await repo.create_country(CountryCreate(**country_data))
        if country is not None:
            await db_session.commit()
        if not isNone:
            assert country is not None
            assert country.abbreviation == country_data["abbreviation"]
            assert country.full_name == country_data["full_name"]
            assert country.id == country_data["id"]
        else:
            assert country is None
