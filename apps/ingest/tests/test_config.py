from apps.ingest.app.config import IngestSettings, load_settings


def test_load_settings_defaults(monkeypatch):
    monkeypatch.delenv("MLB_API_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    monkeypatch.delenv("PROVIDER_SOURCE", raising=False)
    monkeypatch.delenv("LIVE_SCANNER_MODE", raising=False)
    monkeypatch.delenv("SCANNER_CHECKPOINT_PATH", raising=False)
    monkeypatch.delenv("RECONCILE_EVERY_N_SCANS", raising=False)

    settings = load_settings()

    assert isinstance(settings, IngestSettings)
    assert settings.mlb_api_url == "http://localhost:8090"
    assert settings.database_url == "sqlite:///./diamond_departures.db"
    assert settings.log_level == "INFO"
    assert settings.provider_source == "mlb_stats"
    assert settings.live_scanner_mode == "changes"
    assert settings.scanner_checkpoint_path == "orchestration/state/ingest-scanner-checkpoint.json"
    assert settings.reconcile_every_n_scans == 10


def test_load_settings_env_overrides(monkeypatch):
    monkeypatch.setenv("MLB_API_URL", "http://mock:8090")
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/dev")
    monkeypatch.setenv("REQUEST_TIMEOUT_SECONDS", "15")
    monkeypatch.setenv("MAX_HTTP_RETRIES", "4")
    monkeypatch.setenv("PROVIDER_SOURCE", "mlb_stats")
    monkeypatch.setenv("LIVE_SCANNER_MODE", "schedule")
    monkeypatch.setenv("GAME_CHANGES_LOOKBACK_SECONDS", "90")
    monkeypatch.setenv("SCANNER_CHECKPOINT_PATH", "tmp/checkpoint.json")
    monkeypatch.setenv("RECONCILE_EVERY_N_SCANS", "3")

    settings = load_settings()

    assert settings.mlb_api_url == "http://mock:8090"
    assert settings.database_url == "postgresql://localhost/dev"
    assert settings.request_timeout_seconds == 15
    assert settings.max_http_retries == 4
    assert settings.provider_source == "mlb_stats"
    assert settings.live_scanner_mode == "schedule"
    assert settings.game_changes_lookback_seconds == 90
    assert settings.scanner_checkpoint_path == "tmp/checkpoint.json"
    assert settings.reconcile_every_n_scans == 3
