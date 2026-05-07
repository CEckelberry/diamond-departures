from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.app.main import create_app


def _player_detail(player_id: int) -> dict[str, object] | None:
    if player_id != 660271:
        return None
    return {
        "player": {
            "id": 660271,
            "name": "Fernando Tatis Jr.",
            "team_abbr": "SD",
            "headshot_url": "https://example.test/headshot/660271.png",
            "position": "RF",
        },
        "season_totals": {
            "games": 142,
            "plate_appearances": 641,
            "fwar": 6.1,
        },
        "stat_line": {
            "wRC+": 158.2,
            "OPS": 0.925,
        },
        "recent_games": [
            {"game_date": "2026-04-05", "opponent": "LAD", "result": "W", "wRC+": 181.4},
            {"game_date": "2026-04-06", "opponent": "LAD", "result": "L", "wRC+": 132.9},
        ],
    }


def _player_history(player_id: int, stat: str) -> list[dict[str, object]] | None:
    if player_id != 660271:
        return None
    if stat not in {"wRC+", "OPS"}:
        return []
    return [
        {"timestamp": "2026-04-01T00:00:00+00:00", "value": 120.1},
        {"timestamp": "2026-04-03T00:00:00+00:00", "value": 145.3},
        {"timestamp": "2026-04-05T00:00:00+00:00", "value": 158.2},
    ]


def test_player_detail_returns_full_payload() -> None:
    app = create_app(
        player_detail_reader=_player_detail,
        player_history_reader=_player_history,
    )
    client = TestClient(app)

    response = client.get("/api/players/660271")

    assert response.status_code == 200
    payload = response.json()
    assert payload["player"]["id"] == 660271
    assert "season_totals" in payload
    assert "stat_line" in payload
    assert len(payload["recent_games"]) == 2


def test_player_detail_unknown_player_returns_404() -> None:
    app = create_app(
        player_detail_reader=_player_detail,
        player_history_reader=_player_history,
    )
    client = TestClient(app)

    response = client.get("/api/players/123")

    assert response.status_code == 404


def test_player_history_returns_time_ordered_points() -> None:
    app = create_app(
        player_detail_reader=_player_detail,
        player_history_reader=_player_history,
    )
    client = TestClient(app)

    response = client.get("/api/players/660271/history", params={"stat": "wRC+"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["player_id"] == 660271
    assert payload["stat"] == "wRC+"
    assert [point["timestamp"] for point in payload["points"]] == [
        "2026-04-01T00:00:00+00:00",
        "2026-04-03T00:00:00+00:00",
        "2026-04-05T00:00:00+00:00",
    ]


def test_player_history_missing_stat_returns_400() -> None:
    app = create_app(
        player_detail_reader=_player_detail,
        player_history_reader=_player_history,
    )
    client = TestClient(app)

    response = client.get("/api/players/660271/history")

    assert response.status_code == 400


def test_player_history_invalid_stat_returns_400() -> None:
    app = create_app(
        player_detail_reader=_player_detail,
        player_history_reader=_player_history,
    )
    client = TestClient(app)

    response = client.get("/api/players/660271/history", params={"stat": "ERA"})

    assert response.status_code == 400


def test_player_history_unknown_player_returns_404() -> None:
    app = create_app(
        player_detail_reader=_player_detail,
        player_history_reader=_player_history,
    )
    client = TestClient(app)

    response = client.get("/api/players/123/history", params={"stat": "wRC+"})

    assert response.status_code == 404
