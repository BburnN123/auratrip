"""Backend application settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    app_name: str = "Auratrip"
    debug: bool = False
    secret_key: str = "change-me-in-production"

    # AI / LLM
    kimi_api_key: str | None = None

    # Model routing
    tokenrouter_api_key: str | None = None

    # Scraping
    bright_data_api_key: str | None = None

    # Sandboxes
    daytona_api_key: str | None = None
    daytona_api_url: str | None = None

    # GPU compute
    nosana_api_key: str | None = None

    # Multimodal generation
    sensenova_api_key: str | None = None

    # Identity / attestation
    terminal3_api_key: str | None = None

    # Video infrastructure
    videodb_api_key: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
