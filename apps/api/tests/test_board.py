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
    app = create_app(board_reader=lambda view, sort, season=2026: _sample_rows())
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
    app = create_app(board_reader=lambda view, sort, season=2026: _sample_rows())
    client = TestClient(app)

    response = client.get("/api/board", params={"view": "coaches", "sort": "wRC+"})

    assert response.status_code == 400
    assert "invalid view" in response.json()["detail"].lower()


def test_board_rejects_invalid_sort() -> None:
    app = create_app(board_reader=lambda view, sort, season=2026: _sample_rows())
    client = TestClient(app)

    response = client.get("/api/board", params={"view": "hitters", "sort": "XYZ"})

    assert response.status_code == 400
    assert "invalid sort" in response.json()["detail"].lower()


def test_valid_sorts_includes_statcast():
    from apps.api.app.board import VALID_SORTS
    for stat in ("xBA", "barrel_pct", "hard_hit_pct", "exit_velocity"):
        assert stat in VALID_SORTS, f"{stat} missing from VALID_SORTS"


def test_board_reader_filters_by_season(monkeypatch):
    """postgres_board_reader passes season to the SQL query."""
    from unittest.mock import MagicMock, patch
    from apps.api.app.store import postgres_board_reader
    mock_rows = [{"rank": 1, "player_id": 1, "player_name": "X",
                  "team_abbr": "LAD", "headshot_url": None,
                  "position": "DH", "stat_value": 1.0,
                  "refreshed_at": "2026-06-01T00:00:00+00:00",
                  "additional_stats": {}}]
    with patch("psycopg2.connect") as mock_conn:
        mock_cur = MagicMock()
        mock_cur.__enter__ = lambda s: s
        mock_cur.__exit__ = MagicMock(return_value=False)
        mock_cur.fetchall.return_value = mock_rows
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cur
        reader = postgres_board_reader("postgresql://fake")
        reader("hitters", "wRC+", season=2025)
        call_args = mock_cur.execute.call_args
        assert "2025" in str(call_args) or 2025 in call_args[0][1]
