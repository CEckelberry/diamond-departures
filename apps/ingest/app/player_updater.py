from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from packages.stats.hitting import LeagueContext, load_woba_weights, ops, wrc_plus
from packages.stats.hitting import avg as calc_avg
from packages.stats.hitting import obp as calc_obp
from packages.stats.hitting import slg as calc_slg

from .player_stats_store import PlayerStatsStore


@dataclass(frozen=True)
class BattingLine:
    at_bats: int
    hits: int
    doubles: int
    triples: int
    home_runs: int
    walks: int
    intentional_walks: int
    hit_by_pitch: int
    sacrifice_flies: int

    @property
    def singles(self) -> int:
        return self.hits - self.doubles - self.triples - self.home_runs


@dataclass(frozen=True)
class LeagueContextInputs:
    league_woba: float
    woba_scale: float
    league_runs_per_pa: float
    park_factor: float


@dataclass(frozen=True)
class PlayerUpdateResult:
    changed_stats: list[str]


def _derived_stats(line: BattingLine, context: LeagueContextInputs) -> dict[str, float]:
    avg_value = calc_avg(line.hits, line.at_bats)
    obp_value = calc_obp(
        h=line.hits,
        bb=line.walks,
        hbp=line.hit_by_pitch,
        ab=line.at_bats,
        sf=line.sacrifice_flies,
    )
    slg_value = calc_slg(
        singles=line.singles,
        doubles=line.doubles,
        triples=line.triples,
        home_runs=line.home_runs,
        ab=line.at_bats,
    )
    ops_value = ops(obp_value=obp_value, slg_value=slg_value)

    wrc_context = LeagueContext(
        league_woba=context.league_woba,
        woba_scale=context.woba_scale,
        league_runs_per_pa=context.league_runs_per_pa,
        park_factor=context.park_factor,
    )
    wrc_plus_value = wrc_plus(
        singles=line.singles,
        doubles=line.doubles,
        triples=line.triples,
        home_runs=line.home_runs,
        walks=line.walks,
        intentional_walks=line.intentional_walks,
        hit_by_pitch=line.hit_by_pitch,
        at_bats=line.at_bats,
        sacrifice_flies=line.sacrifice_flies,
        context=wrc_context,
        weights=load_woba_weights(2026),
    )

    return {
        "AVG": avg_value,
        "OBP": obp_value,
        "SLG": slg_value,
        "OPS": ops_value,
        "wRC+": wrc_plus_value,
    }


def update_player_stats(
    *,
    player_id: int,
    season: int,
    batting_line: BattingLine,
    store: PlayerStatsStore,
    observed_at: datetime,
    context: LeagueContextInputs,
    source: str = "mlb-api",
) -> PlayerUpdateResult:
    changed_stats: list[str] = []
    derived = _derived_stats(batting_line, context)

    for stat_name, stat_value in derived.items():
        result = store.upsert_stat(
            player_id=player_id,
            stat_name=stat_name,
            stat_value=stat_value,
            season=season,
            source=source,
            observed_at=observed_at,
        )
        if result.changed:
            changed_stats.append(stat_name)

    return PlayerUpdateResult(changed_stats=changed_stats)
