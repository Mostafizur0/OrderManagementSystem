import time
from prometheus_client import Counter, Histogram, Gauge
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total number of HTTP requests",
    ["method", "endpoint", "status"],
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
)

TOTAL_ACTIVE_REQUESTS = Gauge(
    "http_active_requests_total", "Total number of active HTTP requests"
)

TOTAL_PAYMENT_ERRORS = Counter(
    "payment_errors_total",
    "Total number of payment errors",
    ["error_type"],
)

AUTH_TOKENS_ISSUED_TOTAL = Counter(
    "auth_tokens_issued_total",
    "Total number of authentication tokens issued",
    ["token_type", "endpoint"],
)

DATABASE_QUERY_DURATION = Histogram(
    "database_query_duration_seconds",
    "Database query duration in seconds",
    ["query_type"],
    buckets=[0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)


class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp):
        super().__init__(app)

    async def dispatch(self, request, call_next):
        TOTAL_ACTIVE_REQUESTS.inc()

        start_time = time.perf_counter()
        endpoint = request.url.path

        try:
            response = await call_next(request)

            duration = time.perf_counter() - start_time
            REQUEST_DURATION.labels(
                method=request.method, endpoint=endpoint
            ).observe(duration)

            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=endpoint,
                status=response.status_code,
            ).inc()

            return response

        except Exception as _:  # noqa
            duration = time.perf_counter() - start_time
            REQUEST_DURATION.labels(
                method=request.method, endpoint=endpoint
            ).observe(duration)

            REQUEST_COUNT.labels(
                method=request.method, endpoint=endpoint, status=500
            ).inc()

            raise
        finally:
            TOTAL_ACTIVE_REQUESTS.dec()
