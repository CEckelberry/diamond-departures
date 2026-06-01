from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone
from typing import Any

VALID_VIEWS = {"hitters", "pitchers", "hitters_ss", "hitters_of", "pitchers_sp", "pitchers_rp", "defense"}
VALID_SORTS = {
    "wRC+", "OPS", "HR", "SB", "WAR", "AVG", "RBI", "SLG", "OPS+", "DRS", "xwOBA", "H",
    "ERA", "FIP", "K%", "WHIP", "W", "SV", "K", "K-BB%", "K/9", "BB/9", "xFIP",
    "OAA", "UZR", "Fielding %", "Def", "E",
    "wOBA", "ISO", "BABIP", "BB%",
    # Statcast
    "xBA", "barrel_pct", "hard_hit_pct", "exit_velocity",
    # Traditional extras
    "OBP",
}

BoardReader = Callable[[str, str, int], list[dict[str, Any]]]


def age_category(refreshed_at: datetime, now: datetime | None = None) -> str:
    current = now or datetime.now(timezone.utc)
    age = current - refreshed_at
    if age <= timedelta(minutes=2):
        return "live"
    if age <= timedelta(minutes=15):
        return "recent"
    if age <= timedelta(hours=1):
        return "stale"
    return "old"


def parse_refreshed_at(raw: str) -> datetime:
    parsed = datetime.fromisoformat(raw)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def in_memory_board_reader(view: str, sort: str, season: int = 2026) -> list[dict[str, Any]]:
    del view, sort, season
    return []
