import pytest
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token, decode_token

def test_hash_password():
    password = "mysecret"
    hashed = hash_password(password)
    assert hashed != password
    assert isinstance(hashed, str)
    assert hashed.startswith("$2b$")  # bcrypt prefix

def test_verify_password_correct():
    password = "correct"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True

def test_verify_password_incorrect():
    password = "correct"
    wrong = "wrong"
    hashed = hash_password(password)
    assert verify_password(wrong, hashed) is False

def test_create_access_token():
    user_id = "123"
    role = "user"
    token = create_access_token(sub=user_id, role=role)
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALG])
    assert payload["sub"] == user_id
    assert payload["role"] == role
    assert "iat" in payload
    assert "exp" in payload
    exp = datetime.fromtimestamp(payload["exp"])
    iat = datetime.fromtimestamp(payload["iat"])
    assert exp > iat

def test_decode_token_valid():
    user_id = "456"
    role = "admin"
    token = create_access_token(sub=user_id, role=role)
    payload = decode_token(token)
    assert payload["sub"] == user_id
    assert payload["role"] == role

def test_decode_token_invalid():
    with pytest.raises(jwt.JWTError):
        decode_token("invalid.token.string")