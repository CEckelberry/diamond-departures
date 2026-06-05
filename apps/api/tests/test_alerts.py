from __future__ import annotations

import uuid
from jose import jwt
from fastapi.testclient import TestClient
from apps.api.app.main import create_app

SECRET = "test-secret"

def _token() -> str:
    return jwt.encode({"sub": "u1", "email": "u@test.com", "aud": "authenticated"}, SECRET, algorithm="HS256")

def _upsert(user_id, email, name, avatar_url):
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": True}


def _make_app():
    store: list[dict] = []

    def _list(user_id: str) -> list[dict]:
        return [a for a in store if a["user_id"] == user_id]

    def _create(user_id: str, player_id: int, stat_name: str, threshold: float, direction: str) -> dict:
        alert = {"id": str(uuid.uuid4()), "user_id": user_id, "player_id": player_id,
                 "stat_name": stat_name, "threshold": threshold, "direction": direction}
        store.append(alert)
        return alert

    def _delete(alert_id: str, user_id: str) -> bool:
        before = len(store)
        store[:] = [a for a in store if not (a["id"] == alert_id and a["user_id"] == user_id)]
        return len(store) < before

    return create_app(
        db_health_check=lambda: True,
        user_upsert=_upsert,
        supabase_jwt_secret=SECRET,
        alert_lister=_list,
        alert_creator=_create,
        alert_deleter=_delete,
    ), store


def test_create_and_list_alerts() -> None:
    app, _ = _make_app()
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {_token()}"}
    client.post("/api/alerts", json={"player_id": 660271, "stat_name": "wRC+", "threshold": 150.0, "direction": "up"}, headers=headers)
    response = client.get("/api/alerts", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["stat_name"] == "wRC+"


def test_delete_alert() -> None:
    app, store = _make_app()
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {_token()}"}
    resp = client.post("/api/alerts", json={"player_id": 660271, "stat_name": "ERA", "threshold": 3.0, "direction": "down"}, headers=headers)
    alert_id = resp.json()["id"]
    client.delete(f"/api/alerts/{alert_id}", headers=headers)
    assert not any(a["id"] == alert_id for a in store)


def test_alerts_require_premium() -> None:
    def _free(user_id, email, name, avatar_url):
        return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": False}
    app = create_app(db_health_check=lambda: True, user_upsert=_free, supabase_jwt_secret=SECRET)
    client = TestClient(app)
    response = client.get("/api/alerts", headers={"Authorization": f"Bearer {_token()}"})
    assert response.status_code == 403
