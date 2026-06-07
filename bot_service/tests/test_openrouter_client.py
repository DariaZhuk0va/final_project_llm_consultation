# bot_service/tests/integration/test_openrouter_client.py
import pytest
import respx
from httpx import Response
from app.services.openrouter_client import OpenRouterClient, ExternalServiceError

@respx.mock
def test_openrouter_client_success():
    client = OpenRouterClient()
    mock_route = respx.post(f"{client.base_url}/chat/completions").mock(
        return_value=Response(200, json={
            "choices": [{"message": {"content": "Hello from LLM"}}]
        })
    )
    response = client.chat_completion(messages=[{"role": "user", "content": "Hi"}])
    assert response == "Hello from LLM"
    assert mock_route.called

@respx.mock
def test_openrouter_client_http_error():
    client = OpenRouterClient()
    respx.post(f"{client.base_url}/chat/completions").mock(
        return_value=Response(500, json={"error": "server error"})
    )
    with pytest.raises(ExternalServiceError):
        client.chat_completion(messages=[{"role": "user", "content": "Hi"}])

@respx.mock
def test_openrouter_client_network_error():
    client = OpenRouterClient()
    respx.post(f"{client.base_url}/chat/completions").mock(side_effect=Exception("Connection refused"))
    with pytest.raises(ExternalServiceError):
        client.chat_completion(messages=[{"role": "user", "content": "Hi"}])