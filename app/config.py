from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Marketplace Deal Agent"
    environment: str = "development"
    database_url: str = "sqlite:///./marketplace.db"
    collector_provider: str = "mock"

    openai_api_key: str | None = None
    openai_model: str = "gpt-5-mini"
    ai_notify_threshold: int = 80

    whatsapp_access_token: str | None = None
    whatsapp_phone_number_id: str | None = None
    whatsapp_recipient: str | None = None
    meta_graph_version: str = "v23.0"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
