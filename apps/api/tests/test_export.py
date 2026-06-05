from __future__ import annotations

from datetime import datetime, timezone
from jose import jwt
from fastapi.testclient import TestClient
from apps.api.app.main import create_app

SECRET = "test-secret"

def _token() -> str:
    return jwt.encode({"sub": "u1", "email": "u@test.com", "aud": "authenticated"}, SECRET, algorithm="HS256")

def _upsert(user_id, email, name, avatar_url):
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": True}

def _upsert_free(user_id, email, name, avatar_url):
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": False}

def _sample_rows():
    now = datetime.now(timezone.utc)
    return [{"rank": 1, "player_id": 660271, "player_name": "Fernando Tatis Jr.", "team_abbr": "SD", "headshot_url": "", "position": "RF", "stat_value": 158.234, "refreshed_at": now.isoformat()}]


def test_csv_export_returns_csv_for_premium_user() -> None:
    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_upsert,
        supabase_jwt_secret=SECRET,
        board_reader=lambda view, sort, season=2026: _sample_rows(),
    )
    client = TestClient(app)
    response = client.get(
        "/api/board/export",
        params={"view": "hitters", "sort": "wRC+"},
        headers={"Authorization": f"Bearer {_token()}"},
    )
    assert response.status_code == 200
    assert "text/csv" in response.headers["content-type"]
    assert "attachment" in response.headers.get("content-disposition", "")
    assert "Fernando Tatis Jr." in response.text


def test_csv_export_requires_premium() -> None:
    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_upsert_free,
        supabase_jwt_secret=SECRET,
        board_reader=lambda view, sort, season=2026: _sample_rows(),
    )
    client = TestClient(app)
    response = client.get(
        "/api/board/export",
        params={"view": "hitters", "sort": "wRC+"},
        headers={"Authorization": f"Bearer {_token()}"},
    )
    assert response.status_code == 403
