import builtins
import json

import redis.asyncio as redis

from app.core.config import settings
from app.core.logging import logger

JsonType = dict | list | str | int | float | bool


class RedisCache:
    """Клиент для работы с Redis."""

    def __init__(self) -> None:
        """Инициализирует RedisCache без немедленного подключения."""
        self._client: redis.Redis | None = None

    @property
    def client(self) -> redis.Redis:
        """Лениво создает и возвращает клиент Redis."""
        if self._client is None:
            self._client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        return self._client

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
            await self.client.setex(key, ttl, json.dumps(value, default=str))
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    async def delete(self, key: str | tuple) -> None:
        """
        Удаляет ключ из кэша.

        :param key: Ключ кэша.
        :type key: str
        :returns: None
        """
        try:
            if isinstance(key, tuple):
                await self.client.delete(*key)
            else:
                await self.client.delete(key)
        except Exception as e:
            logger.error(f"Redis delete error: {e}")

    async def sadd(self, key: str, member: str) -> None:
        """
        Добавляет элемент в множество Redis по указанному ключу.

        :param key: Ключ множества.
        :type key: str
        :param member: Элемент для добавления в множество.
        :type member: str
        :returns: None
        """
        try:
            await self.client.sadd(key, member)
        except Exception as e:
            logger.error(f"Redis sadd error: {e}")

    async def smembers(self, key: str) -> builtins.set[str]:
        """
        Получает все элементы множества Redis по указанному ключу.

        :param key: Ключ множества.
        :type key: str
        :returns: Множество элементов.
        :rtype: Set[str]
        """
        try:
            return await self.client.smembers(key)
        except Exception as e:
            logger.error(f"Redis smembers error: {e}")
            return set()

    async def close(self) -> None:
        """
        Закрывает соединение с Redis.

        :returns: None
        """
        await self.client.close()


cache = RedisCache()


def get_cache() -> RedisCache:
    """Предоставляет класс RedisCache для зависимостей FastAPI."""
    return cache
