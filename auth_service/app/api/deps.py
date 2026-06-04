from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, ExpiredSignatureError, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenError, TokenExpiredError, UserNotFoundError
from app.core.security import decode_token
from app.db.session import get_db
from app.repositories.users import UserRepository
from app.usecases.auth import AuthUseCase


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def get_user_repo(session: Annotated[AsyncSession, Depends(get_db)]) -> UserRepository:
    """Предоставляет репозиторий пользователей"""
    return UserRepository(session)

def get_auth_usecase(
    user_repo: Annotated[UserRepository, Depends(get_user_repo)]) -> AuthUseCase:
    """Предоставляет usecase аутентификации"""
    return AuthUseCase(user_repo)

async def get_current_user_id(token: Annotated[str, Depends(oauth2_scheme)]) -> int:
    """
    Извлекает user_id из JWT токена.
    При ошибках токена выбрасывает InvalidTokenError или TokenExpiredError.
    """
    try:
        payload = decode_token(token)
        user_id_str = payload.get("sub")
        if user_id_str is None:
            raise InvalidTokenError("Token does not contain sub claim")
        return int(user_id_str)
    except ExpiredSignatureError:
        raise TokenExpiredError()
    except JWTError:
        raise InvalidTokenError()
    except ValueError:
        raise InvalidTokenError("Invalid user_id format in token")

async def get_current_user(
    user_id: Annotated[int, Depends(get_current_user_id)],
    user_repo: Annotated[UserRepository, Depends(get_user_repo)],
) -> UserRepository:
    """
    Возвращает объект пользователя по ID из токена.
    """
    user = await user_repo.get_by_id(user_id)
    if user is None:
        raise UserNotFoundError()  
    return user