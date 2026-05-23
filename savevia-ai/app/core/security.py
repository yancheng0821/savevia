from dataclasses import dataclass

import jwt
from fastapi import HTTPException, Request, status

from app.core.config import get_settings
from app.core.logging import get_logger

_log = get_logger("savevia-ai.security")


@dataclass(frozen=True)
class Principal:
    user_id: int
    email: str | None


def _extract_bearer_token(request: Request) -> str:
    """Strict RFC 6750 bearer parsing: 'Bearer <token>' with single whitespace separator."""
    auth = request.headers.get("Authorization") or request.headers.get("authorization")
    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing Authorization header",
        )
    parts = auth.split(None, 1)  # split on any whitespace, max 2 pieces
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="malformed Authorization header",
        )
    return parts[1].strip()


def current_user(request: Request) -> Principal:
    """FastAPI dependency that verifies the inbound JWT and returns the Principal.

    Reads userId from the standard `sub` claim (matches Java JwtService).
    Requires both `sub` and `exp` claims to be present.
    """
    token = _extract_bearer_token(request)
    settings = get_settings()
    try:
        claims = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
            options={"require": ["sub", "exp"]},
        )
    except jwt.PyJWTError as e:
        _log.warning("jwt_decode_failed", error=str(e), error_type=type(e).__name__)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        ) from e

    sub = claims.get("sub")
    try:
        user_id = int(sub)
    except (TypeError, ValueError) as e:
        _log.warning("jwt_sub_not_numeric", sub=sub)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        ) from e

    return Principal(user_id=user_id, email=claims.get("email"))


def get_raw_token(request: Request) -> str:
    """Returns the raw bearer token (for pass-through to Java services).

    The caller MUST NOT trust this token — it is forwarded as-is and the
    downstream Java service re-verifies it. This helper exists only for
    that pass-through pattern.
    """
    return _extract_bearer_token(request)
