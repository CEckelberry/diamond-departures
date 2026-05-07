"""Weighted Runs Created Plus (wRC+) formulas from STATS.md."""

from __future__ import annotations

from dataclasses import dataclass

from .woba import WOBAWeights, woba


@dataclass(frozen=True)
class LeagueContext:
    """League context inputs used by adjusted rate stats like wRC+."""

    league_woba: float
    woba_scale: float
    league_runs_per_pa: float
    park_factor: float


def wrc_plus(
    singles: int,
    doubles: int,
    triples: int,
    home_runs: int,
    walks: int,
    intentional_walks: int,
    hit_by_pitch: int,
    at_bats: int,
    sacrifice_flies: int,
    context: LeagueContext,
    weights: WOBAWeights,
) -> float:
    """Calculate wRC+ using STATS.md FanGraphs-style formula and park factor."""

    if context.woba_scale == 0 or context.league_runs_per_pa == 0:
        return 0.0

    player_woba = woba(
        singles=singles,
        doubles=doubles,
        triples=triples,
        home_runs=home_runs,
        walks=walks,
        intentional_walks=intentional_walks,
        hit_by_pitch=hit_by_pitch,
        at_bats=at_bats,
        sacrifice_flies=sacrifice_flies,
        weights=weights,
    )
    numerator = (
        ((player_woba - context.league_woba) / context.woba_scale)
        + context.league_runs_per_pa
        + (context.league_runs_per_pa - (context.park_factor * context.league_runs_per_pa))
    )
    return 100 * (numerator / context.league_runs_per_pa)
