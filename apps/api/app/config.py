from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class ApiSettings:
    port: int = 8081
    log_level: str = "INFO"
    database_url: str = "postgresql://diamond:diamond@localhost:5432/diamond"
    sse_poll_seconds: float = 30.0
    current_season: int = field(default_factory=lambda: datetime.now(UTC).year)


def load_settings() -> ApiSettings:
    return ApiSettings(
        port=int(os.getenv("PORT", "8081")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        database_url=os.getenv("DATABASE_URL", "postgresql://diamond:diamond@localhost:5432/diamond"),
        sse_poll_seconds=float(os.getenv("SSE_POLL_SECONDS", "30")),
        current_season=int(os.getenv("CURRENT_SEASON", str(datetime.now(UTC).year))),
    )
