from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated

from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase
from app.api.deps import get_auth_usecase, get_current_user_id
from app.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError, UserNotFoundError  # ← изменено

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
        "/register",
        response_model=UserPublic,
        status_code=status.HTTP_201_CREATED
        )
async def register(
    register_data: RegisterRequest,
    auth_usecase: Annotated[AuthUseCase, Depends(get_auth_usecase)],
):
    """
    Регистрация нового пользователя
    """
    try:
        user_data = await auth_usecase.register(
            email=register_data.email,
            password=register_data.password,
        )
        return UserPublic.model_validate(user_data)
    except UserAlreadyExistsError as e:  # ← изменено
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
            )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_usecase: Annotated[AuthUseCase, Depends(get_auth_usecase)],
):
    """
    Логин пользователя (OAuth2 форма)
    Поле username интерпретируется как email
    """
    try:
        token_data = await auth_usecase.login(
            email=form_data.username,
            password=form_data.password,
        )
        return TokenResponse(**token_data)
    except InvalidCredentialsError as e:  # ← изменено
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
            )


@router.get("/me", response_model=UserPublic)
async def get_me(
    user_id: Annotated[int, Depends(get_current_user_id)],
    auth_usecase: Annotated[AuthUseCase, Depends(get_auth_usecase)],
):
    """
    Получение профиля текущего авторизованного пользователя.
    """
    try:
        user_data = await auth_usecase.get_profile(user_id)
        return UserPublic.model_validate(user_data)
    except UserNotFoundError as e:  # ← изменено
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
            )
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
            )