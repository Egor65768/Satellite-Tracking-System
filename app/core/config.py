from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    db_url: str = "postgresql+asyncpg://postgres:Egor2002@localhost:5432/sat_db"

settings = Settings()