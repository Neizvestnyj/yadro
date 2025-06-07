from unittest.mock import ANY, AsyncMock, MagicMock, call

from fastapi import FastAPI
import pytest
from pytest_mock import MockerFixture

from app.core.logging import logger
from app.db.session import db_manager
from app.lifecycle.lifespan_events import app_lifespan


async def test_app_lifespan_success(mocker: MockerFixture) -> None:
    """
    Тестирует успешное выполнение жизненного цикла приложения.

    :param mocker: Фикстура для создания моков.
    :type mocker: MockerFixture
    :returns: None
    """
    # Мокаем db_manager.connect и db_manager.close
    mock_connect = mocker.patch.object(db_manager, "connect", new=AsyncMock())
    mock_close = mocker.patch.object(db_manager, "close", new=AsyncMock())

    # Мокаем logger.info
    mock_logger_info = mocker.patch.object(logger, "info", new=MagicMock())

    # Мокаем fetch_and_save_users
    mock_fetch_and_save_users = mocker.patch("app.lifecycle.lifespan_events.fetch_and_save_users", new=AsyncMock())

    # Мокаем cache.close
    mock_cache_close = mocker.patch("app.core.cache.cache.close", new=AsyncMock())

    # Создаём тестовое FastAPI приложение
    app = FastAPI()

    # Используем контекстный менеджер app_lifespan
    async with app_lifespan(app):
        # Проверяем вызовы во время активного контекста
        mock_connect.assert_called_once()
        mock_fetch_and_save_users.assert_called_once_with(ANY, 1000)
        mock_close.assert_not_called()
        mock_cache_close.assert_not_called()
        assert mock_logger_info.call_count == 3
        mock_logger_info.assert_any_call("Application startup...")
        mock_logger_info.assert_any_call("Fetching initial users...")
        mock_logger_info.assert_any_call("Initial users fetched and saved.")

    # Проверяем вызовы после выхода из контекста
    mock_close.assert_called_once()
    mock_cache_close.assert_called_once()
    assert mock_logger_info.call_count == 5
    mock_logger_info.assert_any_call("Application shutdown...")
    mock_logger_info.assert_any_call("Application shutdown complete.")


async def test_app_lifespan_connect_failure(mocker: MockerFixture) -> None:
    """
    Тестирует обработку ошибки при подключении к базе данных.

    :param mocker: Фикстура для создания моков.
    :type mocker: MockerFixture
    :returns: None
    """
    # Мокаем db_manager.connect, чтобы он вызывал исключение
    mock_connect = mocker.patch.object(
        db_manager, "connect", new=AsyncMock(side_effect=RuntimeError("Connection failed"))
    )
    mock_close = mocker.patch.object(db_manager, "close", new=AsyncMock())

    # Мокаем logger.info и logger.error
    mock_logger_info = mocker.patch.object(logger, "info", new=MagicMock())
    mock_logger_error = mocker.patch.object(logger, "error", new=MagicMock())

    # Создаём тестовое FastAPI приложение
    app = FastAPI()

    # Проверяем, что ошибка подключения вызывает исключение
    with pytest.raises(RuntimeError, match="Connection failed"):
        async with app_lifespan(app):
            pass

    # Проверяем вызовы
    mock_connect.assert_called_once()
    mock_close.assert_not_called()  # close не вызывается, так как исключение прерывает до yield
    mock_logger_info.assert_called_once_with("Application startup...")
    mock_logger_error.assert_not_called()  # logger.error не вызывается в app_lifespan
    assert call("Application shutdown...") not in mock_logger_info.call_args_list
    assert call("Database disconnected.") not in mock_logger_info.call_args_list
