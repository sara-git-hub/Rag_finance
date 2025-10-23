from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    OPENAI_API_KEY: str

    FILE_ALLOWED_TYPES : list
    FILE_MAX_SIZE : int
    FILE_DEFAULT_CHUNK_SIZE : int

    MONGODB_URL: str
    MONGODB_DATABASE: str

    CLE_API_CHANGES: str
    CLE_API_CHANGES_2: str
    CLE_API_BDT: str
    CLE_API_BDT_2: str
    CLE_API_OBLIG: str
    CLE_API_OBLIG_2: str

    class Config:
        env_file = ".env"

def get_settings():
    return Settings()