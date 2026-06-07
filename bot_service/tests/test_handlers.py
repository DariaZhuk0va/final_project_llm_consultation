import pytest
from unittest.mock import AsyncMock, patch
from fakeredis.aioredis import FakeRedis
from jose import jwt
from app.core.config import settings
from app.bot.handlers import save_token, handle_message

# Фикстура: фейковый Redis (асинхронный)
@pytest.fixture
async def fake_redis():
    redis_client = FakeRedis(decode_responses=True)
    yield redis_client
    await redis_client.flushall()

# Фикстура: подмена get_redis в модуле handlers
@pytest.fixture
def mock_get_redis(fake_redis):
    async def _get_redis():
        return fake_redis
    with patch("app.bot.handlers.get_redis", _get_redis):
        yield fake_redis

# Фикстура: мок для message.answer
@pytest.fixture
def mock_message_answer():
    with patch("aiogram.types.Message.answer", new_callable=AsyncMock) as mock:
        yield mock

# Фикстура: мок для celery задачи
@pytest.fixture
def mock_celery_task():
    with patch("app.bot.handlers.llm_request.delay") as mock_delay:
        yield mock_delay

# Вспомогательная функция для создания Message
def make_message(text, user_id=123, username="test"):
    from aiogram.types import Message, Chat, User
    return Message(
        message_id=1,
        date=0,
        chat=Chat(id=user_id, type="private"),
        from_user=User(id=user_id, is_bot=False, first_name="Test"),
        text=text,
    )

# Вспомогательная функция для генерации подписанного JWT
def generate_valid_token(sub="123", role="user"):
    payload = {"sub": sub, "role": role, "exp": 9999999999}
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

# Тесты
async def test_save_token_valid(mock_get_redis, mock_message_answer):
    redis = mock_get_redis
    token = generate_valid_token()
    msg = make_message(f"/token {token}")
    await save_token(msg)
    saved = await redis.get(f"tg_user:{msg.from_user.id}")
    assert saved == token
    mock_message_answer.assert_called_with("✅ Токен сохранён. Теперь вы можете отправлять сообщения боту.")

async def test_save_token_invalid_format(mock_get_redis, mock_message_answer):
    msg = make_message("/token invalid")
    await save_token(msg)
    mock_message_answer.assert_called_with("❌ Неверный формат JWT токена.")
    redis = mock_get_redis
    saved = await redis.get(f"tg_user:{msg.from_user.id}")
    assert saved is None

async def test_handle_message_no_token(mock_get_redis, mock_message_answer, mock_celery_task):
    msg = make_message("Hello")
    await handle_message(msg)
    mock_celery_task.assert_not_called()
    mock_message_answer.assert_called_with(
        "🔒 У вас нет активного токена. Пожалуйста, получите токен в Auth Service и выполните команду /token <jwt>."
    )

async def test_handle_message_with_valid_token(mock_get_redis, mock_message_answer, mock_celery_task):
    redis = mock_get_redis
    user_id = 123
    valid_token = generate_valid_token()
    await redis.set(f"tg_user:{user_id}", valid_token)
    msg = make_message("What is AI?", user_id=user_id)
    await handle_message(msg)
    mock_celery_task.assert_called_once_with(tg_chat_id=user_id, prompt="What is AI?")
    # Проверяем, что бот отправил уведомление о принятии запроса
    mock_message_answer.assert_any_call("⏳ Запрос принят, ищу ответ...")