from fastapi import FastAPI
from app.core.config import settings

def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="Bot Service – Telegram bot with LLM via OpenRouter",
        version="1.0.0",
    )

    @app.get("/health", tags=["System"])
    async def health_check():
        return {"status": "ok", "service": "bot_service"}

    return app

app = create_app()