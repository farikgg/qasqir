import logging

from dotenv import load_dotenv
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Literal
from functools import lru_cache

from src.core.constants import FILE_ENCODER

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    logging.error("Отсутствует файл .env в корне проекта.")


class _ProjectBaseSettings(BaseSettings):
    """Базовые настройки."""
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding=FILE_ENCODER,
        populate_by_name=True,
        extra="ignore",
    )


class DataBaseSettings(_ProjectBaseSettings):
    database_url: str = Field(..., alias="DATABASE_URL")


class AppSettings(_ProjectBaseSettings):
    environment: Literal["local", "dev", "prod"] = Field(default="local", validation_alias="APP_ENV")
    app_name: str = Field(default="Qasqir Core")
    gateway_url: str = Field(default="http://localhost:8000", validation_alias="GATEWAY_URL")
    debug: bool = Field(default=False, validation_alias="APP_DEBUG")
    database_settings: DataBaseSettings = Field(default_factory=DataBaseSettings)

@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()
