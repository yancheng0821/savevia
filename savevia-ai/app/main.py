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
from app.modules.memory.extraction_chain import build_extraction_chain
from app.modules.memory.extraction_service import ExtractionService
from app.modules.optimizer_api.router import build_optimizer_router
from app.modules.optimizer_api.service import CashbackOptimizerService
from app.modules.saved_results.router import router as saved_results_router
from app.modules.transactions.categorization import CategorizationService
from app.modules.transactions.router import (
    build_analysis_service,
    build_transactions_router,
)
from app.repositories.merchant_category_repository import MerchantCategoryRepository


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
    app.state.extraction_chain = build_extraction_chain()
    app.state.extraction_service = ExtractionService(
        user_client=app.state.user_client,
        chain=app.state.extraction_chain,
    )
    app.state.chat_service = ChatService(
        user_client=app.state.user_client,
        card_client=app.state.card_client,
        agent=app.state.agent,
        extraction_service=app.state.extraction_service,
    )
    app.state.optimizer_service = CashbackOptimizerService(
        card_client=app.state.card_client,
        user_client=app.state.user_client,
    )

    # Categorization patterns are loaded once at startup; refresh via the
    # admin debug endpoint (Phase 4 backlog) if rules change.
    from app.core.db import get_session_factory

    factory = get_session_factory()
    async with factory() as boot_session:
        app.state.categorization_service = CategorizationService(
            merchant_repository=MerchantCategoryRepository(boot_session),
        )
        try:
            await app.state.categorization_service.refresh_patterns()
        except Exception as exc:  # noqa: BLE001 — DB may be unreachable in tests
            log.warning("categorization_patterns_load_failed", error=str(exc))

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
    app.include_router(saved_results_router)
    app.include_router(build_optimizer_router(lambda: app.state.optimizer_service))
    app.include_router(build_transactions_router(
        lambda session: build_analysis_service(
            session=session,
            card_client=app.state.card_client,
            categorization=app.state.categorization_service,
        ),
    ))

    @app.get("/", include_in_schema=False)
    async def root() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return app


app = create_app()
