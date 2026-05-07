"""FIP/xFIP formulas and annual constants from STATS.md."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class PitchingConstants:
    """Annual constants used by FIP/xFIP calculations."""

    c_fip: float
    league_hr_per_fb: float


def load_pitching_constants(year: int = 2026) -> PitchingConstants:
    """Load pitching constants from `cfip_{year}.json`."""

    constants_path = Path(__file__).with_name(f"cfip_{year}.json")
    payload = json.loads(constants_path.read_text(encoding="utf-8"))
    return PitchingConstants(
        c_fip=payload["c_fip"],
        league_hr_per_fb=payload["league_hr_per_fb"],
    )


def fip(
    home_runs: int,
    walks: int,
    hit_by_pitch: int,
    strikeouts: int,
    innings_pitched: float,
    constants: PitchingConstants,
) -> float:
    """FIP formula: `((13*HR + 3*(BB+HBP) - 2*K) / IP) + cFIP`."""

    if innings_pitched == 0:
        return 0.0
    numerator = (13 * home_runs) + (3 * (walks + hit_by_pitch)) - (2 * strikeouts)
    return (numerator / innings_pitched) + constants.c_fip


def xfip(
    fly_balls: int,
    walks: int,
    hit_by_pitch: int,
    strikeouts: int,
    innings_pitched: float,
    constants: PitchingConstants,
) -> float:
    """xFIP: same as FIP but replace HR with expected HR = `FB * league HR/FB`."""

    if innings_pitched == 0:
        return 0.0
    expected_home_runs = fly_balls * constants.league_hr_per_fb
    numerator = (13 * expected_home_runs) + (3 * (walks + hit_by_pitch)) - (2 * strikeouts)
    return (numerator / innings_pitched) + constants.c_fip
