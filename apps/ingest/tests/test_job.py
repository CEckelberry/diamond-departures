from apps.ingest.app.config import IngestSettings
from apps.ingest.app.job import run_once


class FakeClient:
    def __init__(self):
        self.calls = []

    def get_json(self, path: str):
        self.calls.append(path)
        return type("Resp", (), {"status_code": 200, "payload": {"dates": []}})()


class FakeStore:
    def session_factory(self):
        return {"connected": True}


def test_run_once_wires_config_client_and_store(monkeypatch):
    settings = IngestSettings(
        mlb_api_url="http://mock:8090",
        database_url="sqlite:///./diamond_departures.db",
        log_level="INFO",
        environment="development",
        request_timeout_seconds=10,
        max_http_retries=2,
        retry_backoff_seconds=0.1,
    )
    fake_client = FakeClient()
    fake_store = FakeStore()

    monkeypatch.setattr("apps.ingest.app.job.load_settings", lambda: settings)
    monkeypatch.setattr("apps.ingest.app.job.MLBApiClient", lambda **_: fake_client)
    monkeypatch.setattr("apps.ingest.app.job.init_store", lambda _: fake_store)

    result = run_once()

    assert result["status"] == "ok"
    assert result["schedule_status"] == 200
    assert fake_client.calls == ["/api/v1/schedule"]
