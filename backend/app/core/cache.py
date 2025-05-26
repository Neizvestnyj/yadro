import json

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import logger

JsonType = dict | list | str | int | float | bool

class RedisCache:
    """Клиент для работы с Redis."""

    def __init__(self) -> None:
        """Инициализирует подключение к Redis."""
        self.client: redis.Redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def get(self, key: str) -> JsonType | None:
        """
        Получает значение из кэша по ключу.

        :param key: Ключ кэша.
        :type key: str
        :returns: Значение из кэша или None.
        :rtype: Optional[Any]
        """
        try:
            value = await self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def set(self, key: str, value: JsonType, ttl: int = 60) -> None:
        """
        Устанавливает значение в кэш с TTL.

        :param key: Ключ кэша.
        :type key: str
        :param value: Значение для кэширования.
        :type value: Any
        :param ttl: Время жизни кэша в секундах.
        :type ttl: int
        :returns: None
        """
        try:
            await self.client.setex(key, ttl, json.dumps(value))
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    async def delete(self, key: str) -> None:
        """
        Удаляет ключ из кэша.

        :param key: Ключ кэша.
        :type key: str
        :returns: None
        """
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    async def close(self) -> None:
        """
        Закрывает соединение с Redis.

        :returns: None
        """
        await self.client.close()


cache = RedisCache()
