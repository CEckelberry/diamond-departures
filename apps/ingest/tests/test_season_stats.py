from __future__ import annotations
from unittest.mock import MagicMock, patch
from apps.ingest.app.season_stats import SeasonStatsRefresher, _compute_derived


def _make_refresher() -> SeasonStatsRefresher:
    return SeasonStatsRefresher(
        database_url="postgresql://fake",
        mlb_api_url="http://mlb-mock:8090",
    )


def test_compute_derived_iso():
    stats = {"SLG": 0.550, "AVG": 0.300, "HR": 30, "AB": 400,
             "BB": 60, "IBB": 5, "HBP": 3, "SO": 100, "SF": 4,
             "H": 120, "2B": 25, "3B": 2, "PA": 480}
    derived = _compute_derived(stats)
    assert abs(derived["ISO"] - 0.250) < 0.001


def test_compute_derived_babip():
    stats = {"H": 120, "HR": 30, "AB": 400, "SO": 100, "SF": 4,
             "SLG": 0.550, "AVG": 0.300,
             "BB": 60, "IBB": 5, "HBP": 3, "2B": 25, "3B": 2, "PA": 480}
    derived = _compute_derived(stats)
    # BABIP = (120 - 30) / (400 - 100 - 30 + 4) = 90 / 274
    assert abs(derived["BABIP"] - (90 / 274)) < 0.001


def test_compute_derived_bb_pct():
    stats = {"H": 120, "HR": 30, "AB": 400, "SO": 100, "SF": 4,
             "SLG": 0.550, "AVG": 0.300,
             "BB": 60, "IBB": 5, "HBP": 3, "2B": 25, "3B": 2, "PA": 480}
    derived = _compute_derived(stats)
    assert abs(derived["BB%"] - 60 / 480) < 0.0001


def test_compute_derived_k_pct():
    stats = {"H": 120, "HR": 30, "AB": 400, "SO": 100, "SF": 4,
             "SLG": 0.550, "AVG": 0.300,
             "BB": 60, "IBB": 5, "HBP": 3, "2B": 25, "3B": 2, "PA": 480}
    derived = _compute_derived(stats)
    assert abs(derived["K%"] - 100 / 480) < 0.0001
