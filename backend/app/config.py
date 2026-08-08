from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://localhost:5432/shortify"
    BASE_DOMAIN: str = "http://localhost:8000"
    FRONTEND_ORIGIN: str = "http://localhost:5173"

    # JWT — SECRET_KEY must be set in .env for production
    SECRET_KEY: str = "change-me-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


settings = Settings()
