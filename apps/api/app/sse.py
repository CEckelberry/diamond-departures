from __future__ import annotations

import asyncio
import json
import time
from copy import deepcopy
from dataclasses import dataclass
from queue import Empty, Queue
from threading import RLock
from typing import Any

CacheKey = tuple[str, str]
CacheRows = list[dict[str, Any]]


@dataclass
class _Connection:
    queue: Queue[str]


class BoardSSEHub:
    def __init__(self, *, heartbeat_seconds: float = 30.0) -> None:
        self._heartbeat_seconds = heartbeat_seconds
        self._lock = RLock()
        self._connections: dict[CacheKey, list[_Connection]] = {}
        self._snapshots: dict[CacheKey, CacheRows] = {}

    async def stream(self, view: str, sort: str, snapshot_rows: CacheRows):
        key = (view, sort)
        conn = _Connection(queue=Queue())
        with self._lock:
            self._connections.setdefault(key, []).append(conn)
            self._snapshots[key] = deepcopy(snapshot_rows)

        try:
            yield _encode_event(
                "snapshot",
                {
                    "view": view,
                    "sort": sort,
                    "entries": deepcopy(snapshot_rows),
                },
            )

            while True:
                try:
                    event = await asyncio.to_thread(
                        conn.queue.get,
                        True,
                        self._heartbeat_seconds,
                    )
                    yield event
                except Empty:
                    yield _encode_event("heartbeat", {"ts": int(time.time())})
        finally:
            with self._lock:
                current = self._connections.get(key, [])
                self._connections[key] = [item for item in current if item is not conn]
                if not self._connections[key]:
                    self._connections.pop(key, None)

    def publish_snapshot(self, view: str, sort: str, rows: CacheRows) -> None:
        key = (view, sort)
        new_rows = deepcopy(rows)
        with self._lock:
            old_rows = deepcopy(self._snapshots.get(key, []))
            self._snapshots[key] = new_rows
            recipients = list(self._connections.get(key, []))

        delta = compute_delta(old_rows, new_rows)
        payload = _encode_event(
            "delta",
            {
                "view": view,
                "sort": sort,
                "changes": delta,
            },
        )
        for conn in recipients:
            conn.queue.put_nowait(payload)

    def connection_count(self, view: str, sort: str) -> int:
        with self._lock:
            return len(self._connections.get((view, sort), []))


def compute_delta(old_rows: CacheRows, new_rows: CacheRows) -> list[dict[str, Any]]:
    old_index = {int(row["player_id"]): row for row in old_rows if "player_id" in row}
    changes: list[dict[str, Any]] = []

    for row in sorted(new_rows, key=lambda item: int(item.get("rank", 10_000))):
        player_id = int(row["player_id"])
        old_row = old_index.get(player_id)
        old_rank = None if old_row is None else old_row.get("rank")
        new_rank = row.get("rank")
        old_value = None if old_row is None else old_row.get("stat_value")
        new_value = row.get("stat_value")

        changed_stats: list[dict[str, Any]] = []
        if old_value != new_value:
            changed_stats.append({"name": "stat_value", "old": old_value, "new": new_value})

        if old_rank != new_rank or changed_stats:
            changes.append(
                {
                    "player_id": player_id,
                    "old_rank": old_rank,
                    "new_rank": new_rank,
                    "changed_stats": changed_stats,
                }
            )

    return changes


def _encode_event(event: str, payload: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, separators=(',', ':'))}\n\n"
