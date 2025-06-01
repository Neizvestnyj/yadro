from fastapi import FastAPI
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
inprogress_requests = Gauge("fastapi_http_requests_in_progress", "Number of in-progress HTTP requests")


def configure_prometheus(app: FastAPI) -> None:
    """
    Конфигурирует интеграцию Prometheus для FastAPI приложения.

    Подключает инструментатор для сбора метрик и выставляет
    endpoint для экспорта метрик по адресу `/metrics`.

    :param app: Экземпляр FastAPI приложения.
    :type app: FastAPI
    :return: None
    """
    instrumentator.instrument(app, metric_namespace="fastapi").expose(app, endpoint="/metrics")
