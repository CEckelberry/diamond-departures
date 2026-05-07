from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


TRACKED_VIEW_STATS = {
    "wRC+": "hitters",
    "OPS": "hitters",
}


@dataclass(frozen=True)
class PlayerLeaderboardSnapshot:
    player_id: int
    stat_name: str
    stat_value: float
    eligible_pos: set[str]


@dataclass(frozen=True)
class LeaderboardRow:
    view_key: str
    sort_stat: str
    rank: int
    player_id: int
    stat_value: float
    refreshed_at: datetime


class LeaderboardStore:
    def __init__(self) -> None:
        self._rows: list[LeaderboardRow] = []

    def replace_view_rows(self, *, view_key: str, sort_stat: str, rows: list[LeaderboardRow]) -> None:
        self._rows = [
            row
            for row in self._rows
            if not (row.view_key == view_key and row.sort_stat == sort_stat)
        ]
        self._rows.extend(rows)

    def get_view_rows(self, *, view_key: str, sort_stat: str) -> list[LeaderboardRow]:
        return [
            row
            for row in sorted(self._rows, key=lambda item: item.rank)
            if row.view_key == view_key and row.sort_stat == sort_stat
        ]


def map_affected_views(
    *,
    updated_stats_by_player: dict[int, set[str]],
    player_positions: dict[int, set[str]],
) -> set[tuple[str, str]]:
    affected: set[tuple[str, str]] = set()

    for player_id, stat_names in updated_stats_by_player.items():
        for stat_name in stat_names:
            base_view = TRACKED_VIEW_STATS.get(stat_name)
            if base_view is None:
                continue

            affected.add((base_view, stat_name))
            for pos in player_positions.get(player_id, set()):
                affected.add((f"{base_view}_{pos.lower()}", stat_name))

    return affected


def recompute_view(
    *,
    store: LeaderboardStore,
    view_key: str,
    sort_stat: str,
    snapshots: list[PlayerLeaderboardSnapshot],
    refreshed_at: datetime,
    required_position: str | None = None,
    limit: int = 100,
) -> list[LeaderboardRow]:
    filtered = [snapshot for snapshot in snapshots if snapshot.stat_name == sort_stat]
    if required_position is not None:
        filtered = [snapshot for snapshot in filtered if required_position in snapshot.eligible_pos]

    sorted_rows = sorted(filtered, key=lambda item: (-item.stat_value, item.player_id))
    top = sorted_rows[:limit]

    rows = [
        LeaderboardRow(
            view_key=view_key,
            sort_stat=sort_stat,
            rank=index + 1,
            player_id=snapshot.player_id,
            stat_value=round(snapshot.stat_value, 3),
            refreshed_at=refreshed_at,
        )
        for index, snapshot in enumerate(top)
    ]

    store.replace_view_rows(view_key=view_key, sort_stat=sort_stat, rows=rows)
    return rows
