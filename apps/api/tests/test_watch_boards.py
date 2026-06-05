from __future__ import annotations

import uuid
from jose import jwt
from fastapi.testclient import TestClient
from apps.api.app.main import create_app

SECRET = "test-secret"

def _token(sub: str = "u1") -> str:
    return jwt.encode({"sub": sub, "email": "u@test.com", "aud": "authenticated"}, SECRET, algorithm="HS256")

def _upsert(user_id, email, name, avatar_url):
    return {"id": user_id, "email": email, "name": name, "avatar_url": avatar_url, "is_premium": True}


def _make_app():
    boards: dict[str, dict] = {}
    board_players: dict[str, list[int]] = {}

    def _list_boards(user_id: str) -> list[dict]:
        return [b for b in boards.values() if b["user_id"] == user_id]

    def _create_board(user_id: str, name: str) -> dict:
        bid = str(uuid.uuid4())
        boards[bid] = {"id": bid, "user_id": user_id, "name": name}
        board_players[bid] = []
        return boards[bid]

    def _get_board(board_id: str, user_id: str) -> dict | None:
        b = boards.get(board_id)
        if not b or b["user_id"] != user_id:
            return None
        return {**b, "players": board_players.get(board_id, [])}

    def _rename_board(board_id: str, user_id: str, name: str) -> bool:
        b = boards.get(board_id)
        if not b or b["user_id"] != user_id:
            return False
        b["name"] = name
        return True

    def _delete_board(board_id: str, user_id: str) -> bool:
        b = boards.get(board_id)
        if not b or b["user_id"] != user_id:
            return False
        del boards[board_id]
        return True

    def _add_player(board_id: str, user_id: str, player_id: int) -> bool:
        b = boards.get(board_id)
        if not b or b["user_id"] != user_id:
            return False
        if player_id not in board_players[board_id]:
            board_players[board_id].append(player_id)
        return True

    def _remove_player(board_id: str, user_id: str, player_id: int) -> bool:
        b = boards.get(board_id)
        if not b or b["user_id"] != user_id:
            return False
        board_players[board_id] = [p for p in board_players[board_id] if p != player_id]
        return True

    app = create_app(
        db_health_check=lambda: True,
        user_upsert=_upsert,
        supabase_jwt_secret=SECRET,
        board_lister=_list_boards,
        board_creator=_create_board,
        board_getter=_get_board,
        board_renamer=_rename_board,
        board_deleter=_delete_board,
        board_player_adder=_add_player,
        board_player_remover=_remove_player,
    )
    return app, boards


def test_create_and_list_boards() -> None:
    app, _ = _make_app()
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {_token()}"}
    client.post("/api/watch-boards", json={"name": "My Lineup"}, headers=headers)
    response = client.get("/api/watch-boards", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["name"] == "My Lineup"


def test_get_board_returns_players() -> None:
    app, _ = _make_app()
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {_token()}"}
    create_resp = client.post("/api/watch-boards", json={"name": "A"}, headers=headers)
    bid = create_resp.json()["id"]
    client.post(f"/api/watch-boards/{bid}/players/660271", headers=headers)
    response = client.get(f"/api/watch-boards/{bid}", headers=headers)
    assert response.status_code == 200
    assert 660271 in response.json()["players"]


def test_delete_board() -> None:
    app, boards = _make_app()
    client = TestClient(app)
    headers = {"Authorization": f"Bearer {_token()}"}
    resp = client.post("/api/watch-boards", json={"name": "Gone"}, headers=headers)
    bid = resp.json()["id"]
    client.delete(f"/api/watch-boards/{bid}", headers=headers)
    assert bid not in boards


def test_board_not_found_for_other_user() -> None:
    app, _ = _make_app()
    client = TestClient(app)
    resp = client.post("/api/watch-boards", json={"name": "Mine"}, headers={"Authorization": f"Bearer {_token('u1')}"})
    bid = resp.json()["id"]
    response = client.get(f"/api/watch-boards/{bid}", headers={"Authorization": f"Bearer {_token('u2')}"})
    assert response.status_code == 404
