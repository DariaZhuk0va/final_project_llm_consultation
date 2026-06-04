import requests
import redis
from celery import Task
from app.core.config import settings
from app.infra.celery_app import celery_app

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

@celery_app.task(bind=True, name="llm_request")
def llm_request(self, tg_chat_id: int, prompt: str) -> None:
    """
    Запрашивает ответ у OpenRouter, сохраняет результат в Redis.
    Ключ: llm_result:{tg_chat_id}
    """
    result_key = f"llm_result:{tg_chat_id}"
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    if settings.OPENROUTER_REFERER:
        headers["HTTP-Referer"] = settings.OPENROUTER_REFERER
    if settings.OPENROUTER_TITLE:
        headers["X-Title"] = settings.OPENROUTER_TITLE

    try:
        resp = requests.post(
            f"{settings.OPENROUTER_BASE_URL}/chat/completions",
            headers=headers,
            json={
                "model": settings.OPENROUTER_DEFAULT_MODEL,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=settings.OPENROUTER_TIMEOUT,
        )
        resp.raise_for_status()
        reply = resp.json()["choices"][0]["message"]["content"]
        # Сохраняем успешный ответ в Redis на 5 минут
        redis_client.setex(result_key, 300, reply)
    except Exception as e:
        error_msg = f"❌ Ошибка LLM: {str(e)}"
        redis_client.setex(result_key, 300, error_msg)
        raise