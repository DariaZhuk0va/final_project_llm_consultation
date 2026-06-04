from fastapi import HTTPException

class BaseHTTPException(HTTPException):
    """Базовое HTTP-исключение для Auth Service"""
    def __init__(self, status_code: int, detail: str):
        super().__init__(status_code=status_code, detail=detail)

class UserAlreadyExistsError(BaseHTTPException):
    def __init__(self, detail: str = "User with this email already exists"):
        super().__init__(status_code=409, detail=detail)

class InvalidCredentialsError(BaseHTTPException):
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(status_code=401, detail=detail)

class InvalidTokenError(BaseHTTPException):
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(status_code=401, detail=detail)

class TokenExpiredError(BaseHTTPException):
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(status_code=401, detail=detail)

class UserNotFoundError(BaseHTTPException):
    def __init__(self, detail: str = "User not found"):
        super().__init__(status_code=404, detail=detail)

class PermissionDeniedError(BaseHTTPException):
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(status_code=403, detail=detail)