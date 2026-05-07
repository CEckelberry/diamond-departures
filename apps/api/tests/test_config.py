from __future__ import annotations

from apps.api.app.config import ApiSettings, load_settings


def test_load_settings_from_environment(monkeypatch) -> None:
    monkeypatch.setenv("PORT", "9123")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("DATABASE_URL", "postgresql://diamond:diamond@localhost:5432/diamond")

    settings = load_settings()

    assert isinstance(settings, ApiSettings)
    assert settings.port == 9123
    assert settings.log_level == "DEBUG"
    assert settings.database_url.endswith("/diamond")
