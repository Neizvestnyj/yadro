from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.core.config import settings
from app.db.models import Base

# Конфигурация Alembic
config = context.config
fileConfig(config.config_file_name)

# Установка DATABASE_URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Метаданные моделей
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Выполняет миграции в оффлайн-режиме.

    :returns: Ничего не возвращает.
    :rtype: None
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """
    Выполняет миграции в онлайн-режиме с использованием асинхронного движка.

    :returns: Ничего не возвращает.
    :rtype: None
    """
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        echo=False,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata,
            )
        )
        # Используем синхронную транзакцию внутри run_sync
        await connection.run_sync(lambda sync_conn: context.run_migrations())

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    asyncio.run(run_migrations_online())
