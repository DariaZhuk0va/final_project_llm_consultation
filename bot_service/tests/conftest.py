import pytest
from unittest.mock import patch
import fakeredis.aioredis
from app.bot import handlers


@pytest.fixture(autouse=True)
def mock_redis_for_handlers():
    """
    Подменяет get_redis в модуле app.bot.handlers на fake Redis клиент.
    Все тесты, использующие handlers, будут получать фейковый Redis.
    """
    fake_redis = fakeredis.aioredis.FakeRedis(decode_responses=True)

    async def fake_get_redis():
        return fake_redis

    with patch.object(handlers, "get_redis", side_effect=fake_get_redis):
        yield fake_redis