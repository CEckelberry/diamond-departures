from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class PlayerStatRecord:
    player_id: int
    stat_name: str
    stat_value: float
    valid_from: datetime
    valid_to: datetime | None
    source: str
    season: int


@dataclass(frozen=True)
class UpsertResult:
    changed: bool
    record: PlayerStatRecord | None


class PlayerStatsStore:
    def __init__(self, seed: list[PlayerStatRecord] | None = None) -> None:
        self._rows: list[PlayerStatRecord] = list(seed or [])

    def get_current(self, *, player_id: int, stat_name: str, season: int) -> PlayerStatRecord | None:
        for row in self._rows:
            if (
                row.player_id == player_id
                and row.stat_name == stat_name
                and row.season == season
                and row.valid_to is None
            ):
                return row
        return None

    def get_history(self, *, player_id: int, stat_name: str, season: int) -> list[PlayerStatRecord]:
        return [
            row
            for row in self._rows
            if row.player_id == player_id and row.stat_name == stat_name and row.season == season
        ]

    def upsert_stat(
        self,
        *,
        player_id: int,
        stat_name: str,
        stat_value: float,
        season: int,
        source: str,
        observed_at: datetime,
    ) -> UpsertResult:
        current = self.get_current(player_id=player_id, stat_name=stat_name, season=season)
        rounded_new = round(float(stat_value), 3)
        if current is not None and round(float(current.stat_value), 3) == rounded_new:
            return UpsertResult(changed=False, record=current)

        if current is not None:
            current.valid_to = observed_at

        record = PlayerStatRecord(
            player_id=player_id,
            stat_name=stat_name,
            stat_value=rounded_new,
            valid_from=observed_at,
            valid_to=None,
            source=source,
            season=season,
        )
        self._rows.append(record)
        return UpsertResult(changed=True, record=record)
