from typing import Any

import pytest
from httpx import AsyncClient, Response
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
        city="Test city",
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
    update_data = {"first_name": "Updated", "email": "updated@example.com"}
    response = await async_client.put(f"/v1/users/{user.id}", json=update_data)
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
                "gender": "female",
                "name": {"title": "Miss", "first": "Jennie", "last": "Nichols"},
                "location": {
                    "street": {
                        "number": 8929,
                        "name": "Valwood Pkwy",
                    },
                    "city": "Billings",
                    "state": "Michigan",
                    "country": "United States",
                    "postcode": "63104",
                    "coordinates": {"latitude": "-69.8246", "longitude": "134.8719"},
                    "timezone": {"offset": "+9:30", "description": "Adelaide, Darwin"},
                },
                "email": "jennie.nichols@example.com",
                "login": {
                    "uuid": "7a0eed16-9430-4d68-901f-c0d4c1c3bf00",
                    "username": "yellowpeacock117",
                    "password": "addison",
                    "salt": "sld1yGtd",
                    "md5": "ab54ac4c0be9480ae8fa5e9e2a5196a3",
                    "sha1": "edcf2ce613cbdea349133c52dc2f3b83168dc51b",
                    "sha256": "48df5229235ada28389b91e60a935e4f9b73eb4bdb855ef9258a1751f10bdc5d",
                },
                "dob": {"date": "1992-03-08T15:13:16.688Z", "age": 30},
                "registered": {"date": "2007-07-09T05:51:59.390Z", "age": 14},
                "phone": "(272) 790-0888",
                "cell": "(489) 330-2385",
                "id": {"name": "SSN", "value": "405-88-3636"},
                "picture": {
                    "large": "https://randomuser.me/api/portraits/men/75.jpg",
                    "medium": "https://randomuser.me/api/portraits/med/men/75.jpg",
                    "thumbnail": "https://randomuser.me/api/portraits/thumb/men/75.jpg",
                },
                "nat": "US",
            },
            {
                "gender": "male",
                "name": {"title": "Mr", "first": "Liam", "last": "Griffin"},
                "location": {
                    "street": {"number": 4023, "name": "Hickory Lane"},
                    "city": "Cedar Rapids",
                    "state": "Iowa",
                    "country": "United States",
                    "postcode": "52404",
                    "coordinates": {"latitude": "42.0097", "longitude": "-91.6441"},
                    "timezone": {"offset": "-6:00", "description": "Central Time (US & Canada)"},
                },
                "email": "liam.griffin@example.com",
                "login": {
                    "uuid": "a3f5f8e7-8b91-4a13-a987-3baf49c1a4e1",
                    "username": "brownkoala284",
                    "password": "matrix42",
                    "salt": "N7dH2Ztr",
                    "md5": "bd7b3a27a10a66304d4e6bbbaaa34c67",
                    "sha1": "e042cd1b4f83ac09b0d8e326fcfbb07ad3f31989",
                    "sha256": "b8746bb6801c6ea8e546a67a6dd9f1a46cf12b1f470ef51b84b5738396f3b6cd",
                },
                "dob": {"date": "1985-11-23T09:44:00.000Z", "age": 39},
                "registered": {"date": "2010-06-15T11:32:45.000Z", "age": 14},
                "phone": "(303) 555-0132",
                "cell": "(303) 555-0198",
                "id": {"name": "SSN", "value": "123-45-6789"},
                "picture": {
                    "large": "https://randomuser.me/api/portraits/men/45.jpg",
                    "medium": "https://randomuser.me/api/portraits/med/men/45.jpg",
                    "thumbnail": "https://randomuser.me/api/portraits/thumb/men/45.jpg",
                },
                "nat": "US",
            },
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
    assert users[0]["first_name"] == "Jennie"
    assert users[0]["email"] in "jennie.nichols@example.com"

    assert users[1]["first_name"] == "Liam"
    assert users[1]["email"] in "liam.griffin@example.com"
