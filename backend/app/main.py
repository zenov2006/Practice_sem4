from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.exception_handlers import register_exception_handlers
from app.core.metrics import PrometheusMiddleware, register_metrics_endpoint

app = FastAPI(
    title="Document Search API",
    description="Backend API для загрузки документов и полнотекстового поиска.",
    version="0.1.0",
)

register_exception_handlers(app)

# Подключаем middleware для сбора метрик
app.add_middleware(PrometheusMiddleware)

# Регистрируем эндпоинт /metrics для Prometheus
register_metrics_endpoint(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")