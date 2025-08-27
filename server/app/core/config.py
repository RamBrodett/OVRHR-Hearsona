from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List

class Settings(BaseSettings):
    app_name: str = "Hearsona API"
    api_version: str = "v1.0"
    app_description: str = "AI-powered audio generation API with conversational interface"
    debug: bool = False
    cors_origins: List[str] = ["http://localhost:5173"]
    cors_methods: List[str] = ["*"]
    cors_headers: List[str] = ["*"]

    request_timeout: int = 300


def get_settings() -> Settings:
    return Settings()
