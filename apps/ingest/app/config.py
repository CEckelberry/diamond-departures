from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class IngestSettings:
    mlb_api_url: str
    database_url: str
    log_level: str
    environment: str
    request_timeout_seconds: int
    max_http_retries: int
    retry_backoff_seconds: float


def load_settings() -> IngestSettings:
    return IngestSettings(
        mlb_api_url=os.getenv("MLB_API_URL", "http://localhost:8090"),
        database_url=os.getenv("DATABASE_URL", "sqlite:///./diamond_departures.db"),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        environment=os.getenv("ENVIRONMENT", "development"),
        request_timeout_seconds=int(os.getenv("REQUEST_TIMEOUT_SECONDS", "10")),
        max_http_retries=int(os.getenv("MAX_HTTP_RETRIES", "3")),
        retry_backoff_seconds=float(os.getenv("RETRY_BACKOFF_SECONDS", "1.0")),
    )
