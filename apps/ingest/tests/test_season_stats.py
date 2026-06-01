from __future__ import annotations
from unittest.mock import MagicMock, patch
from apps.ingest.app.season_stats import SeasonStatsRefresher, RefreshResult, _compute_derived


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


def test_refresh_result_fields():
    """refresh() returns a RefreshResult with expected fields (mocked DB)."""
    refresher = _make_refresher()

    fake_split = {
        "player": {"id": 660271, "fullName": "Shohei Ohtani",
                   "useLastName": "Ohtani",
                   "primaryPosition": {"abbreviation": "DH"}},
        "team": {"id": 119},
        "stat": {
            "plateAppearances": 550, "atBats": 480, "hits": 150,
            "doubles": 30, "triples": 2, "homeRuns": 40,
            "baseOnBalls": 60, "intentionalWalks": 5, "hitByPitch": 3,
            "strikeOuts": 120, "sacrificeFlies": 4, "rbi": 100,
            "stolenBases": 20, "avg": ".313", "obp": ".405",
            "slg": ".654", "ops": "1.059",
        },
    }

    with patch.object(refresher, "_fetch_hitting_splits", return_value=[fake_split]), \
         patch.object(refresher, "_fetch_expected_stats", return_value={}), \
         patch.object(refresher, "_fetch_savant", return_value={}), \
         patch.object(refresher, "_fetch_team_map", return_value={119: "LAD"}), \
         patch.object(refresher, "_write_to_db", return_value=(1, 10, 0)) as mock_write:
        result = refresher.refresh(season=2026)

    assert result.season == 2026
    assert result.players_upserted == 1
    assert result.stats_upserted == 10
    assert result.errors == []
