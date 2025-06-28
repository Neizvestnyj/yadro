from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.monitoring.prometheus import inprogress_requests

# Определяем CORS_ORIGINS здесь или импортируем из config.py
CORS_ORIGINS_CONFIG = {
    "development": ["http://localhost:3001", "http://frontend:3001", "http://localhost:3000", "http://frontend:3000"],
    "production": [
        "http://localhost",  # Для Nginx на localhost:80
        "http://localhost:3001",  # Для локального dev фронтенда против "prod" бэкенда
        # "https://your.actual.domain", # Когда появится домен
    ],
}


async def track_inprogress_requests_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response | None:
    """
    Middleware для подсчёта текущих обрабатываемых HTTP-запросов.

    :param request: Объект запроса FastAPI.
    :param call_next: Функция для вызова следующего обработчика в цепочке middleware.
    :return: Объект ответа FastAPI.
    :rtype: Response | None

    Увеличивает счётчик метрики `fastapi_http_requests_in_progress` при начале обработки запроса
    и уменьшает при завершении (независимо от результата).
    """
    inprogress_requests.inc()
    try:
        response = await call_next(request)
        return response
    finally:
        inprogress_requests.dec()


def configure_middleware(app: FastAPI) -> None:
    """
    Добавляет middleware в экземпляр FastAPI-приложения.

    :param app: Экземпляр FastAPI, к которому необходимо применить middleware.
    :type app: FastAPI
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ORIGINS_CONFIG.get(settings.ENVIRONMENT, ["http://localhost:3001"]),
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.middleware("http")(track_inprogress_requests_middleware)
