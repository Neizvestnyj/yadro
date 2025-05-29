from typing import Any

from httpx import AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreate
from app.services.user_service import create_user


@pytest.mark.asyncio
async def test_get_random_user(async_session: AsyncSession, async_client: AsyncClient) -> None:
    """
    Тестирует эндпоинт GET /v1/random/ для получения рандомного пользователя.

    :param async_session: Асинхронная сессия базы данных.
    :type async_session: AsyncSession
    :param async_client: Асинхронный тестовый клиент FastAPI.
    :type async_client: AsyncClient
    :returns: Ничего не возвращает.
    :rtype: None
    """
    user = UserCreate(
        gender="male",
        first_name="Tom",
        last_name="Wilson",
        phone="444-555-6666",
        email="tom.wilson@example.com",
        picture="http://example.com/tom.jpg",
    )
    await create_user(async_session, user)
    response = await async_client.get("/v1/random")
    assert response.status_code == 200
    user_data: dict[str, Any] = response.json()
    assert user_data["email"] == "tom.wilson@example.com"


@pytest.mark.asyncio
async def test_get_random_user_when_none_exist(async_session: AsyncSession, async_client: AsyncClient) -> None:
    """
    Тестирует эндпоинт GET /v1/random/ для получения рандомного пользователя.

    :param async_session: Асинхронная сессия базы данных.
    :type async_session: AsyncSession
    :param async_client: Асинхронный тестовый клиент FastAPI.
    :type async_client: AsyncClient
    :returns: Ничего не возвращает.
    :rtype: None
    """
    response = await async_client.get("/v1/random")
    assert response.status_code == 404
    get_user = response.json()
    assert get_user["detail"] == "User not found"
