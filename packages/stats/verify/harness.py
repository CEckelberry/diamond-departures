"""Verification harness against curated player-season dataset."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from ..hitting import (
    LeagueContext,
    avg,
    babip,
    iso,
    load_woba_weights,
    obp,
    ops,
    slg,
    woba,
    wrc_plus,
)
from ..pitching import (
    bb_per_nine,
    era,
    era_plus,
    fip,
    k_minus_bb_rate,
    k_per_nine,
    load_pitching_constants,
    siera,
    whip,
    xfip,
)

DEFAULT_DATA_PATH = Path(__file__).with_name("data.json")
DEFAULT_TOLERANCE = 0.005


@dataclass(frozen=True)
class VerificationMismatch:
    player_id: int
    player_name: str
    stat_key: str
    expected: float
    actual: float
    pct_diff: float

    def to_error_line(self) -> str:
        return (
            f"player_id={self.player_id} "
            f"player_name={self.player_name} "
            f"stat={self.stat_key} "
            f"expected={self.expected} "
            f"actual={self.actual} "
            f"pct_diff={self.pct_diff:.4f}%"
        )


def load_dataset(path: Path | None = None) -> dict[str, Any]:
    dataset_path = path or DEFAULT_DATA_PATH
    return json.loads(dataset_path.read_text(encoding="utf-8"))


def compare_stat(
    *,
    player_id: int,
    player_name: str,
    stat_key: str,
    expected: float,
    actual: float,
    tolerance: float,
) -> VerificationMismatch | None:
    if expected == 0:
        pct_diff = 0.0 if actual == 0 else 100.0
    else:
        pct_diff = abs((actual - expected) / expected) * 100.0

    if pct_diff <= tolerance * 100.0:
        return None

    return VerificationMismatch(
        player_id=player_id,
        player_name=player_name,
        stat_key=stat_key,
        expected=expected,
        actual=actual,
        pct_diff=pct_diff,
    )


def _compute_hitting(entry: dict[str, Any]) -> dict[str, float]:
    stats = entry["inputs"]["hitting"]
    weights = load_woba_weights(entry["inputs"].get("woba_weights_year", 2026))
    league = entry["inputs"]["league_context"]
    context = LeagueContext(
        league_woba=league["league_woba"],
        woba_scale=league["woba_scale"],
        league_runs_per_pa=league["league_runs_per_pa"],
        park_factor=league["park_factor"],
    )

    singles = stats["h"] - stats["doubles"] - stats["triples"] - stats["home_runs"]
    avg_value = avg(stats["h"], stats["ab"])
    obp_value = obp(stats["h"], stats["bb"], stats["hbp"], stats["ab"], stats["sf"])
    slg_value = slg(singles, stats["doubles"], stats["triples"], stats["home_runs"], stats["ab"])

    return {
        "avg": avg_value,
        "obp": obp_value,
        "slg": slg_value,
        "ops": ops(obp_value, slg_value),
        "iso": iso(slg_value, avg_value),
        "babip": babip(stats["h"], stats["home_runs"], stats["ab"], stats["strikeouts"], stats["sf"]),
        "woba": woba(
            singles=singles,
            doubles=stats["doubles"],
            triples=stats["triples"],
            home_runs=stats["home_runs"],
            walks=stats["bb"],
            intentional_walks=stats["intentional_walks"],
            hit_by_pitch=stats["hbp"],
            at_bats=stats["ab"],
            sacrifice_flies=stats["sf"],
            weights=weights,
        ),
        "wrc_plus": wrc_plus(
            singles=singles,
            doubles=stats["doubles"],
            triples=stats["triples"],
            home_runs=stats["home_runs"],
            walks=stats["bb"],
            intentional_walks=stats["intentional_walks"],
            hit_by_pitch=stats["hbp"],
            at_bats=stats["ab"],
            sacrifice_flies=stats["sf"],
            context=context,
            weights=weights,
        ),
    }


def _compute_pitching(entry: dict[str, Any]) -> dict[str, float]:
    stats = entry["inputs"]["pitching"]
    constants = load_pitching_constants(entry["inputs"].get("pitching_constants_year", 2026))
    league = entry["inputs"]["league_context"]
    return {
        "era": era(stats["earned_runs"], stats["innings_pitched"]),
        "whip": whip(stats["walks"], stats["hits"], stats["innings_pitched"]),
        "k_per_nine": k_per_nine(stats["strikeouts"], stats["innings_pitched"]),
        "bb_per_nine": bb_per_nine(stats["walks"], stats["innings_pitched"]),
        "k_minus_bb_rate": k_minus_bb_rate(
            stats["strikeouts"], stats["walks"], stats["plate_appearances"]
        ),
        "fip": fip(
            stats["home_runs"],
            stats["walks"],
            stats["hit_by_pitch"],
            stats["strikeouts"],
            stats["innings_pitched"],
            constants,
        ),
        "xfip": xfip(
            stats["fly_balls"],
            stats["walks"],
            stats["hit_by_pitch"],
            stats["strikeouts"],
            stats["innings_pitched"],
            constants,
        ),
        "siera": siera(
            stats["strikeouts"],
            stats["walks"],
            stats["plate_appearances"],
            stats["ground_balls"],
            stats["fly_balls"],
        ),
        "era_plus": era_plus(
            pitcher_era=era(stats["earned_runs"], stats["innings_pitched"]),
            league_era=league["league_era"],
            park_factor=league["park_factor"],
        ),
    }


def compute_entry_stats(entry: dict[str, Any]) -> dict[str, float]:
    if "hitting" in entry["inputs"]:
        return _compute_hitting(entry)
    if "pitching" in entry["inputs"]:
        return _compute_pitching(entry)
    raise ValueError(f"Unsupported entry inputs: {entry['inputs'].keys()}")


def run_verification(path: Path | None = None, tolerance: float = DEFAULT_TOLERANCE) -> list[VerificationMismatch]:
    payload = load_dataset(path)
    mismatches: list[VerificationMismatch] = []

    for entry in payload["entries"]:
        expected_stats = entry["expected"]
        actual_stats = compute_entry_stats(entry)
        for stat_key, expected in expected_stats.items():
            actual = actual_stats.get(stat_key)
            if actual is None:
                mismatches.append(
                    VerificationMismatch(
                        player_id=entry["player_id"],
                        player_name=entry["player_name"],
                        stat_key=stat_key,
                        expected=expected,
                        actual=float("nan"),
                        pct_diff=100.0,
                    )
                )
                continue

            mismatch = compare_stat(
                player_id=entry["player_id"],
                player_name=entry["player_name"],
                stat_key=stat_key,
                expected=float(expected),
                actual=float(actual),
                tolerance=tolerance,
            )
            if mismatch is not None:
                mismatches.append(mismatch)

    return mismatches
