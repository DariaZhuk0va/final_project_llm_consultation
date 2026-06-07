import pytest
from jose import jwt
from app.core.config import settings
from app.core.jwt import decode_and_validate

def test_decode_and_validate_valid():
    # Создаём тестовый токен тем же секретом
    payload = {"sub": "123", "role": "user", "exp": 9999999999}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    result = decode_and_validate(token)
    assert result["sub"] == "123"
    assert result["role"] == "user"

def test_decode_and_validate_invalid():
    with pytest.raises(ValueError):
        decode_and_validate("garbage.token.string")

def test_decode_and_validate_expired():
    from datetime import datetime, timedelta
    exp = int((datetime.now() - timedelta(minutes=1)).timestamp())
    payload = {"sub": "123", "exp": exp}
    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    with pytest.raises(ValueError):
        decode_and_validate(token)