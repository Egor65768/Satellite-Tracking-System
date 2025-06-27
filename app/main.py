from fastapi import FastAPI
from app.api import (
    country_api,
    satellite_api,
    region_api,
    coverage_zone_api,
    user_api,
    auth_api,
)

app = FastAPI()

# Подключаем роутеры из разных файлов
app.include_router(country_api.router, prefix="/country", tags=["country"])
app.include_router(satellite_api.router, prefix="/satellite", tags=["satellite"])
app.include_router(region_api.router, prefix="/region", tags=["region"])
app.include_router(
    coverage_zone_api.router, prefix="/coverage_zone", tags=["coverage_zone"]
)
app.include_router(user_api.router, prefix="/user", tags=["user"])
app.include_router(auth_api.router, prefix="/auth", tags=["auth"])
