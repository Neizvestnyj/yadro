from typing import Any

from httpx import AsyncClient
from tenacity import retry, stop_after_attempt

from app.core.config import settings


@retry(stop=stop_after_attempt(3))
async def fetch_random_users(count: int) -> dict[str, Any]:
    """
    Получает данные пользователей из randomuser.me.

    :param count: Количество пользователей для загрузки.
    :type count: int
    :returns: Данные пользователей в формате JSON.
    :rtype: Dict[str, Any]
    :raises HTTPException: Если запрос к API не удался после 3 попыток.
    """
    async with AsyncClient() as client:
        response = await client.get(f"{settings.RANDOMUSER_API_URL}?results={count}")
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    import asyncio

    async def ten_fetch() -> None:  # noqa: D103
        users = await fetch_random_users(10)
        print(f"{users}")

    asyncio.run(ten_fetch())
