from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.logging import logger

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    Настройки приложения.

    :param APP_TITLE: Название приложение.
    :type APP_TITLE: str
    :param DATABASE_URL: URL для подключения к PostgreSQL.
    :type DATABASE_URL: str
    :param SQLALCHEMY_TEST_DATABASE_URL: URL для подключения к тестовой PostgreSQL.
    :type SQLALCHEMY_TEST_DATABASE_URL: str
    :param REDIS_URL: URL для подключения к Redis.
    :type REDIS_URL: str
    :param RANDOMUSER_API_URL: URL внешнего API randomuser.me.
    :type RANDOMUSER_API_URL: str
    :param ENVIRONMENT: Окружение приложения (development или production).
    :type ENVIRONMENT: str
    """

    APP_TITLE: str = "Random User API"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:1234@localhost:5432/randomuser_db"
    SQLALCHEMY_TEST_DATABASE_URL: str = "postgresql+asyncpg://postgres:1234@localhost:5432/test_randomuser_db"
    REDIS_URL: str = "redis://localhost:6379/0"
    RANDOMUSER_API_URL: str = "https://randomuser.me/api/"
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(
        env_file=str(ENV_PATH),
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    @property
    def DATABASE_URL_SYNC(self) -> str:  # noqa: N802
        """
        Возвращает синхронный URL подключения к базе данных, заменяя драйвер ``asyncpg`` на ``psycopg2``.

        :return: Строка с URL базы данных,
        пригодным для использования с синхронным SQLAlchemy-движком (например, в Alembic).
        :rtype: str
        """
        return self.DATABASE_URL.replace("asyncpg", "psycopg2")


settings: Settings = Settings()
logger.info(f"{settings.__dict__}")

if __name__ == "__main__":
    print(settings)
