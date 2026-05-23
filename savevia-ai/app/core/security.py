from dataclasses import dataclass

import jwt
from fastapi import HTTPException, Request, status

from app.core.config import get_settings


@dataclass(frozen=True)
class Principal:
    user_id: int
    email: str | None


def _extract_bearer_token(request: Request) -> str:
    auth = request.headers.get("Authorization") or request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing or malformed Authorization header",
        )
    return auth.split(" ", 1)[1].strip()


def current_user(request: Request) -> Principal:
    """FastAPI dependency that verifies the inbound JWT and returns the Principal."""
    token = _extract_bearer_token(request)
    settings = get_settings()
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.PyJWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"invalid token: {e}",
        ) from e

    user_id = claims.get("userId")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token missing userId claim",
        )

    return Principal(user_id=int(user_id), email=claims.get("email"))


def get_raw_token(request: Request) -> str:
    """Returns the raw bearer token (for pass-through to Java services)."""
    return _extract_bearer_token(request)
