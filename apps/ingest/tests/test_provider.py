from apps.ingest.app.config import IngestSettings
from apps.ingest.app.mlb_client import MLBResponse
from apps.ingest.app.provider import MLBStatsLiveProvider, build_provider
from apps.ingest.app.schedule import extract_changed_game_ids


class FakeClient:
    def __init__(self):
        self.calls = []

    def get_json(self, path: str):
        self.calls.append(path)
        return MLBResponse(status_code=200, payload={}, headers={})


def test_mlb_provider_hits_expected_paths() -> None:
    client = FakeClient()
    provider = MLBStatsLiveProvider(client)

    provider.fetch_schedule()
    provider.fetch_game_changes("2026-05-08T11:00:00Z")
    provider.fetch_live_game_feed(662001)

    assert client.calls == [
        "/api/v1/schedule",
        "/api/v1/game/changes?updatedSince=2026-05-08T11:00:00Z",
        "/api/v1.1/game/662001/feed/live",
    ]


def test_extract_changed_game_ids_supports_common_payload_shapes() -> None:
    payload = {
        "games": [
            {"gamePk": 662001},
            {"gamePk": "662002"},
            {"gamePk": None},
        ]
    }

    assert extract_changed_game_ids(payload) == [662001, 662002]


def test_build_provider_for_mlb_stats() -> None:
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
        scanner_checkpoint_path="orchestration/state/ingest-scanner-checkpoint.json",
        reconcile_every_n_scans=10,
    )

    provider = build_provider(settings)
    assert isinstance(provider, MLBStatsLiveProvider)
