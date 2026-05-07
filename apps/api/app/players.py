from __future__ import annotations

from collections.abc import Callable
from typing import Any

PlayerDetailReader = Callable[[int], dict[str, Any] | None]
PlayerHistoryReader = Callable[[int, str], list[dict[str, Any]] | None]

VALID_HISTORY_STATS = {"wRC+", "OPS"}


def in_memory_player_detail_reader(player_id: int) -> dict[str, Any] | None:
    del player_id
    return None


def in_memory_player_history_reader(player_id: int, stat: str) -> list[dict[str, Any]] | None:
    del player_id, stat
    return None
