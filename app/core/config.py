from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    GEMINI_API_KEY: str
    REDIS_URL: str = "redis://localhost:6379/0"
    DATABASE_URL: str = "sqlite:///./sql_app.db"
    USE_REDIS: bool = False # set to True if Redis is available

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
