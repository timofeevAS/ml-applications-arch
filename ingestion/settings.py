from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    polling_seconds_timeout: int = Field(default=10, ge=1, alias="POLLING_SECONDS_TIMEOUT")
    digitraffic_sources: dict[int, Path] = Field(default_factory=dict, alias="DIGITRAFFIC_SOURCES")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
print(settings)