from __future__ import annotations

from .config import IngestSettings
from .mlb_client import MLBApiClient, MLBResponse


class LiveDataProvider:
    def fetch_schedule(self) -> MLBResponse:
        raise NotImplementedError

    def fetch_game_changes(self, updated_since: str) -> MLBResponse:
        raise NotImplementedError

    def fetch_live_game_feed(self, game_pk: int) -> MLBResponse:
        raise NotImplementedError


class MLBStatsLiveProvider(LiveDataProvider):
    def __init__(self, client) -> None:
        self.client = client

    def fetch_schedule(self) -> MLBResponse:
        return self.client.get_json("/api/v1/schedule")

    def fetch_game_changes(self, updated_since: str) -> MLBResponse:
        return self.client.get_json(f"/api/v1/game/changes?updatedSince={updated_since}")

    def fetch_live_game_feed(self, game_pk: int) -> MLBResponse:
        return self.client.get_json(f"/api/v1.1/game/{game_pk}/feed/live")


def build_provider(settings: IngestSettings) -> LiveDataProvider:
    source = settings.provider_source.lower().strip()
    if source != "mlb_stats":
        raise ValueError(f"Unsupported provider source '{settings.provider_source}'")

    client = MLBApiClient(
        base_url=settings.mlb_api_url,
        timeout_seconds=settings.request_timeout_seconds,
        max_retries=settings.max_http_retries,
        retry_backoff_seconds=settings.retry_backoff_seconds,
    )
    return MLBStatsLiveProvider(client)
