"""Weighted On-Base Average (wOBA) formulas from STATS.md."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class WOBAWeights:
    """Annual wOBA coefficients for each offensive event type."""

    walk: float
    hit_by_pitch: float
    single: float
    double: float
    triple: float
    home_run: float


def load_woba_weights(year: int = 2026) -> WOBAWeights:
    """Load annual wOBA coefficients from `woba_weights_{year}.json`."""

    weights_path = Path(__file__).with_name(f"woba_weights_{year}.json")
    payload = json.loads(weights_path.read_text(encoding="utf-8"))
    raw_weights = payload["weights"]
    return WOBAWeights(
        walk=raw_weights["bb"],
        hit_by_pitch=raw_weights["hbp"],
        single=raw_weights["1b"],
        double=raw_weights["2b"],
        triple=raw_weights["3b"],
        home_run=raw_weights["hr"],
    )


def woba(
    singles: int,
    doubles: int,
    triples: int,
    home_runs: int,
    walks: int,
    intentional_walks: int,
    hit_by_pitch: int,
    at_bats: int,
    sacrifice_flies: int,
    weights: WOBAWeights,
) -> float:
    """Calculate wOBA: weighted events divided by `(AB + BB - IBB + SF + HBP)`."""

    numerator = (
        (weights.walk * walks)
        + (weights.hit_by_pitch * hit_by_pitch)
        + (weights.single * singles)
        + (weights.double * doubles)
        + (weights.triple * triples)
        + (weights.home_run * home_runs)
    )
    denominator = at_bats + walks - intentional_walks + sacrifice_flies + hit_by_pitch
    return 0.0 if denominator == 0 else numerator / denominator
