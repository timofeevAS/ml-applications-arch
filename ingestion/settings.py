from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    polling_seconds_timeout: int = Field(default=10, ge=1, alias="POLLING_SECONDS_TIMEOUT")
    digitraffic_stations_ids: list[int] = Field(default_factory=list, alias="DIGITRAFFIC_STATIONS_IDS")

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
print(settings)