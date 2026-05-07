from __future__ import annotations

from collections.abc import Callable
from copy import deepcopy
from threading import RLock
from typing import Any

CacheKey = tuple[str, str]
CacheRows = list[dict[str, Any]]
LoadAllCallback = Callable[[], dict[CacheKey, CacheRows]]
RefreshOneCallback = Callable[[str, str], CacheRows]


class LeaderboardCache:
    def __init__(self, *, load_all: LoadAllCallback) -> None:
        self._lock = RLock()
        self._load_all = load_all
        self._cache: dict[CacheKey, CacheRows] = {}

    def load_startup(self) -> None:
        rows_by_key = self._load_all()
        with self._lock:
            self._cache = {key: deepcopy(rows) for key, rows in rows_by_key.items()}

    def get(self, view: str, sort: str) -> CacheRows:
        with self._lock:
            return deepcopy(self._cache.get((view, sort), []))

    def invalidate(self, view: str, sort: str, *, refresh_one: RefreshOneCallback) -> None:
        refreshed = refresh_one(view, sort)
        with self._lock:
            self._cache[(view, sort)] = deepcopy(refreshed)
