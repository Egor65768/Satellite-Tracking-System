from datetime import date
from app.schemas import UserRole

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

satellite_test_date = [
    {
        "international_code": "123_A_123_A",
        "name_satellite": "Yaml-5012",
        "norad_id": 318420,
        "launch_date": date(2012, 1, 7),
        "country_id": 1,
    },
    {
        "international_code": "321_B_123_A",
        "name_satellite": "Yaml-5011",
        "norad_id": 318421,
        "launch_date": date(1999, 12, 7),
        "country_id": 1,
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

satellite_characteristic_test_date_1 = {
    "international_code": "321_B_123_A",
    "longitude": 143.1,
    "period": 1521.1,
    "launch_site": "Байконур",
    "rocket": "Союз 2.1",
    "launch_mass": 126237.3,
    "manufacturer": "Роскосмос",
    "model": "11kk4224",
    "expected_lifetime": 18,
    "remaining_lifetime": 2,
    "details": "nfhehdloevasdvsdjkdsjdsouefhouhofd",
}

region_test = [
    {"name_region": "USA"},
    {"name_region": "Russia"},
    {"name_region": "China"},
    {"name_region": "Canada"},
    {"name_region": "South Africa"},
    {"name_region": "Nigeria"},
    {"name_region": "Brazil"},
]

region_list = [
    {"name_region": "region_1"},
    {"name_region": "region_2"},
    {"name_region": "region_3"},
    {"name_region": "region_4"},
    {"name_region": "region_5"},
]

subregion_list = [
    {"name_region": "region_1", "name_subregion": "subregion_1"},
    {"name_region": "region_1", "name_subregion": "subregion_2"},
    {"name_region": "region_1", "name_subregion": "subregion_3"},
    {"name_region": "region_1", "name_subregion": "subregion_4"},
    {"name_region": "region_1", "name_subregion": "subregion_5"},
    {"name_region": "region_2", "name_subregion": "subregion_6"},
    {"name_region": "region_3", "name_subregion": "subregion_7"},
    {"name_region": "region_2", "name_subregion": "subregion_8"},
    {"name_region": "region_2", "name_subregion": "subregion_9"},
    {"name_region": "region_2", "name_subregion": "subregion_10"},
]

test_subregion = [
    {"name_region": "USA", "name_subregion": "Texas"},
    {"name_region": "USA", "name_subregion": "New York"},
    {"name_region": "USA", "name_subregion": "California"},
    {"name_region": "USA", "name_subregion": "Las Vegas"},
    {"name_region": "USA", "name_subregion": "Florida"},
    {"name_region": "Russia", "name_subregion": "Moscow"},
    {"name_region": "Russia", "name_subregion": "Stavropol"},
    {"name_region": "Brazil", "name_subregion": "Rio"},
]

test_create_data = [
    {
        "id": "2021-12bd-23730",
        "transmitter_type": "Ku-Band",
        "image": "tests/test/test1.jpg",
    },
    {
        "id": "2001-1234-24670",
        "transmitter_type": "Ku-Band",
        "image": "tests/test/test2.jpg",
    },
]

test_get_data = [
    ("2021-12bd-23730", True),
    ("2001-1234-24670", True),
    ("2edecdf", False),
]

region_test_data = [
    {"name_region": "China"},
    {"name_region": "Russia"},
    {"name_region": "USA"},
]

subregion_test_data = [
    {"name_subregion": "Wuhan", "id_region": 1},
    {"name_subregion": "Moscow", "id_region": 2},
    {"name_subregion": "Stavropol", "id_region": 2},
    {"name_subregion": "Saint Petersburg", "id_region": 2},
]

user_data = {"name": "Egor", "email": "rhkh3ik334@gmail.com", "password": "Egor21212e"}
admin_data = {
    "name": "Dimas",
    "email": "d2rhgrnjev34@gmail.com",
    "password": "rfSgor21212e",
    "role": UserRole.ADMIN,
}
email_admin_data = {"email": "d2rhgrnjev34@gmail.com"}
user_data_admin = {
    "name": "Slavic",
    "email": "admin_adminovich@gmail.com",
    "password": "Admin_1291_admin",
    "role": UserRole.ADMIN,
}
invalid_email = {"email": "Invalid_email@gmail.com"}
user_data_tests = [
    {"name": "Misha", "email": "dfff34@gmail.com", "password": "Ldr21fe2e"},
    {"name": "Sasha", "email": "dfv13@mail.ru", "password": "vcMSr2lf2e"},
    {"name": "Alina", "email": "dakddjda344@gmail.com", "password": "fevhvbfHBVKD824"},
    {
        "name": "Nick",
        "email": "nick12331nick@gmail.com",
        "password": "rwhjGDUu8842gfguc",
    },
]

token_data = dict()
headers_auth = dict()

invalid_refresh_token = (
    "eyJhbGciOiJIUzI1NiIsInR"
    "5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODk"
    "wIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWU"
    "sImlhdCI6MTUxNjIzOTAyMn0.KMUFsIDTnFmyG3nM"
    "iGM6H9FNFUROf3wh7SmqJp-QV30"
)
