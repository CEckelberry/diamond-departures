from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.app.main import create_app


def _season_state() -> dict[str, object]:
    return {
        "mode": "between",
        "next_game_at": "2026-07-01T23:10:00+00:00",
        "current_season": 2026,
    }


def _freshness() -> dict[str, object]:
    return {
        "ingest_runs": [
            {"run_id": "run-001", "started_at": "2026-07-01T22:01:00+00:00", "status": "ok"},
            {"run_id": "run-002", "started_at": "2026-07-01T22:06:00+00:00", "status": "ok"},
        ],
        "schema_drift": {"status": "clean", "last_checked_at": "2026-07-01T22:07:00+00:00"},
        "stats": {
            "wRC+": {"updated_at": "2026-07-01T22:06:00+00:00", "age_seconds": 65},
            "OPS": {"updated_at": "2026-07-01T22:06:00+00:00", "age_seconds": 65},
        },
    }


def test_season_state_contract_and_cache_headers() -> None:
    app = create_app(
        season_state_reader=_season_state,
        freshness_reader=_freshness,
    )
    client = TestClient(app)

    response = client.get("/api/season-state")

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "between"
    assert payload["current_season"] == 2026
    assert "next_game_at" in payload
    assert response.headers["cache-control"] == "public, max-age=300"


def test_freshness_contract_and_no_store_header() -> None:
    app = create_app(
        season_state_reader=_season_state,
        freshness_reader=_freshness,
    )
    client = TestClient(app)

    response = client.get("/api/freshness")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["ingest_runs"]) == 2
    assert payload["schema_drift"]["status"] == "clean"
    assert "wRC+" in payload["stats"]
    assert response.headers["cache-control"] == "no-store"
