"""Centralized app configuration, loaded from environment variables (.env)."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    environment: str = "development"
    secret_key: str = "dev-secret-key-change-in-prod"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 14
    frontend_url: str = "http://localhost:5173"

    database_url: str = "postgresql://insightai:insightai@localhost:5432/insightai"

    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/auth/google/callback"

    openai_api_key: str = ""
    openai_model: str = "gpt-4o"

    upload_dir: str = "./uploads"
    max_upload_mb: int = 50

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
