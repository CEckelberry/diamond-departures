from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor, execute_values

from .mlb_client import MLBApiClient
from .savant_client import SavantClient

log = logging.getLogger("apps.ingest.season_stats")

# Direct stat names from MLB API hitting split -> our stat_name
_HITTING_API_KEYS: dict[str, str] = {
    "HR":  "homeRuns",
    "RBI": "rbi",
    "SB":  "stolenBases",
    "AVG": "avg",
    "OBP": "obp",
    "SLG": "slg",
    "OPS": "ops",
    "H":   "hits",
}

# wOBA weights — 2026 coefficients used as approximation for all years
_WOBA_WEIGHTS = {"bb": 0.69, "hbp": 0.72, "1b": 0.89, "2b": 1.27, "3b": 1.62, "hr": 2.10}
_LEAGUE_WOBA = 0.310
_WOBA_SCALE = 1.21
_LEAGUE_R_PER_PA = 0.115

_MIN_PA = 100

_HITTER_VIEWS: list[tuple[str, bool]] = [
    ("HR", False), ("RBI", False), ("SB", False), ("AVG", False),
    ("OBP", False), ("SLG", False), ("OPS", False),
    ("wRC+", False), ("wOBA", False), ("ISO", False),
    ("BABIP", False), ("BB%", False), ("K%", True),
    ("xwOBA", False), ("xBA", False),
    ("barrel_pct", False), ("hard_hit_pct", False), ("exit_velocity", False),
]

_VIEW_KEYS = ["hitters", "hitters_ss", "hitters_of"]
_POSITION_FILTER: dict[str, str | None] = {
    "hitters": None,
    "hitters_ss": "SS",
    "hitters_of": "OF",
}


@dataclass
class RefreshResult:
    season: int
    players_upserted: int
    stats_upserted: int
    leaderboard_rows: int
    errors: list[str]


def _compute_woba(
    singles: float, doubles: float, triples: float, hr: float,
    bb: float, ibb: float, hbp: float, ab: float, sf: float,
) -> float | None:
    denom = ab + bb - ibb + sf + hbp
    if denom == 0:
        return None
    return (
        _WOBA_WEIGHTS["bb"] * bb + _WOBA_WEIGHTS["hbp"] * hbp
        + _WOBA_WEIGHTS["1b"] * singles + _WOBA_WEIGHTS["2b"] * doubles
        + _WOBA_WEIGHTS["3b"] * triples + _WOBA_WEIGHTS["hr"] * hr
    ) / denom


def _compute_wrc_plus(
    singles: float, doubles: float, triples: float, hr: float,
    bb: float, ibb: float, hbp: float, ab: float, sf: float,
) -> float | None:
    player_woba = _compute_woba(singles, doubles, triples, hr, bb, ibb, hbp, ab, sf)
    if player_woba is None or _WOBA_SCALE == 0 or _LEAGUE_R_PER_PA == 0:
        return None
    numerator = ((player_woba - _LEAGUE_WOBA) / _WOBA_SCALE) + _LEAGUE_R_PER_PA
    return round(100 * (numerator / _LEAGUE_R_PER_PA))


def _compute_derived(raw: dict[str, Any]) -> dict[str, float]:
    """Compute ISO, BABIP, BB%, K%, wOBA, wRC+ from raw hitting stats dict."""
    result: dict[str, float] = {}
    try:
        h    = float(raw.get("H", 0))
        d    = float(raw.get("2B", 0))
        t    = float(raw.get("3B", 0))
        hr   = float(raw.get("HR", 0))
        ab   = float(raw.get("AB", 0))
        bb   = float(raw.get("BB", 0))
        ibb  = float(raw.get("IBB", 0))
        hbp  = float(raw.get("HBP", 0))
        sf   = float(raw.get("SF", 0))
        so   = float(raw.get("SO", 0))
        pa   = float(raw.get("PA", 0))
        slg  = float(raw.get("SLG", 0))
        avg  = float(raw.get("AVG", 0))
        singles = h - d - t - hr

        result["ISO"] = slg - avg

        babip_denom = ab - so - hr + sf
        if babip_denom > 0:
            result["BABIP"] = (h - hr) / babip_denom

        if pa > 0:
            result["BB%"] = bb / pa
            result["K%"] = so / pa

        woba_val = _compute_woba(singles, d, t, hr, bb, ibb, hbp, ab, sf)
        if woba_val is not None:
            result["wOBA"] = woba_val

        wrc = _compute_wrc_plus(singles, d, t, hr, bb, ibb, hbp, ab, sf)
        if wrc is not None:
            result["wRC+"] = float(wrc)
    except (TypeError, ValueError, ZeroDivisionError):
        pass
    return result


class SeasonStatsRefresher:
    def __init__(
        self,
        *,
        database_url: str,
        mlb_api_url: str,
        savant_base_url: str = "https://baseballsavant.mlb.com",
    ) -> None:
        self._db_url = database_url
        self._mlb = MLBApiClient(base_url=mlb_api_url, timeout_seconds=15)
        self._savant = SavantClient(base_url=savant_base_url)

    def _fetch_hitting_splits(self, season: int) -> list[dict]:
        resp = self._mlb.get_json(
            f"/api/v1/stats?stats=season&group=hitting&season={season}"
            f"&limit=500&sortStat=homeRuns&playerPool=All&hydrate=person"
        )
        return resp.payload.get("stats", [{}])[0].get("splits", [])

    def _fetch_expected_stats(self, season: int) -> dict[int, dict]:
        """Return {player_id: {xwOBA, xBA}} from MLB expectedStatistics endpoint."""
        try:
            resp = self._mlb.get_json(
                f"/api/v1/stats?stats=expectedStatistics&playerPool=qualified"
                f"&group=hitting&gameType=R&season={season}&sportId=1"
            )
            result: dict[int, dict] = {}
            for split in resp.payload.get("stats", [{}])[0].get("splits", []):
                pid = int(split.get("player", {}).get("id", 0))
                if pid:
                    stat = split.get("stat", {})
                    result[pid] = {
                        "xwOBA": float(stat.get("xwoba") or stat.get("xwOBA") or 0),
                        "xBA":   float(stat.get("xba")   or stat.get("xBA")   or 0),
                    }
            return result
        except Exception as exc:
            log.warning("expectedStatistics fetch failed: %s", exc)
            return {}

    def _fetch_savant(self, season: int) -> dict[int, dict]:
        """Return {player_id: {barrel_pct, hard_hit_pct, exit_velocity}} from Savant."""
        try:
            rows = self._savant.fetch_statcast(year=season)
            return {r["player_id"]: r for r in rows}
        except Exception as exc:
            log.warning("Savant fetch failed: %s", exc)
            return {}

    def _fetch_team_map(self, season: int) -> dict[int, str]:
        """Return {team_id_api: abbr}."""
        resp = self._mlb.get_json(f"/api/v1/teams?season={season}&sportId=1")
        return {
            t["id"]: t["abbreviation"]
            for t in resp.payload.get("teams", [])
            if "abbreviation" in t
        }
