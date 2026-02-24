import logging

from dotenv import load_dotenv
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from functools import lru_cache

from gateway.core.constants import FILE_ENCODER

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    logging.error("Отсутствует файл .env в корне проекта.")


class _ProjectBaseSettings(BaseSettings):
    """Базовые настройки Gateway"""
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding=FILE_ENCODER,
        populate_by_name=True,
        extra="ignore",
    )


class GreenAPISettings(_ProjectBaseSettings):
    instance_id: str = Field(..., alias="GREEN_API_INSTANCE_ID")
    api_token: str = Field(..., alias="GREEN_API_TOKEN")
    api_host: str = "https://api.green-api.com"
    core_url: str = "http://localhost:8001"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


class GatewaySettings(_ProjectBaseSettings):
    environment: Literal["local", "dev", "prod"] = Field(default="local", validation_alias="APP_ENV")
    app_name: str = Field(default="Qasqir Gateway")
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    green_api: GreenAPISettings = Field(default_factory=GreenAPISettings)

@lru_cache
def get_settings() -> GatewaySettings:
    return GatewaySettings()
