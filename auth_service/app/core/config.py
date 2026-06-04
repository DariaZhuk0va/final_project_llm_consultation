from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Общие настройки
    APP_NAME: str = "Auth Service"          
    ENV: str = "development"                 
    DEBUG: bool = True

    # JWT
    JWT_SECRET: str
    JWT_ALG: str = "HS256"                   
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # База данных (SQLite)
    SQLITE_PATH: str = str(BASE_DIR / "auth.db")   

settings = Settings()