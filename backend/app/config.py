from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/nautical_gourmet"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/nautical_gourmet"

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    # App
    APP_NAME: str = "Nautical Gourmet Atlas"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/v1"

    # Default language
    DEFAULT_LANGUAGE: str = "en"
    SUPPORTED_LANGUAGES: list = ["hr", "en", "de"]

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
