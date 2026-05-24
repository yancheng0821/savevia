from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api import health
from app.clients.card_client import CardServiceClient
from app.clients.user_client import UserServiceClient
from app.core.config import get_settings
from app.core.logging import configure_logging, get_logger
from app.modules.agent.graph import build_agent
from app.modules.chat.router import build_chat_router
from app.modules.chat.service import ChatService


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = get_settings()
    configure_logging(
        log_level=settings.log_level,
        json_output=(settings.environment != "development"),
    )
    log = get_logger("savevia-ai")
    log.info("service_starting", service=settings.service_name, port=settings.service_port)

    # Build per-app singletons
    app.state.user_client = UserServiceClient(base_url=settings.user_service_url)
    app.state.card_client = CardServiceClient(base_url=settings.card_service_url)
    app.state.agent = build_agent()
    app.state.chat_service = ChatService(
        user_client=app.state.user_client,
        card_client=app.state.card_client,
        agent=app.state.agent,
    )

    try:
        yield
    finally:
        from app.core.db import dispose_engine
        from app.core.redis_client import close_redis

        await app.state.user_client.aclose()
        await app.state.card_client.aclose()
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
    app.include_router(build_chat_router(lambda: app.state.chat_service))

    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return app


app = create_app()
