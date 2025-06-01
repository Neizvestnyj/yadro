from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.cache import cache
from app.core.logging import logger
from app.db.session import db_manager
from app.services.user_service import fetch_and_save_users


@asynccontextmanager
async def app_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Функция, которая выполняется при старте приложения и завершении.

    :param app: FastAPI приложение
    :rtype: FastAPI
    :return: None

    Инициализирует базу данных с помощью функции `init_db()` и запускает прослушивание событий,
    используя `start_listening_events()`.
    """
    logger.info("Application startup...")
    await db_manager.connect()

    logger.info("Fetching initial users...")
    async with db_manager.session() as session:
        await fetch_and_save_users(session, 1000)
    logger.info("Initial users fetched and saved.")

    yield

    logger.info("Application shutdown...")
    await db_manager.close()
    await cache.close()
    logger.info("Application shutdown complete.")
