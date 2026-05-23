import time

import jwt
import pytest
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.testclient import TestClient

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


def _java_shape_claims(user_id: int = 42, email: str = "u@example.com") -> dict:
    now = int(time.time())
    return {
        "sub": str(user_id),  # Java uses subject for userId (stringified)
        "email": email,
        "type": "access",
        "iat": now,
        "exp": now + 3600,
    }


def test_decode_java_shape_token_returns_principal():
    from app.core.security import current_user

    token = _make_token(_java_shape_claims(user_id=42, email="u@x.com"))
    req = _build_request({"Authorization": f"Bearer {token}"})

    principal = current_user(req)
    assert principal.user_id == 42
    assert principal.email == "u@x.com"


def test_missing_header_raises_401():
    from app.core.security import current_user

    req = _build_request({})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_malformed_scheme_raises_401():
    from app.core.security import current_user

    req = _build_request({"Authorization": "NotBearer xxx"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_empty_bearer_raises_401():
    from app.core.security import current_user

    req = _build_request({"Authorization": "Bearer "})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_expired_token_raises_401():
    from app.core.security import current_user

    claims = _java_shape_claims()
    claims["exp"] = int(time.time()) - 10
    token = _make_token(claims)
    req = _build_request({"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_wrong_secret_raises_401():
    from app.core.security import current_user

    token = _make_token(
        _java_shape_claims(),
        secret="some-other-wrong-secret-that-is-also-32-chars-long",
    )
    req = _build_request({"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_missing_sub_claim_raises_401():
    from app.core.security import current_user

    claims = _java_shape_claims()
    del claims["sub"]
    token = _make_token(claims)
    req = _build_request({"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_missing_exp_claim_raises_401():
    from app.core.security import current_user

    claims = _java_shape_claims()
    del claims["exp"]
    token = _make_token(claims)
    req = _build_request({"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_non_numeric_sub_raises_401():
    from app.core.security import current_user

    claims = _java_shape_claims()
    claims["sub"] = "not-a-number"
    token = _make_token(claims)
    req = _build_request({"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_alg_none_token_rejected():
    """Algorithm-confusion attack: HS256-signed token forged with alg=none."""
    from app.core.security import current_user

    token = jwt.encode(_java_shape_claims(), key="", algorithm="none")
    req = _build_request({"Authorization": f"Bearer {token}"})
    with pytest.raises(HTTPException) as exc:
        current_user(req)
    assert exc.value.status_code == 401


def test_email_optional():
    from app.core.security import current_user

    claims = _java_shape_claims()
    del claims["email"]
    token = _make_token(claims)
    req = _build_request({"Authorization": f"Bearer {token}"})

    principal = current_user(req)
    assert principal.user_id == 42
    assert principal.email is None


def test_fastapi_depends_integration_returns_401_not_500():
    """End-to-end: malformed token through FastAPI dep injection yields HTTP 401, not 500."""
    from app.core.security import Principal, current_user

    app = FastAPI()

    @app.get("/protected")
    async def protected(user: Principal = Depends(current_user)) -> dict:
        return {"user_id": user.user_id}

    client = TestClient(app)

    # No header — must be 401
    r = client.get("/protected")
    assert r.status_code == 401

    # Bad token — must be 401 (not 500)
    r = client.get("/protected", headers={"Authorization": "Bearer not-a-jwt"})
    assert r.status_code == 401

    # Valid token — must be 200
    token = _make_token(_java_shape_claims(user_id=99))
    r = client.get("/protected", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200
    assert r.json() == {"user_id": 99}
