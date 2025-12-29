from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    SECRET_KEY: str

    FILE_ALLOWED_TYPES : list
    FILE_MAX_SIZE : int
    FILE_DEFAULT_CHUNK_SIZE : int

    POSTGRES_USERNAME : str
    POSTGRES_PASSWORD : str
    POSTGRES_HOST : str
    POSTGRES_PORT : int
    POSTGRES_MAIN_DATABASE : str

    CLE_API_CHANGES: str
    CLE_API_CHANGES_2: str

    # Exchange Rates Backfill Configuration
    ENABLE_INITIAL_BACKFILL: bool = True
    BACKFILL_DAYS: int = 30

    GENERATION_BACKEND: str
    EMBEDDING_BACKEND: str

    OPENAI_API_KEY: Optional[str] = None
    OPENAI_API_URL: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    OLLAMA_BASE_URL: Optional[str] = None

    GENERATION_MODEL_ID_LITERAL: Optional[List[str]] = None
    GENERATION_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_ID: Optional[str] = None
    EMBEDDING_MODEL_SIZE: Optional[int] = None
    EMBEDDING_DEVICE: Optional[str] = None
    INPUT_DEFAULT_MAX_CHARACTERS: Optional[int] = None
    GENERATION_DEFAULT_MAX_TOKENS: Optional[int] = None
    GENERATION_DEFAULT_TEMPERATURE: Optional[float] = None

    VECTOR_DB_BACKEND_LITERAL: Optional[List[str]] = None
    VECTOR_DB_BACKEND : str
    VECTOR_DB_PATH : str
    QDRANT_URL: Optional[str] = None  # URL for remote Qdrant (Docker)
    VECTOR_DB_DISTANCE_METHOD: Optional[str] = None
    VECTOR_DB_PGVEC_INDEX_THRESHOLD: int = 100

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()