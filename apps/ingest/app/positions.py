from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from math import ceil


@dataclass(frozen=True)
class PositionUsage:
    position: str
    games: int
    innings: float


@dataclass(frozen=True)
class PitchingUsage:
    appearances: int
    starts: int
    innings_pitched: float


@dataclass(frozen=True)
class QualificationInputs:
    role: str
    team_games: int
    plate_appearances: int
    innings_pitched: float
    appearances: int
    currently_qualified: bool
    previous_just_qualified_at: datetime | None


@dataclass(frozen=True)
class QualificationOutcome:
    is_qualified: bool
    just_qualified_at: datetime | None


def _normalized_position(position: str) -> str:
    token = position.strip().upper()
    if token in {"LF", "CF", "RF", "OF"}:
        return "OF"
    return token


def classify_primary_position(usage: list[PositionUsage]) -> str:
    if not usage:
        return "UT"

    normalized = [_normalized_position(item.position) for item in usage if item.games > 0]
    distinct_positions = set(normalized)

    if len(distinct_positions) >= 3:
        return "UT"

    best = sorted(
        usage,
        key=lambda item: (
            item.games,
            item.innings,
        ),
        reverse=True,
    )

    top_games = best[0].games
    tied = [item for item in best if item.games == top_games]
    tied_positions = {_normalized_position(item.position) for item in tied}
    if tied_positions <= {"OF"}:
        return "OF"

    return _normalized_position(best[0].position)


def compute_eligible_positions(usage: list[PositionUsage], min_games: int = 5) -> list[str]:
    eligible = {
        _normalized_position(item.position)
        for item in usage
        if item.games >= min_games
    }
    return sorted(eligible)


def classify_pitcher_role(usage: PitchingUsage) -> str:
    if usage.appearances <= 0:
        return "RP"
    return "SP" if (usage.starts / usage.appearances) > 0.5 else "RP"


def _meets_threshold(inputs: QualificationInputs) -> bool:
    role = inputs.role.upper()
    if role == "HITTER":
        return inputs.plate_appearances >= ceil(2.7 * inputs.team_games)
    if role == "SP":
        return inputs.innings_pitched >= (1.0 * inputs.team_games)
    if role == "RP":
        return inputs.appearances >= 25
    return False


def evaluate_qualification(inputs: QualificationInputs, observed_at: datetime) -> QualificationOutcome:
    qualified_now = _meets_threshold(inputs)
    just_qualified_at = inputs.previous_just_qualified_at

    if qualified_now and not inputs.currently_qualified and just_qualified_at is None:
        just_qualified_at = observed_at

    if not qualified_now:
        just_qualified_at = None

    return QualificationOutcome(is_qualified=qualified_now, just_qualified_at=just_qualified_at)
