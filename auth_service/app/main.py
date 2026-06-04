from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.api.router import router as api_router  # ← импорт из router.py


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Управление жизненным циклом приложения: создание таблиц при старте
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


def create_app() -> FastAPI:
    """
    Фабрика приложения FastAPI
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description="Auth Service for JWT-based authentication",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.include_router(api_router)  # ← подключение общего роутера

    @app.get("/health", tags=["System"])
    async def health_check():
        return {"status": "ok", "environment": settings.ENV}

    return app

app = create_app()