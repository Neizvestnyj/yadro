from fastapi import FastAPI
from prometheus_client import Gauge
from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator()
inprogress_requests = Gauge("fastapi_http_requests_in_progress", "Number of in-progress HTTP requests")


def configure_prometheus(app: FastAPI):
    instrumentator.instrument(app, metric_namespace="fastapi").expose(app, endpoint="/metrics")
