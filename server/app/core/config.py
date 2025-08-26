from pydantic import BaseSettings
from pathlib import Path
from typing import List

class Settings(BaseSettings):
    app_name: str = "Hearsona API"
    api_version: str = "v1"
    debug: bool = False
    cors_origins: List[str] = ["http://localhost:5173"]

    request_timeout: int = 300


def get_settings() -> Settings:
    return Settings()
