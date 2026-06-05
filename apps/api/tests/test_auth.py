# apps/api/tests/test_auth.py
from __future__ import annotations

from jose import jwt
from fastapi.testclient import TestClient

from apps.api.app.main import create_app


def _make_token(secret: str, sub: str = "user-uuid-1", email: str = "test@example.com", extra: dict | None = None) -> str:
    claims = {"sub": sub, "email": email, "aud": "authenticated", **(extra or {})}
    return jwt.encode(claims, secret, algorithm="HS256")


def _fake_upsert(user_id: str, email: str, name: str | None, avatar_url: str | None) -> dict:
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": False}


SECRET = "test-jwt-secret"


def test_me_returns_user_when_jwt_valid() -> None:
    app = create_app(db_health_check=lambda: True, user_upsert=_fake_upsert, supabase_jwt_secret=SECRET)
    client = TestClient(app)
    token = _make_token(SECRET)

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["is_premium"] is False


def test_me_returns_401_when_no_token() -> None:
    app = create_app(db_health_check=lambda: True, user_upsert=_fake_upsert, supabase_jwt_secret=SECRET)
    client = TestClient(app)

    response = client.get("/api/auth/me")

    assert response.status_code == 401


def test_me_returns_401_when_token_invalid() -> None:
    app = create_app(db_health_check=lambda: True, user_upsert=_fake_upsert, supabase_jwt_secret=SECRET)
    client = TestClient(app)

    response = client.get("/api/auth/me", headers={"Authorization": "Bearer not-a-real-token"})

    assert response.status_code == 401


def test_me_returns_401_when_wrong_secret() -> None:
    app = create_app(db_health_check=lambda: True, user_upsert=_fake_upsert, supabase_jwt_secret=SECRET)
    client = TestClient(app)
    token = _make_token("wrong-secret")

    response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 401
