from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings


class Database:
    """
    Асинхронная работа с базой данных SQLite
    """
    
    def __init__(self, url: str | None = None):
        self.url = url or f"sqlite+aiosqlite:///{settings.SQLITE_PATH}"
        self.engine = create_async_engine(
            self.url,
            echo=settings.DEBUG,      
            future=True,              
        )
        self.AsyncSessionLocal = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )


db = Database()
engine = db.engine
AsyncSessionLocal = db.AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Генератор сессий для внедрения зависимостей
    """
    async with AsyncSessionLocal() as session:
        yield session