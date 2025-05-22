from pathlib import Path

from pydantic_settings import BaseSettings

from app.core.logging import logger

BASE_DIR = Path(__file__).resolve().parents[2]
ENV_PATH = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    Настройки приложения.

    :param DATABASE_URL: URL для подключения к PostgreSQL.
    :type DATABASE_URL: str
    :param RANDOMUSER_API_URL: URL внешнего API randomuser.me.
    :type RANDOMUSER_API_URL: str
    """

    DATABASE_URL: str = "postgresql+asyncpg://postgres:1234@localhost:5432/randomuser_db"
    SQLALCHEMY_TEST_DATABASE_URL: str = "postgresql+asyncpg://postgres:1234@localhost:5432/test_randomuser_db"
    RANDOMUSER_API_URL: str = "https://randomuser.me/api/"

    class Config:
        """Конфигурация Pydantic Settings для чтения переменных из .env-файла."""

        env_file = str(ENV_PATH)
        env_file_encoding = "utf-8"


settings: Settings = Settings()
logger.info(f"{settings.__dict__}")

if __name__ == "__main__":
    print(settings)
