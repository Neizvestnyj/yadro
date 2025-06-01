from fastapi import FastAPI

from app.api.v1 import random, users
from app.core.config import settings
from app.lifecycle.lifespan_events import app_lifespan
from app.middleware.setup import configure_middleware
from app.monitoring.prometheus import configure_prometheus

# Создание FastAPI приложения
app = FastAPI(
    title=settings.APP_TITLE,
    lifespan=app_lifespan,
)

# Настройка middleware (включая CORS)
configure_middleware(app)

app.include_router(users.router)
app.include_router(random.router)

# Настройка Prometheus
configure_prometheus(app)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
