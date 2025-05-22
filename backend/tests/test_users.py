from typing import Any

from httpx import AsyncClient, Response
import pytest
from respx import MockRouter
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.schemas.user import UserCreate
from app.services.user_service import create_user, fetch_and_save_users


@pytest.mark.asyncio
async def test_get_users_paginated(async_session: AsyncSession, async_client: AsyncClient) -> None:
    """
    Тестирует эндпоинт GET /v1/users с пагинацией.

    :param async_session: Асинхронная сессия базы данных.
    :type async_session: AsyncSession
    :param async_client: Асинхронный тестовый клиент FastAPI.
    :type async_client: AsyncClient
    :returns: Ничего не возвращает.
    :rtype: None
    """
    users = await fetch_and_save_users(async_session, 15)

    # Тестируем первую страницу
    response = await async_client.get("/v1/users?limit=10&offset=0")
    assert response.status_code == 200
    users_resp = response.json()
    assert len(users_resp) == 10
    assert users_resp[0]["first_name"] == users[0].first_name

    # Тестируем вторую страницу
    response = await async_client.get("/v1/users?limit=5&offset=10")
    assert response.status_code == 200
    users_resp = response.json()
    assert len(users_resp) == 5
    assert users_resp[0]["first_name"] == users[10].first_name


@pytest.mark.asyncio
async def test_get_users(async_session: AsyncSession, async_client: AsyncClient) -> None:
    """
    Тестирует эндпоинт GET /v1/users для получения списка пользователей.

    :param async_session: Асинхронная сессия базы данных.
    :type async_session: AsyncSession
    :param async_client: Асинхронный тестовый клиент FastAPI.
    :type async_client: AsyncClient
    :returns: Ничего не возвращает.
    :rtype: None
    """
    await fetch_and_save_users(async_session, 2)
    response = await async_client.get("/v1/users?limit=1&offset=0")
    assert response.status_code == 200
    users: list[dict[str, Any]] = response.json()
    assert len(users) == 1


@pytest.mark.asyncio
async def test_get_user_by_id(async_session: AsyncSession, async_client: AsyncClient) -> None:
    """
    Тестирует эндпоинт GET /v1/users/{user_id} для получения пользователя по ID.

    :param async_session: Асинхронная сессия базы данных.
    :type async_session: AsyncSession
    :param async_client: Асинхронный тестовый клиент FastAPI.
    :type async_client: AsyncClient
    :returns: Ничего не возвращает.
    :rtype: None
    """
    user_data = UserCreate(
        first_name="Original",
        last_name="User",
        email="original@example.com",
        gender="male",
        phone="1234567890",
        location="Test Location",
        picture="http://example.com/pic.jpg",
    )
    user = await create_user(async_session, user_data)

    # Получаем пользователя
    response = await async_client.get(f"/v1/users/{user.id}")
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["first_name"] == user.first_name
    assert user_data["email"] == user.email


@pytest.mark.asyncio
async def test_update_user(async_session: AsyncSession, async_client: AsyncClient) -> None:
    """
    Тестирует эндпоинт PUT /v1/users/{user_id} для обновления данных пользователя.

    :param async_session: Асинхронная сессия базы данных.
    :type async_session: AsyncSession
    :param async_client: Асинхронный тестовый клиент FastAPI.
    :type async_client: AsyncClient
    :returns: Ничего не возвращает.
    :rtype: None
    """
    user_data = UserCreate(
        first_name="Original",
        last_name="User",
        email="original@example.com",
        gender="male",
        phone="1234567890",
        location="Test Location",
        picture="http://example.com/pic.jpg",
    )
    user = await create_user(async_session, user_data)

    # Обновляем пользователя
    update_data = {
        "first_name": "Updated",
        "email": "updated@example.com"
    }
    response = await async_client.put(
        f"/v1/users/{user.id}",
        json=update_data
    )
    assert response.status_code == 200
    updated_user = response.json()
    assert updated_user["first_name"] == "Updated"
    assert updated_user["email"] == "updated@example.com"


@pytest.mark.asyncio
async def test_delete_user(async_session: AsyncSession, async_client: AsyncClient) -> None:
    """
    Тестирует эндпоинт DELETE /v1/users/{user_id} для удаления пользователя.

    :param async_session: Асинхронная сессия базы данных.
    :type async_session: AsyncSession
    :param async_client: Асинхронный тестовый клиент FastAPI.
    :type async_client: AsyncClient
    :returns: Ничего не возвращает.
    :rtype: None
    """
    # Создаем тестового пользователя
    user_data = UserCreate(
        first_name="Original",
        last_name="User",
        email="original@example.com",
        gender="male",
        phone="1234567890",
        location="Test Location",
        picture="http://example.com/pic.jpg",
    )
    user = await create_user(async_session, user_data)

    # Удаляем пользователя
    response = await async_client.delete(f"/v1/users/{user.id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_fetch_users_from_api(async_client: AsyncClient, respx_mock: MockRouter) -> None:
    """
    Тестирует эндпоинт POST /v1/users/fetch для загрузки пользователей из API randomuser.me.

    :param async_client: Асинхронный тестовый клиент FastAPI.
    :type async_client: AsyncClient
    :param respx_mock: Фикстура для мокирования HTTP-запросов с помощью respx.
    :type respx_mock: respx.MockRouter
    :returns: Ничего не возвращает.
    :rtype: None
    """
    # Мокаем ответ от randomuser.me
    mock_users = {
        "results": [
            {
                "name": {"first": "Mocked", "last": "User1"},
                "email": "mocked1@example.com",
                "gender": "male",
                "phone": "1234567890",
                "location": {"city": "Mock City", "country": "Mock Country"},
                "picture": {"large": "http://example.com/pic1.jpg",
                            "thumbnail": "http://example.com/pic2.jpg", }
            },
            {
                "name": {"first": "Mocked", "last": "User2"},
                "email": "mocked2@example.com",
                "gender": "female",
                "phone": "0987654321",
                "location": {"city": "Mock City", "country": "Mock Country"},
                "picture": {"large": "http://example.com/pic2.jpg",
                            "thumbnail": "http://example.com/pic2.jpg"
                            }
            }
        ]
    }

    respx_mock.get(settings.RANDOMUSER_API_URL).mock(return_value=Response(200, json=mock_users))

    response = await async_client.post("/v1/users/fetch?count=2")
    assert response.status_code == 200
    result = response.json()
    assert len(result) == 2

    # Проверяем, что пользователи сохранились в БД
    users_response = await async_client.get("/v1/users?limit=2&offset=0")
    users = users_response.json()
    assert len(users) == 2
    assert users[0]["first_name"] == "Mocked"
    assert users[0]["email"] in ["mocked1@example.com", "mocked2@example.com"]
