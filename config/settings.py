from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Re:World"
    debug: bool = True

    database_url: str = "sqlite:///./reworld.db"

    google_api_key: str = ""
    gemini_api_key: str = ""
    llm_model: str = "gemini-2.0-flash"

    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000,http://localhost:3001"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


settings = Settings()