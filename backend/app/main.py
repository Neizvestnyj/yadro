from collections.abc import AsyncGenerator, Awaitable, Callable
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.v1 import random, users
from app.core.cache import cache
from app.core.config import settings
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
    await cache.close()


app = FastAPI(title="Random User API", lifespan=lifespan)
app.include_router(users.router)
app.include_router(random.router)

CORS_ORIGINS = {
    "development": ["http://localhost:3001", "http://frontend:3001"],
    "production": ["http://localhost:3001", "http://frontend:3001"],  # ["http://localhost", "https://yourdomain.com"]
}

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS.get(settings.ENVIRONMENT, ["http://localhost:3001"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Настройка Prometheus с кастомным именем метрики
instrumentator = Instrumentator()
inprogress_requests = Gauge("fastapi_http_requests_in_progress", "Number of in-progress HTTP requests")


@app.middleware("http")
async def track_inprogress_requests(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response | None:
    """
    Middleware для подсчёта текущих обрабатываемых HTTP-запросов.

    :param request: Объект запроса FastAPI.
    :param call_next: Функция для вызова следующего обработчика в цепочке middleware.
    :return: Объект ответа FastAPI.

    Увеличивает счётчик метрики `fastapi_http_requests_in_progress` при начале обработки запроса
    и уменьшает при завершении (независимо от результата).
    """
    inprogress_requests.inc()
    try:
        response = await call_next(request)
        return response
    finally:
        inprogress_requests.dec()


instrumentator.instrument(app, metric_namespace="fastapi").expose(app, endpoint="/metrics")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
