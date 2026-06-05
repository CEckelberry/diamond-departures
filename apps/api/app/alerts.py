# apps/api/app/alerts.py
from __future__ import annotations

from collections.abc import Callable

AlertLister  = Callable[[str], list[dict]]
AlertCreator = Callable[[str, int, str, float, str], dict]
AlertDeleter = Callable[[str, str], bool]


def in_memory_alert_lister(user_id: str) -> list[dict]: return []
def in_memory_alert_creator(user_id: str, player_id: int, stat_name: str, threshold: float, direction: str) -> dict:
    return {"id": "stub", "user_id": user_id, "player_id": player_id, "stat_name": stat_name, "threshold": threshold, "direction": direction}
def in_memory_alert_deleter(alert_id: str, user_id: str) -> bool: return False
