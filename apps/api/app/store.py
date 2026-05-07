from __future__ import annotations

from collections.abc import Callable


def postgres_health_check(database_url: str) -> Callable[[], bool]:
    def _health() -> bool:
        # Real DB check wired in later packet.
        return bool(database_url)

    return _health
