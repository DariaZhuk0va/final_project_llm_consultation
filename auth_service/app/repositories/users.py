from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserRole
from app.db.models import User


class UserRepository:
    """
    Репозиторий для доступа к данным пользователей
    """
    
    def __init__(self, session: AsyncSession):
        self._session = session
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        stmt = select(User).where(User.id == user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create(self, email: str, password_hash: str, role: UserRole = UserRole.USER) -> User:
        """
        Создать нового пользователя.
        
        email: Email пользователя
        password_hash: Хешированный пароль
        role: Роль (по умолчанию "user")

        return: Созданный объект User
        """
        user = User(email=email, password_hash=password_hash, role=role)
        self._session.add(user)
        await self._session.commit()
        await self._session.refresh(user)
        return user