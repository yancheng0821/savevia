from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api import health
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(
        log_level=settings.log_level,
        json_output=(settings.environment != "development"),
    )
    log = get_logger("savevia-ai")
    log.info("service_starting", service=settings.service_name, port=settings.service_port)
    try:
        yield
    finally:
        from app.core.db import dispose_engine
        from app.core.redis_client import close_redis

        await dispose_engine()
        await close_redis()
        log.info("service_stopping")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="savevia-ai",
        description="SaveVia AI service",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.environment != "production" else None,
        redoc_url=None,
    )

    app.include_router(health.router)

    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return app


app = create_app()
