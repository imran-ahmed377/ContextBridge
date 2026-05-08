from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Configuration for ContextBridge application."""

    # App settings
    app_name: str = "ContextBridge"
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000

    # Embedding settings
    embedding_model: str = "all-MiniLM-L6-v2"  # Fast, lightweight model for MVP
    embedding_dimension: int = 384

    # Database settings
    db_path: str = "./data/contextbridge.db"

    # Connectors
    github_token: Optional[str] = None
    notion_token: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
