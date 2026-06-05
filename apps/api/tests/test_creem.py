from __future__ import annotations

from jose import jwt
from fastapi.testclient import TestClient

from apps.api.app.main import create_app

SECRET = "test-jwt-secret"


def _token(sub: str = "user-uuid-1", email: str = "buyer@example.com") -> str:
    return jwt.encode({"sub": sub, "email": email, "aud": "authenticated"}, SECRET, algorithm="HS256")


def _fake_upsert(user_id, email, name, avatar_url):
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": False}


def _fake_mark_premium(user_id: str) -> None:
    pass  # no-op in tests


def _fake_checkout(product_id: str, user_id: str, email: str, success_url: str) -> str:
    return f"https://creem.io/test-checkout/{user_id}"


def test_checkout_returns_url_for_authenticated_user() -> None:
    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_fake_upsert,
        supabase_jwt_secret=SECRET,
        creem_checkout=_fake_checkout,
        creem_mark_premium=_fake_mark_premium,
        creem_product_id="prod-test",
    )
    client = TestClient(app)

    response = client.post(
        "/api/creem/checkout",
        headers={"Authorization": f"Bearer {_token()}"},
    )

    assert response.status_code == 200
    assert "checkout_url" in response.json()
    assert "creem.io" in response.json()["checkout_url"]


def test_checkout_returns_401_unauthenticated() -> None:
    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_fake_upsert,
        supabase_jwt_secret=SECRET,
        creem_checkout=_fake_checkout,
        creem_mark_premium=_fake_mark_premium,
        creem_product_id="prod-test",
    )
    client = TestClient(app)

    response = client.post("/api/creem/checkout")

    assert response.status_code == 401


def test_webhook_marks_user_premium_on_payment_succeeded() -> None:
    marked: list[str] = []

    def _capture_mark(user_id: str) -> None:
        marked.append(user_id)

    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_fake_upsert,
        supabase_jwt_secret=SECRET,
        creem_checkout=_fake_checkout,
        creem_mark_premium=_capture_mark,
        creem_product_id="prod-test",
        creem_webhook_secret="whsec-test",
    )
    client = TestClient(app)

    import hmac, hashlib, json
    body = json.dumps({"type": "payment.succeeded", "data": {"metadata": {"user_id": "user-uuid-1"}}})
    sig = hmac.new("whsec-test".encode(), body.encode(), hashlib.sha256).hexdigest()

    response = client.post(
        "/api/creem/webhook",
        content=body,
        headers={"content-type": "application/json", "creem-signature": sig},
    )

    assert response.status_code == 200
    assert "user-uuid-1" in marked


def test_webhook_returns_400_on_bad_signature() -> None:
    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_fake_upsert,
        supabase_jwt_secret=SECRET,
        creem_checkout=_fake_checkout,
        creem_mark_premium=_fake_mark_premium,
        creem_product_id="prod-test",
        creem_webhook_secret="whsec-real",
    )
    client = TestClient(app)

    response = client.post(
        "/api/creem/webhook",
        json={"type": "payment.succeeded", "data": {"metadata": {"user_id": "x"}}},
        headers={"creem-signature": "bad-sig"},
    )

    assert response.status_code == 400
