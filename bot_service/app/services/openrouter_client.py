import httpx
from typing import List, Dict, Any, Optional

from app.core.config import settings


class ExternalServiceError(Exception):
    """Исключение для ошибок внешнего сервиса (OpenRouter)"""
    def __init__(self, service_name: str, original_error: Optional[Exception] = None):
        self.service_name = service_name
        self.original_error = original_error
        message = f"Ошибка при обращении к {service_name}"
        if original_error:
            message += f": {str(original_error)}"
        super().__init__(message)


class OpenRouterClient:
    """
    Клиент для взаимодействия с API OpenRouter (синхронная версия для Celery)
    """

    def __init__(self):
        self.base_url = settings.OPENROUTER_BASE_URL
        self.api_key = settings.OPENROUTER_API_KEY
        self.referer = settings.OPENROUTER_REFERER
        self.title = settings.OPENROUTER_TITLE
        self.default_model = settings.OPENROUTER_DEFAULT_MODEL
        self.timeout = settings.OPENROUTER_TIMEOUT

    def _build_headers(self) -> Dict[str, str]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        if self.referer:
            headers["HTTP-Referer"] = self.referer
        if self.title:
            headers["X-Title"] = self.title
        return headers

    def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Отправить запрос к OpenRouter и получить ответ модели (синхронно).
        """
        if not messages:
            raise ExternalServiceError(
                service_name="OpenRouter",
                original_error=Exception("Messages list cannot be empty")
            )

        url = f"{self.base_url}/chat/completions"
        headers = self._build_headers()

        payload: Dict[str, Any] = {
            "model": model or self.default_model,
            "messages": messages,
        }
        if temperature is not None:
            payload["temperature"] = temperature
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        with httpx.Client(timeout=self.timeout) as client:
            try:
                response = client.post(url, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
            except httpx.HTTPStatusError as e:
                raise ExternalServiceError("OpenRouter", e)
            except httpx.RequestError as e:
                raise ExternalServiceError("OpenRouter", e)
            except Exception as e:
                raise ExternalServiceError("OpenRouter", e)

        try:
            choices = data.get("choices", [])
            if not choices:
                raise ExternalServiceError("OpenRouter", Exception("No choices in response"))
            answer = choices[0].get("message", {}).get("content", "")
            if not answer:
                raise ExternalServiceError("OpenRouter", Exception("Empty content in response"))
            return answer
        except (KeyError, IndexError, TypeError) as e:
            raise ExternalServiceError("OpenRouter", e)