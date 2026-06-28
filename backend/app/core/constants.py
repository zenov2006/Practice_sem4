import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
UPLOAD_DIR = APP_DIR / "storage" / "uploads"

MAX_FILE_SIZE_MB = 20
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
ALLOWED_FILE_EXTENSIONS = {".pdf", ".docx"}

TEXT_CHUNK_SIZE = 1000
TEXT_CHUNK_OVERLAP = 100

ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
ELASTICSEARCH_INDEX_NAME = os.getenv("ELASTICSEARCH_INDEX_NAME", "documents")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
SEARCH_CACHE_TTL_SECONDS = 300