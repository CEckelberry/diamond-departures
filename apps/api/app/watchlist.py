# apps/api/app/watchlist.py
from __future__ import annotations

from collections.abc import Callable

WatchlistLister  = Callable[[str], list[dict]]
WatchlistAdder   = Callable[[str, int], None]
WatchlistRemover = Callable[[str, int], bool]


def in_memory_watchlist_lister(user_id: str) -> list[dict]:
    return []

def in_memory_watchlist_adder(user_id: str, player_id: int) -> None:
    pass

def in_memory_watchlist_remover(user_id: str, player_id: int) -> bool:
    return False
