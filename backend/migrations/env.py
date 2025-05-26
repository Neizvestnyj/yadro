from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine

from app.core.config import settings
from app.db.models import Base

# Конфигурация Alembic
config = context.config
fileConfig(config.config_file_name)

# Установка DATABASE_URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL_SYNC)
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Выполняет миграции в оффлайн-режиме."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Выполняет миграции в онлайн-режиме."""
    connectable = create_engine(
        config.get_main_option("sqlalchemy.url"),
        pool_pre_ping=True,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
