from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class ApiSettings:
    port: int = 8081
    log_level: str = "INFO"
    database_url: str = "postgresql://diamond:diamond@localhost:5432/diamond"


def load_settings() -> ApiSettings:
    return ApiSettings(
        port=int(os.getenv("PORT", "8081")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        database_url=os.getenv("DATABASE_URL", "postgresql://diamond:diamond@localhost:5432/diamond"),
    )
