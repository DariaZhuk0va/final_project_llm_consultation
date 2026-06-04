from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """
    Схема для регистрации нового пользователя
    """
    email: EmailStr
    password: str = Field(..., min_length=8, description="Пароль (минимум 8 символов)")


class TokenResponse(BaseModel):
    """
    Схема ответа с JWT токеном
    """
    access_token: str
    token_type: str = "bearer"