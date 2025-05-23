from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.logging import logger
from app.db.models import Base


class DatabaseManager:
    """Базовый класс для управления подключением к базе данных."""

    def __init__(self, url: str = None) -> None:
        """
        Инициализирует подключение к базе данных PostgreSQL.

        :param url: Url БД
        """
        if not url:
            url = settings.DATABASE_URL

        self.engine = create_async_engine(
            url,
            echo=False,
            pool_size=5,
            max_overflow=5,
            isolation_level="READ COMMITTED",
        )
        self.async_session = sessionmaker(self.engine, expire_on_commit=False, class_=AsyncSession)

    async def connect(self) -> None:
        """Выполняет первоначальную настройку базы данных и проверяет подключение."""
        try:
            async with self.engine.connect() as conn:
                async with conn.begin():
                    await conn.run_sync(Base.metadata.create_all)

            logger.info("Successfully connected to PostgreSQL")
        except sqlalchemy.exc.OperationalError as e:
            logger.error(f"Database connection error: {e}")
            raise

    async def close(self) -> None:
        """Закрывает все соединения с базой данных."""
        await self.engine.dispose()
        logger.info("Database connections closed")

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        Асинхронный контекстный менеджер для сессии базы данных.

        Откатывает транзакцию при ошибке и автоматически закрывает сессию.
        """
        async with self.async_session() as session:
            try:
                logger.debug("Opening new database session")
                yield session
                logger.debug("Session ready to commit or rollback")
            except Exception as e:
                await session.rollback()
                logger.error(f"Database error: {e}")
                raise
            finally:
                await session.close()
                logger.debug("Session closed")


# Глобальный экземпляр DatabaseManager
db_manager = DatabaseManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Предоставляет асинхронную сессию базы данных для зависимостей FastAPI.

    :returns: Асинхронная сессия SQLAlchemy.
    :rtype: AsyncGenerator[AsyncSession, None]
    """
    async with db_manager.session() as session:
        yield session


if __name__ == "__main__":
    import asyncio

    async def initialize() -> None:
        """Инициализация базы данных."""
        await db_manager.connect()


    asyncio.run(initialize())
