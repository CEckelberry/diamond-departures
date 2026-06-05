from __future__ import annotations

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


def _make_app(upsert=None):
    store: list[dict] = []

    def _list(user_id: str) -> list[dict]:
        return [e for e in store if e["user_id"] == user_id]

    def _add(user_id: str, player_id: int) -> None:
        if not any(e["user_id"] == user_id and e["player_id"] == player_id for e in store):
            store.append({"user_id": user_id, "player_id": player_id})

    def _remove(user_id: str, player_id: int) -> bool:
        before = len(store)
        store[:] = [e for e in store if not (e["user_id"] == user_id and e["player_id"] == player_id)]
        return len(store) < before

    return create_app(
        db_health_check=lambda: True,
        user_upsert=upsert or _upsert,
        supabase_jwt_secret=SECRET,
        watchlist_lister=_list,
        watchlist_adder=_add,
        watchlist_remover=_remove,
    ), store


def test_get_watchlist_returns_entries() -> None:
    app, store = _make_app()
    store.append({"user_id": "u1", "player_id": 660271})
    client = TestClient(app)
    response = client.get("/api/watchlist", headers={"Authorization": f"Bearer {_token()}"})
    assert response.status_code == 200
    assert response.json() == [{"user_id": "u1", "player_id": 660271}]


def test_add_to_watchlist() -> None:
    app, store = _make_app()
    client = TestClient(app)
    response = client.post("/api/watchlist", json={"player_id": 660271}, headers={"Authorization": f"Bearer {_token()}"})
    assert response.status_code == 200
    assert any(e["player_id"] == 660271 for e in store)


def test_remove_from_watchlist() -> None:
    app, store = _make_app()
    store.append({"user_id": "u1", "player_id": 660271})
    client = TestClient(app)
    response = client.delete("/api/watchlist/660271", headers={"Authorization": f"Bearer {_token()}"})
    assert response.status_code == 200
    assert not any(e["player_id"] == 660271 for e in store)


def test_watchlist_requires_premium() -> None:
    app, _ = _make_app(upsert=_upsert_free)
    client = TestClient(app)
    response = client.get("/api/watchlist", headers={"Authorization": f"Bearer {_token()}"})
    assert response.status_code == 403


def test_watchlist_requires_auth() -> None:
    app, _ = _make_app()
    client = TestClient(app)
    response = client.get("/api/watchlist")
    assert response.status_code == 401
