"""Backend application settings."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""
    app_name: str = "Auratrip"
    debug: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
