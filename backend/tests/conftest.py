from collections.abc import AsyncGenerator
from typing import Literal
from unittest.mock import AsyncMock, patch

from httpx import ASGITransport, AsyncClient
import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.db.models import Base
from app.db.session import get_db as get_session
from app.main import app


@pytest.fixture(scope="session")
def anyio_backend() -> Literal["asyncio"]:
    """
    Указывает бэкенд для асинхронных тестов.

    :returns: Название асинхронного бэкенда.
    :rtype: Literal['asyncio']
    """
    return "asyncio"


@pytest.fixture
async def async_client(async_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    Предоставляет асинхронный тестовый клиент FastAPI с переопределённой зависимостью get_db.

    :param async_session: Асинхронная сессия базы данных.
    :type async_session: AsyncSession
    :returns: Асинхронный тестовый клиент FastAPI.
    :rtype: AsyncGenerator[AsyncClient, None]
    """
    with patch("app.main.fetch_and_save_users", new_callable=AsyncMock) as _:
        app.dependency_overrides[get_session] = lambda: async_session
        _transport = ASGITransport(app=app)

        async with AsyncClient(transport=_transport, base_url="http://test", follow_redirects=True) as client:
            yield client

        app.dependency_overrides.clear()


@pytest.fixture
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет ас concepтную сессию базы данных для тестов с очисткой таблиц перед каждым тестом.

    :returns: Асинхронная сессия базы данных.
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async_engine = create_async_engine(settings.SQLALCHEMY_TEST_DATABASE_URL)

    # Создаем и очищаем тестовые таблицы
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async_session = async_sessionmaker(
        bind=async_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )

    async with async_session() as session:
        yield session

    await async_engine.dispose()
