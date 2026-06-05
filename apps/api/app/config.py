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
    supabase_jwt_secret: str = ""
    creem_api_key: str = ""
    creem_webhook_secret: str = ""
    creem_product_id: str = ""
    resend_api_key: str = ""
    public_url: str = "https://diamonddepartures.com"


def load_settings() -> ApiSettings:
    return ApiSettings(
        port=int(os.getenv("PORT", "8081")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        database_url=os.getenv("DATABASE_URL", "postgresql://diamond:diamond@localhost:5432/diamond"),
        sse_poll_seconds=float(os.getenv("SSE_POLL_SECONDS", "30")),
        current_season=int(os.getenv("CURRENT_SEASON", str(datetime.now(UTC).year))),
        supabase_jwt_secret=os.getenv("SUPABASE_JWT_SECRET", ""),
        creem_api_key=os.getenv("CREEM_API_KEY", ""),
        creem_webhook_secret=os.getenv("CREEM_WEBHOOK_SECRET", ""),
        creem_product_id=os.getenv("CREEM_PRODUCT_ID", ""),
        resend_api_key=os.getenv("RESEND_API_KEY", ""),
        public_url=os.getenv("PUBLIC_URL", "https://diamonddepartures.com"),
    )
