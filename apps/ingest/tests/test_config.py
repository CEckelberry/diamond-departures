from apps.ingest.app.config import IngestSettings, load_settings


def test_load_settings_defaults(monkeypatch):
    monkeypatch.delenv("MLB_API_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)

    settings = load_settings()

    assert isinstance(settings, IngestSettings)
    assert settings.mlb_api_url == "http://localhost:8090"
    assert settings.database_url == "sqlite:///./diamond_departures.db"
    assert settings.log_level == "INFO"


def test_load_settings_env_overrides(monkeypatch):
    monkeypatch.setenv("MLB_API_URL", "http://mock:8090")
    monkeypatch.setenv("DATABASE_URL", "postgresql://localhost/dev")
    monkeypatch.setenv("REQUEST_TIMEOUT_SECONDS", "15")
    monkeypatch.setenv("MAX_HTTP_RETRIES", "4")

    settings = load_settings()

    assert settings.mlb_api_url == "http://mock:8090"
    assert settings.database_url == "postgresql://localhost/dev"
    assert settings.request_timeout_seconds == 15
    assert settings.max_http_retries == 4
