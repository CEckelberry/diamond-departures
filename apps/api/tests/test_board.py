from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from apps.api.app.main import create_app


def _sample_rows() -> list[dict[str, object]]:
    now = datetime.now(timezone.utc)
    return [
        {
            "rank": 1,
            "player_id": 660271,
            "player_name": "Fernando Tatis Jr.",
            "team_abbr": "SD",
            "headshot_url": "https://example.test/headshot/660271.png",
            "position": "RF",
            "stat_value": 158.234,
            "refreshed_at": now.isoformat(),
        },
        {
            "rank": 2,
            "player_id": 665487,
            "player_name": "Bobby Witt Jr.",
            "team_abbr": "KC",
            "headshot_url": "https://example.test/headshot/665487.png",
            "position": "SS",
            "stat_value": 152.120,
            "refreshed_at": (now - timedelta(minutes=9)).isoformat(),
        },
    ]


def test_board_returns_ranked_rows_with_player_metadata() -> None:
    app = create_app(board_reader=lambda view, sort: _sample_rows())
    client = TestClient(app)

    response = client.get("/api/board", params={"view": "hitters", "sort": "wRC+"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["view"] == "hitters"
    assert payload["sort"] == "wRC+"
    assert len(payload["entries"]) == 2

    entry = payload["entries"][0]
    assert entry["rank"] == 1
    assert entry["player"]["id"] == 660271
    assert entry["player"]["team_abbr"] == "SD"
    assert entry["freshness"]["age_category"] in {"live", "recent", "stale", "old"}


def test_board_rejects_invalid_view() -> None:
    app = create_app(board_reader=lambda view, sort: _sample_rows())
    client = TestClient(app)

    response = client.get("/api/board", params={"view": "coaches", "sort": "wRC+"})

    assert response.status_code == 400
    assert "invalid view" in response.json()["detail"].lower()


def test_board_rejects_invalid_sort() -> None:
    app = create_app(board_reader=lambda view, sort: _sample_rows())
    client = TestClient(app)

    response = client.get("/api/board", params={"view": "hitters", "sort": "XYZ"})

    assert response.status_code == 400
    assert "invalid sort" in response.json()["detail"].lower()
