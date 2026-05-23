from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict[str, str]:
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.service_name,
        "version": "0.1.0",
        "environment": settings.environment,
    }


@router.get("/ready")
async def ready() -> dict[str, str]:
    """Liveness probe placeholder. Wired to DB/Redis pings in Task 5 and Task 6."""
    return {"status": "ready"}
