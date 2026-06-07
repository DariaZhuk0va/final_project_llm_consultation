from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="",
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Bot Service"
    DEBUG: bool = True

    # Telegram Bot
    BOT_TOKEN: str = Field(..., alias="TELEGRAM_BOT_TOKEN")

    # JWT (для валидации)
    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # OpenRouter
    OPENROUTER_API_KEY: str
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_DEFAULT_MODEL: str = "openrouter/free"
    OPENROUTER_REFERER: str | None = "http://localhost:8000"
    OPENROUTER_TITLE: str | None = "My LLM App"
    OPENROUTER_TIMEOUT: float = 60.0

    # RabbitMQ и Redis
    RABBITMQ_URL: str = "amqp://guest:guest@rabbitmq:5672/"
    REDIS_URL: str = "redis://redis:6379/0"

    # Auth Service URL
    AUTH_SERVICE_URL: str | None = None

settings = Settings()