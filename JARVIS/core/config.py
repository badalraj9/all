import os
from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    PROJECT_NAME: str = "JARVIS"
    VERSION: str = "1.0.0"

    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    PLUGINS_DIR: Path = BASE_DIR / "plugins"

    # Event Bus
    MAX_EVENT_HISTORY: int = 1000

    # Memory
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "jarvis_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

    QDRANT_HOST: str = os.getenv("QDRANT_HOST", "localhost")
    QDRANT_PORT: int = int(os.getenv("QDRANT_PORT", "6333"))

    class Config:
        env_file = ".env"

settings = Settings()
