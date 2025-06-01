from asyncpg.exceptions import ConnectionDoesNotExistError, InvalidPasswordError
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.models.user import User
from app.db.session import DatabaseManager


@pytest.mark.anyio
async def test_connect_success() -> None:
    """
    Тест успешного подключения к тестовой БД.

    Ожидается, что DatabaseManager сможет успешно установить соединение
    с указанной тестовой БД без выброса исключений.
    """
    db = DatabaseManager(settings.SQLALCHEMY_TEST_DATABASE_URL)
    try:
        await db.connect()
    finally:
        await db.close()


@pytest.mark.anyio
async def test_connect_invalid_url() -> None:
    """
    Тест ошибки подключения с некорректным URL.

    При попытке соединения с заведомо неправильной строкой подключения
    должно быть выброшено исключение ConnectionDoesNotExistError.
    """
    db = DatabaseManager("postgresql+asyncpg://wrong:wrong@localhost:5432/invalid")
    with pytest.raises((ConnectionDoesNotExistError, InvalidPasswordError)):
        await db.connect()


@pytest.mark.anyio
async def test_session_commit(async_session: AsyncSession) -> None:
    """
    Тест сохранения пользователя в сессии и последующего получения.

    Добавляется объект User, выполняется коммит, затем объект извлекается
    из базы по ID и проверяется, что он был сохранён корректно.
    """
    new_user = User(gender="male", first_name="Test", last_name="User", email="test@example.com")

    async_session.add(new_user)
    await async_session.commit()
    await async_session.refresh(new_user)

    result = await async_session.get(User, new_user.id)

    assert result is not None
    assert result.first_name == "Test"
    assert result.last_name == "User"
    assert result.email == "test@example.com"
