from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator, metrics

from app.api.v1 import random, users
from app.core.logging import logger
from app.db.session import db_manager, get_db
from app.services.user_service import fetch_and_save_users

# Вынесенная зависимость, чтобы избежать B008
db_dependency = Depends(get_db)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Функция, которая выполняется при старте приложения и завершении.

    :param app: FastAPI приложение
    :rtype: FastAPI
    :return: None

    Инициализирует базу данных с помощью функции `init_db()` и запускает прослушивание событий,
    используя `start_listening_events()`.
    """
    # код инициализации
    await db_manager.connect()
    logger.info("Starting up, fetching 1000 users...")
    async with db_manager.session() as session:
        await fetch_and_save_users(session, 1000)
    logger.info("Successfully fetched and saved 1000 users")

    yield

    # код завершения работы
    await db_manager.close()


app = FastAPI(title="Random User API", lifespan=lifespan)
app.include_router(users.router)
app.include_router(random.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "http://localhost:3001", "http://frontend:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка Prometheus с кастомным именем метрики
instrumentator = Instrumentator()
instrumentator.instrument(app,  metric_namespace="fastapi").expose(app, endpoint="/metrics")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
