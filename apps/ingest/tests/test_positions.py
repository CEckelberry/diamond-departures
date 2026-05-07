from __future__ import annotations

from datetime import datetime, timedelta, timezone

from apps.ingest.app.positions import (
    PitchingUsage,
    PositionUsage,
    QualificationInputs,
    classify_pitcher_role,
    classify_primary_position,
    compute_eligible_positions,
    evaluate_qualification,
)


def test_primary_position_and_eligibility_from_usage_counts() -> None:
    usage = [
        PositionUsage(position="2B", games=80, innings=650.0),
        PositionUsage(position="SS", games=25, innings=210.0),
    ]

    assert classify_primary_position(usage) == "2B"
    assert compute_eligible_positions(usage) == ["2B", "SS"]


def test_corner_outfield_tie_collapses_to_of() -> None:
    usage = [
        PositionUsage(position="LF", games=45, innings=330.0),
        PositionUsage(position="RF", games=45, innings=330.0),
    ]

    assert classify_primary_position(usage) == "OF"


def test_three_plus_positions_returns_ut() -> None:
    usage = [
        PositionUsage(position="2B", games=30, innings=220.0),
        PositionUsage(position="SS", games=25, innings=205.0),
        PositionUsage(position="3B", games=20, innings=180.0),
    ]

    assert classify_primary_position(usage) == "UT"


def test_pitcher_role_split_by_start_ratio() -> None:
    reliever = PitchingUsage(appearances=25, starts=2, innings_pitched=60.0)
    starter = PitchingUsage(appearances=20, starts=12, innings_pitched=70.0)

    assert classify_pitcher_role(reliever) == "RP"
    assert classify_pitcher_role(starter) == "SP"


def test_qualification_thresholds_and_just_qualified_transition() -> None:
    now = datetime(2026, 5, 7, 15, 0, tzinfo=timezone.utc)

    hitter = evaluate_qualification(
        QualificationInputs(
            role="HITTER",
            team_games=81,
            plate_appearances=218,
            innings_pitched=0.0,
            appearances=0,
            currently_qualified=False,
            previous_just_qualified_at=None,
        ),
        observed_at=now,
    )
    assert hitter.is_qualified is False
    assert hitter.just_qualified_at is None

    newly_qualified_hitter = evaluate_qualification(
        QualificationInputs(
            role="HITTER",
            team_games=81,
            plate_appearances=219,
            innings_pitched=0.0,
            appearances=0,
            currently_qualified=False,
            previous_just_qualified_at=None,
        ),
        observed_at=now,
    )
    assert newly_qualified_hitter.is_qualified is True
    assert newly_qualified_hitter.just_qualified_at == now

    existing_stamp = now - timedelta(hours=4)
    already_qualified = evaluate_qualification(
        QualificationInputs(
            role="HITTER",
            team_games=81,
            plate_appearances=260,
            innings_pitched=0.0,
            appearances=0,
            currently_qualified=True,
            previous_just_qualified_at=existing_stamp,
        ),
        observed_at=now,
    )
    assert already_qualified.just_qualified_at == existing_stamp

    starter = evaluate_qualification(
        QualificationInputs(
            role="SP",
            team_games=81,
            plate_appearances=0,
            innings_pitched=70.0,
            appearances=20,
            currently_qualified=False,
            previous_just_qualified_at=None,
        ),
        observed_at=now,
    )
    assert starter.is_qualified is False

    reliever = evaluate_qualification(
        QualificationInputs(
            role="RP",
            team_games=81,
            plate_appearances=0,
            innings_pitched=60.0,
            appearances=25,
            currently_qualified=False,
            previous_just_qualified_at=None,
        ),
        observed_at=now,
    )
    assert reliever.is_qualified is True
