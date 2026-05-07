from __future__ import annotations

from collections.abc import Callable
from typing import Any

SeasonStateReader = Callable[[], dict[str, Any]]
FreshnessReader = Callable[[], dict[str, Any]]

VALID_SEASON_MODES = {"live", "between", "off-game", "off-season"}


def in_memory_season_state_reader() -> dict[str, Any]:
    return {
        "mode": "off-season",
        "next_game_at": None,
        "current_season": 2026,
    }


def in_memory_freshness_reader() -> dict[str, Any]:
    return {
        "ingest_runs": [],
        "schema_drift": {"status": "unknown", "last_checked_at": None},
        "stats": {},
    }
