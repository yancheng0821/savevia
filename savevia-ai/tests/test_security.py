import time

import jwt
import pytest
from fastapi import HTTPException, Request

from app.core.config import get_settings


def _build_request(headers: dict[str, str]) -> Request:
    scope = {
        "type": "http",
        "headers": [
            (k.lower().encode(), v.encode()) for k, v in headers.items()
        ],
        "method": "GET",
        "path": "/",
    }
    return Request(scope)


def _make_token(claims: dict, secret: str | None = None, alg: str = "HS256") -> str:
    settings = get_settings()
    return jwt.encode(claims, secret or settings.jwt_secret, algorithm=alg)


def test_decode_valid_token_returns_principal():
    from app.core.security import current_user

    token = _make_token({"userId": 42, "email": "u@example.com", "exp": int(time.time()) + 3600})
    req = _build_request({"Authorization": f"Bearer {token}"})

    principal = current_user(req)
    assert principal.user_id == 42
    assert principal.email == "u@example.com"


def test_missing_header_raises_401():
    from app.core.security import current_user

    req = _build_request({})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_malformed_header_raises_401():
    from app.core.security import current_user

    req = _build_request({"Authorization": "NotBearer xxx"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_expired_token_raises_401():
    from app.core.security import current_user

    token = _make_token({"userId": 1, "exp": int(time.time()) - 10})
    req = _build_request({"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_wrong_secret_raises_401():
    from app.core.security import current_user

    token = _make_token(
        {"userId": 1, "exp": int(time.time()) + 3600},
        secret="some-other-wrong-secret-that-is-also-32-chars-long",
    )
    req = _build_request({"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_missing_user_id_raises_401():
    from app.core.security import current_user

    token = _make_token({"email": "x@x.com", "exp": int(time.time()) + 3600})
    req = _build_request({"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401
