from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import asyncio

from app.core.config import settings
from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis
from app.tasks.llm_tasks import llm_request

router = Router()

@router.message(Command("token"))
async def save_token(message: Message):
    """
    Сохраняет JWT токен в Redis для данного пользователя.
    """
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2:
        await message.answer("❌ Использование: /token <ваш_jwt_токен>")
        return

    jwt_token = parts[1].strip()
    # Простая проверка формата JWT
    if len(jwt_token.split('.')) != 3:
        await message.answer("❌ Неверный формат JWT токена.")
        return

    # Валидация токена
    try:
        decode_and_validate(jwt_token)
    except ValueError as e:
        await message.answer(f"❌ Недействительный токен: {e}")
        return

    redis = await get_redis()

    ttl = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
    await redis.set(f"tg_user:{message.from_user.id}", jwt_token, ex=ttl)

    await message.answer("✅ Токен сохранён. Теперь вы можете отправлять сообщения боту.")


@router.message()
async def handle_message(message: Message):
    """
    Обрабатывает текстовое сообщение:
    - проверяет наличие и валидность токена,
    - отправляет задачу в Celery,
    - ждёт результат в Redis и отправляет пользователю.
    """
    user_id = message.from_user.id
    redis = await get_redis()

    # 1. Проверяем наличие токена
    jwt_token = await redis.get(f"tg_user:{user_id}")
    if not jwt_token:
        await message.answer(
            "🔒 У вас нет активного токена. Пожалуйста, получите токен в Auth Service и выполните команду /token <jwt>."
        )
        return

    # 2. Валидируем токен
    try:
        decode_and_validate(jwt_token)
    except ValueError as e:
        await redis.delete(f"tg_user:{user_id}")
        await message.answer(
            f"❌ Ваш токен недействителен или истёк: {e}\n"
            "Пожалуйста, получите новый токен и выполните /token <новый_токен>."
        )
        return

    # 3. Запускаем Celery-задачу
    prompt = message.text
    llm_request.delay(tg_chat_id=user_id, prompt=prompt)
    await message.answer("⏳ Запрос принят, ищу ответ...")

    # 4. Ожидаем результат в Redis
    result_key = f"llm_result:{user_id}"
    timeout_seconds = 30
    poll_interval = 0.5
    elapsed = 0
    while elapsed < timeout_seconds:
        await asyncio.sleep(poll_interval)
        elapsed += poll_interval
        result = await redis.get(result_key)
        if result is not None:
            await redis.delete(result_key)

            MAX_LEN = 4096
            if len(result) <= MAX_LEN:
                await message.answer(result)
            else:
                for i in range(0, len(result), MAX_LEN):
                    chunk = result[i:i+MAX_LEN]
                    await message.answer(chunk)
                    await asyncio.sleep(0.5)  
            return

    # Если время вышло
    await message.answer("⏰ Время ожидания ответа истекло. Попробуйте позже.")