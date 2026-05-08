from apps.ingest.app.config import IngestSettings
from apps.ingest.app.job import run_once
from apps.ingest.app.mlb_client import MLBResponse


class FakeProvider:
    def __init__(self):
        self.calls: list[object] = []

    def fetch_schedule(self):
        self.calls.append("schedule")
        return MLBResponse(
            status_code=200,
            payload={
                "dates": [
                    {
                        "games": [
                            {
                                "gamePk": 662001,
                                "status": {"abstractGameState": "Live", "codedGameState": "I"},
                            }
                        ]
                    }
                ]
            },
            headers={},
        )

    def fetch_game_changes(self, updated_since: str):
        self.calls.append(("changes", updated_since))
        return MLBResponse(status_code=200, payload={"games": [{"gamePk": 662001}]}, headers={})

    def fetch_live_game_feed(self, game_pk: int):
        self.calls.append(("feed", game_pk))
        return MLBResponse(
            status_code=200,
            payload={
                "gamePk": game_pk,
                "liveData": {
                    "plays": {
                        "allPlays": [
                            {
                                "atBatIndex": 1,
                                "result": {"eventType": "single"},
                                "matchup": {"batter": {"id": 660271}},
                            }
                        ]
                    }
                },
            },
            headers={},
        )


class FakeStore:
    def session_factory(self):
        return {"connected": True}


def test_run_once_wires_provider_and_store(monkeypatch):
    settings = IngestSettings(
        mlb_api_url="http://mock:8090",
        database_url="sqlite:///./diamond_departures.db",
        log_level="INFO",
        environment="development",
        request_timeout_seconds=10,
        max_http_retries=2,
        retry_backoff_seconds=0.1,
        provider_source="mlb_stats",
        live_scanner_mode="schedule",
        game_changes_lookback_seconds=30,
    )
    fake_provider = FakeProvider()
    fake_store = FakeStore()

    monkeypatch.setattr("apps.ingest.app.job.load_settings", lambda: settings)
    monkeypatch.setattr("apps.ingest.app.job.build_provider", lambda _settings: fake_provider)
    monkeypatch.setattr("apps.ingest.app.job.init_store", lambda _: fake_store)

    result = run_once()

    assert result["status"] == "ok"
    assert result["schedule_status"] == 200
    assert result["games_scanned"] == [662001]
    assert ("feed", 662001) in fake_provider.calls


def test_run_once_changes_mode_fetches_game_changes(monkeypatch):
    settings = IngestSettings(
        mlb_api_url="http://mock:8090",
        database_url="sqlite:///./diamond_departures.db",
        log_level="INFO",
        environment="development",
        request_timeout_seconds=10,
        max_http_retries=2,
        retry_backoff_seconds=0.1,
        provider_source="mlb_stats",
        live_scanner_mode="changes",
        game_changes_lookback_seconds=30,
    )
    fake_provider = FakeProvider()
    fake_store = FakeStore()

    monkeypatch.setattr("apps.ingest.app.job.load_settings", lambda: settings)
    monkeypatch.setattr("apps.ingest.app.job.build_provider", lambda _settings: fake_provider)
    monkeypatch.setattr("apps.ingest.app.job.init_store", lambda _: fake_store)

    result = run_once(updated_since="2026-05-08T11:00:00Z")

    assert result["status"] == "ok"
    assert result["scanner_mode"] == "changes"
    assert result["changed_games"] == [662001]
    assert ("changes", "2026-05-08T11:00:00Z") in fake_provider.calls
