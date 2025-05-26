import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class GoogleSearchSettings(BaseSettings):
    GOOGLE_API_KEY: str
    CUSTOM_SEARCH_ENGINE_ID: str

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.getcwd(), ".env"),
        case_sensitive=True,
        extra="ignore",
    )


google_search_settings = GoogleSearchSettings()
