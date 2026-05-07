from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class DBEngine:
    database_url: str


@dataclass(frozen=True)
class StoreContext:
    engine: DBEngine
    session_factory: Callable[[], dict[str, object]]


def init_store(database_url: str) -> StoreContext:
    engine = DBEngine(database_url=database_url)

    def _session_factory() -> dict[str, object]:
        return {"database_url": database_url, "connected": True}

    return StoreContext(engine=engine, session_factory=_session_factory)
