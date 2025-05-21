from fastapi import FastAPI
from app.api import country_api

app = FastAPI()

# Подключаем роутеры из разных файлов
app.include_router(country_api.router, prefix="/country", tags=["country"])
