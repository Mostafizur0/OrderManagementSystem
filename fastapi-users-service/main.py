import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from prometheus_client import REGISTRY, make_asgi_app, Gauge
import psutil

from app.core.settings import settings
from app.routes import users as users_router
from app.routes.payments import payment_router
from app.routes.auth import router as auth_router
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.metrics_middleware import MetricsMiddleware
from app.middleware.register_exceptions import RegisterExceptionsMiddleware
from app.utils.logger import setup_logger
from app.utils.os_metrics import update_system_metrics


logs_dir = Path("logs")
logs_dir.mkdir(exist_ok=True)

logger = setup_logger(
    name=settings.LOGGER_NAME, log_level="INFO", log_file=settings.LOGGER_PATH
)

app = FastAPI(
    title="FastAPI Users Service",
    description="A FastAPI service for managing users",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
RegisterExceptionsMiddleware(app)
app.add_middleware(MetricsMiddleware)
app.add_middleware(LoggingMiddleware)

app.include_router(users_router.router, prefix="/api/v1")
app.include_router(payment_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "FastAPI Users Service",
        "version": "1.0.0",
    }


@app.get("/")
async def root():
    """
    Root endpoint
    """
    logger.info("Root endpoint accessed")
    return {
        "message": "Welcome to FastAPI Users Service",
        "docs": "/docs",
        "health": "/health",
        "metrics": "/metrics",
    }


@app.on_event("startup")
async def start_metric_updater():
    async def run():
        while True:
            update_system_metrics()
            await asyncio.sleep(5)

    asyncio.create_task(run())


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI Users Service")
    uvicorn.run(
        "main:app", host="0.0.0.0", port=8000, reload=True, log_level="info"
    )
