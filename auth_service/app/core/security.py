from __future__ import annotations

import time
from typing import Any, Dict

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings

# Контекст для хеширования паролей (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def _now() -> int:
    """
    Возвращает текущее время в секундах (UTC timestamp)
    """
    return int(time.time())


def hash_password(password: str) -> str:
    """
    Хеширует пароль с использованием bcrypt
    """
    return pwd_context.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Проверяет, соответствует ли пароль его хешу
    """
    return pwd_context.verify(password, hashed_password)


def create_access_token(sub: str, role: str) -> str:
    """
    Создаёт JWT access token.

    sub: Идентификатор пользователя (user_id)
    role: Роль пользователя ("admin" или "user")
    
    return: Закодированный JWT токен
    """
    payload = {
        "sub": sub,
        "role": role,
        "iat": _now(),
        "exp": _now() + settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)  


def decode_token(token: str) -> Dict[str, Any]:
    """
    Декодирует и валидирует JWT токен.

    token: JWT токен

    return: Payload токена (содержит sub, role, exp, iat)
    
    """
    return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])  