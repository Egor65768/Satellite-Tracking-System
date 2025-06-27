from .v1 import country_api, satellite_api, region_api, coverage_zone_api, user_api
from .v1.auth import endpoints as auth_api

__all__ = [
    "country_api",
    "satellite_api",
    "region_api",
    "coverage_zone_api",
    "user_api",
    "auth_api",
]
