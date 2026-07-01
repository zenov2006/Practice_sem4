from prometheus_client import Counter, Histogram, generate_latest, REGISTRY
from fastapi import FastAPI, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

# Метрики
http_requests_total = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'path', 'status_code']
)

http_request_duration_seconds = Histogram(
    'http_request_duration_seconds',
    'HTTP request duration in seconds',
    ['method', 'path']
)


class PrometheusMiddleware(BaseHTTPMiddleware):
    """
    Middleware для сбора метрик HTTP запросов.
    """

    async def dispatch(self, request, call_next):
        start_time = time.perf_counter()

        response = await call_next(request)

        duration = time.perf_counter() - start_time
        path = request.url.path
        method = request.method

        http_requests_total.labels(
            method=method,
            path=path,
            status_code=response.status_code
        ).inc()

        http_request_duration_seconds.labels(
            method=method,
            path=path
        ).observe(duration)

        return response


def register_metrics_endpoint(app: FastAPI) -> None:
    """
    Регистрирует эндпоинт /metrics для Prometheus.
    """

    @app.get("/metrics")
    async def metrics():
        return Response(
            content=generate_latest(REGISTRY),
            media_type="text/plain"
        )