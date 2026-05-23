from fastapi import APIRouter, Depends, status
from fastapi.responses import JSONResponse
from redis.asyncio import Redis
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.db import get_db
from app.core.redis_client import get_redis

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
async def ready(
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
) -> JSONResponse:
    """Readiness probe — verifies DB + Redis connectivity."""
    db_ok = False
    redis_ok = False
    errors: dict[str, str] = {}

    try:
        await db.execute(text("SELECT 1"))
        db_ok = True
    except Exception as e:
        errors["db"] = str(e)

    try:
        pong = await redis.ping()
        redis_ok = bool(pong)
    except Exception as e:
        errors["redis"] = str(e)

    if db_ok and redis_ok:
        return JSONResponse({"status": "ready", "db": "ok", "redis": "ok"})

    return JSONResponse(
        {
            "status": "not_ready",
            "db": "ok" if db_ok else "error",
            "redis": "ok" if redis_ok else "error",
            "errors": errors,
        },
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    )
