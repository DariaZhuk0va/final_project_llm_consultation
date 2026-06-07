import redis
from celery import Task
from app.core.config import settings
from app.infra.celery_app import celery_app
from app.services.openrouter_client import OpenRouterClient  # импорт клиента

redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)

@celery_app.task(bind=True, name="llm_request")
def llm_request(self, tg_chat_id: int, prompt: str) -> None:
    """
    Запрашивает ответ у OpenRouter через OpenRouterClient,
    сохраняет результат в Redis.
    Ключ: llm_result:{tg_chat_id}
    """
    result_key = f"llm_result:{tg_chat_id}"

    try:
        client = OpenRouterClient()
        reply = client.chat_completion(messages=[{"role": "user", "content": prompt}])
        redis_client.setex(result_key, 300, reply)
    except Exception as e:
        error_msg = f"❌ Ошибка LLM: {str(e)}"
        redis_client.setex(result_key, 300, error_msg)
        raise