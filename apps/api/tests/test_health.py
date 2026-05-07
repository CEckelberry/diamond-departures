from __future__ import annotations

from fastapi.testclient import TestClient

from apps.api.app.main import create_app


def test_health_ok_when_db_is_reachable() -> None:
    app = create_app(db_health_check=lambda: True)
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_degraded_when_db_is_unreachable() -> None:
    app = create_app(db_health_check=lambda: False)
    client = TestClient(app)

    response = client.get("/api/health")

    assert response.status_code == 503
    assert response.json()["status"] == "degraded"
    assert response.json()["checks"]["database"] == "unreachable"
