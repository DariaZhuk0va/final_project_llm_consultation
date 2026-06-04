from typing import Any, Dict

from jose import jwt, ExpiredSignatureError, JWTError

from app.core.config import settings


def decode_and_validate(token: str) -> Dict[str, Any]:
    """
    Декодирует и валидирует JWT токен (подпись, срок действия).
    
    token: JWT токен
    
    return: Payload токена (содержит sub, role, exp, iat)
    
    Raises:
        ValueError: Если токен недействителен или истёк
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG]
        )
        return payload
    except (ExpiredSignatureError, JWTError) as e:
        raise ValueError(f"Invalid or expired token: {e}")