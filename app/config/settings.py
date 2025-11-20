"""Application configuration settings."""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = ConfigDict(
        env_file=".env",
        case_sensitive=False
    )

    app_name: str = "polygon-manager"
    app_host: str = "0.0.0.0"
    app_port: int = 8080

    database_url: str = "sqlite:///./data/polygon.db"
    database_echo: bool = False

    max_coordinate: float = 1000000.0
    max_name_length: int = 255
    max_points_count: int = 10000
    min_points_count: int = 3

    api_delay_seconds: int = 5

    log_level: str = "INFO"

    cors_origins: list = ["*"]
    cors_credentials: bool = True
    cors_methods: list = ["*"]
    cors_headers: list = ["*"]


settings = Settings()
