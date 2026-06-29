from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


APP_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = Path(__file__).resolve().parents[2]
PROJECT_DIR = Path(__file__).resolve().parents[3]

UPLOAD_DIR = APP_DIR / "storage" / "uploads"


class Settings(BaseSettings):
    """
    Настройки приложения, загружаемые из переменных окружения или .env файла.
    """

    model_config = SettingsConfigDict(
        env_file=(
            PROJECT_DIR / ".env",
            BACKEND_DIR / ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    ELASTICSEARCH_URL: str = "http://localhost:9200"
    ELASTICSEARCH_INDEX_NAME: str = "documents"

    REDIS_URL: str = "redis://localhost:6379/0"
    SEARCH_CACHE_TTL_SECONDS: int = 300

    DATABASE_URL: str = "postgresql+psycopg://postgres:postgres@localhost:5432/practice_db"


settings = Settings()

MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_FILE_EXTENSIONS = {".pdf", ".docx"}

TEXT_CHUNK_SIZE = 1000
TEXT_CHUNK_OVERLAP = 100

ELASTICSEARCH_URL = settings.ELASTICSEARCH_URL
ELASTICSEARCH_INDEX_NAME = settings.ELASTICSEARCH_INDEX_NAME

REDIS_URL = settings.REDIS_URL
SEARCH_CACHE_TTL_SECONDS = settings.SEARCH_CACHE_TTL_SECONDS

DATABASE_URL = settings.DATABASE_URL

SEARCH_HISTORY_LIMIT = 10