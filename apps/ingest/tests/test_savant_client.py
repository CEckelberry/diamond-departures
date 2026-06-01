from __future__ import annotations
from unittest.mock import MagicMock
from apps.ingest.app.savant_client import SavantClient
from apps.ingest.app.mlb_client import MLBResponse


def _mock_client(payload: dict, status: int = 200) -> SavantClient:
    response = MLBResponse(status_code=status, payload=payload, headers={})
    client = SavantClient(base_url="https://baseballsavant.mlb.com")
    client._mlb_client.request_fn = MagicMock(return_value=response)
    return client


def test_fetch_statcast_returns_list():
    client = _mock_client({"players": [
        {"player_id": "660271", "barrel_batted_rate": 0.15,
         "hard_hit_percent": 0.52, "avg_hit_speed": 95.2,
         "xwoba": 0.410, "xba": 0.285}
    ]})
    result = client.fetch_statcast(year=2026)
    assert len(result) == 1
    assert result[0]["player_id"] == 660271
    assert result[0]["barrel_pct"] == 0.15


def test_fetch_statcast_empty_on_missing_key():
    client = _mock_client({})
    result = client.fetch_statcast(year=2026)
    assert result == []
