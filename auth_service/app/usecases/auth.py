from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import UserAlreadyExistsError, InvalidCredentialsError, UserNotFoundError
from app.repositories.users import UserRepository
from app.schemas.user import UserRole
from app.db.models import User


class AuthUseCase:
    """
    Бизнес-логика регистрации и логина
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def register(self, email: str, password: str) -> User:
        """
        Регистрация нового пользователя.

        email: Email пользователя
        password: Пароль

        return: Объект User (созданный пользователь)
        """

        existing_user = await self.user_repo.get_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError(f"User with email '{email}' already exists")

        hashed_password = hash_password(password)

        user = await self.user_repo.create(
            email=email,
            password_hash=hashed_password,
            role=UserRole.USER
        )

        return user

    async def login(self, email: str, password: str) -> dict:
        """
        Аутентификация пользователя и выдача JWT.

        email: Email пользователя
        password: Пароль

        return: Словарь с access_token и token_type
        """
        user = await self.user_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError("Invalid email or password")

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError("Invalid email or password")
        
        access_token = create_access_token(
            sub=str(user.id),
            role=user.role
        )

        return {"access_token": access_token, "token_type": "bearer"}

    async def get_profile(self, user_id: int) -> User:
        """
        Получение профиля пользователя по ID

        user_id: ID пользователя

        return: Объект User
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError(f"User with id '{user_id}' not found")

        return user