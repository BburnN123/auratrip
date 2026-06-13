"""Backend application settings."""

from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import ConfigDict


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    app_name: str = "Auratrip"
    debug: bool = False

    videodb_api_url: str = "https://api.videodb.ai"
    videodb_api_key: Optional[str] = None
    # Use 'mock' to route requests to the local mock endpoints, 'live' to use real VideoDB
    videodb_mode: str = "live"

    model_config = ConfigDict(env_file=".env")


settings = Settings()
