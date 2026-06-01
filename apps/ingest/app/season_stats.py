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

    # ── DB writes ────────────────────────────────────────────────────────────

    def _write_to_db(
        self,
        season: int,
        splits: list[dict],
        expected: dict[int, dict],
        savant: dict[int, dict],
        team_map_api: dict[int, str],
        now: datetime,
    ) -> tuple[int, int, int]:
        """Upsert players and stats, rebuild leaderboards. Returns (players, stats, errors)."""
        players_upserted = 0
        stats_upserted = 0
        error_count = 0

        with psycopg2.connect(self._db_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT id, abbr FROM teams")
                team_map_db: dict[str, int] = {r["abbr"]: r["id"] for r in cur.fetchall()}

                for split in splits:
                    pa = int(split["stat"].get("plateAppearances", 0))
                    if pa < _MIN_PA:
                        continue

                    player = split["player"]
                    team_abbr = team_map_api.get(split["team"]["id"], "")
                    if not team_abbr or team_abbr not in team_map_db:
                        continue

                    pid = int(player["id"])
                    full_name = player["fullName"]
                    short_name = (
                        player.get("useLastName")
                        or player.get("lastName")
                        or full_name.split()[-1]
                    )
                    pos = player.get("primaryPosition", {}).get("abbreviation", "OF")
                    headshot = (
                        f"https://img.mlbstatic.com/mlb-photos/image/upload/"
                        f"d_people:generic:headshot:67:current.png/w_213,q_auto:best"
                        f"/v1/people/{pid}/headshot/67/current"
                    )

                    cur.execute("""
                        INSERT INTO players
                            (id, full_name, short_name, primary_pos, team_id, last_seen_at, headshot_url, is_active)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,true)
                        ON CONFLICT (id) DO UPDATE SET
                            full_name=EXCLUDED.full_name, short_name=EXCLUDED.short_name,
                            primary_pos=EXCLUDED.primary_pos, team_id=EXCLUDED.team_id,
                            last_seen_at=EXCLUDED.last_seen_at, headshot_url=EXCLUDED.headshot_url,
                            is_active=true
                    """, (pid, full_name, short_name, pos, team_map_db[team_abbr], now, headshot))
                    players_upserted += 1

                    raw = {
                        "H": split["stat"].get("hits", 0),
                        "2B": split["stat"].get("doubles", 0),
                        "3B": split["stat"].get("triples", 0),
                        "HR": split["stat"].get("homeRuns", 0),
                        "AB": split["stat"].get("atBats", 0),
                        "BB": split["stat"].get("baseOnBalls", 0),
                        "IBB": split["stat"].get("intentionalWalks", 0),
                        "HBP": split["stat"].get("hitByPitch", 0),
                        "SF":  split["stat"].get("sacrificeFlies", 0),
                        "SO":  split["stat"].get("strikeOuts", 0),
                        "PA":  pa,
                        "SLG": float(split["stat"].get("slg") or 0),
                        "AVG": float(split["stat"].get("avg") or 0),
                    }

                    all_stats: dict[str, float] = {}
                    for stat_name, api_key in _HITTING_API_KEYS.items():
                        val = split["stat"].get(api_key)
                        if val is not None and str(val) not in ("", ".---", "-.--"):
                            try:
                                all_stats[stat_name] = float(val)
                            except (ValueError, TypeError):
                                pass

                    all_stats.update(_compute_derived(raw))

                    if pid in expected:
                        all_stats.update(expected[pid])

                    if pid in savant:
                        sv = savant[pid]
                        all_stats["barrel_pct"]    = sv["barrel_pct"]
                        all_stats["hard_hit_pct"]  = sv["hard_hit_pct"]
                        all_stats["exit_velocity"] = sv["exit_velocity"]

                    for stat_name, stat_value in all_stats.items():
                        try:
                            rounded = round(float(stat_value), 3)
                            cur.execute("""
                                SELECT id, stat_value FROM player_stats
                                WHERE player_id=%s AND stat_name=%s AND season=%s AND valid_to IS NULL
                            """, (pid, stat_name, season))
                            existing = cur.fetchone()
                            if existing and round(float(existing["stat_value"]), 3) == rounded:
                                continue
                            if existing:
                                cur.execute("""
                                    UPDATE player_stats
                                    SET valid_to = GREATEST(%s, valid_from + interval '1 microsecond')
                                    WHERE id=%s
                                """, (now, existing["id"]))
                            cur.execute("""
                                INSERT INTO player_stats
                                    (player_id, stat_name, stat_value, valid_from, valid_to, source, season)
                                VALUES (%s,%s,%s,%s,NULL,'mlb_stats_api',%s)
                            """, (pid, stat_name, rounded, now, season))
                            stats_upserted += 1
                        except Exception as exc:
                            log.debug("stat upsert failed %s/%s: %s", pid, stat_name, exc)
                            error_count += 1

                self._rebuild_leaderboards(cur, season=season, now=now)
                conn.commit()

        return players_upserted, stats_upserted, error_count

    def _rebuild_leaderboards(self, cur: Any, *, season: int, now: datetime) -> int:
        """DELETE + INSERT leaderboard_views for all hitter (view, sort) pairs."""
        total = 0
        for view_key in _VIEW_KEYS:
            pos_filter = _POSITION_FILTER[view_key]
            for sort_stat, sort_asc in _HITTER_VIEWS:
                direction = "ASC" if sort_asc else "DESC"
                if pos_filter:
                    cur.execute(f"""
                        SELECT ps.player_id, ps.stat_value
                        FROM player_stats ps
                        JOIN players pl ON pl.id = ps.player_id
                        WHERE ps.stat_name = %s AND ps.season = %s AND ps.valid_to IS NULL
                          AND pl.primary_pos = %s
                        ORDER BY ps.stat_value {direction} NULLS LAST
                        LIMIT 100
                    """, (sort_stat, season, pos_filter))
                else:
                    cur.execute(f"""
                        SELECT ps.player_id, ps.stat_value
                        FROM player_stats ps
                        WHERE ps.stat_name = %s AND ps.season = %s AND ps.valid_to IS NULL
                        ORDER BY ps.stat_value {direction} NULLS LAST
                        LIMIT 100
                    """, (sort_stat, season))
                rows = cur.fetchall()
                if not rows:
                    continue
                cur.execute(
                    "DELETE FROM leaderboard_views WHERE view_key=%s AND sort_stat=%s AND season=%s",
                    (view_key, sort_stat, season),
                )
                execute_values(cur, """
                    INSERT INTO leaderboard_views
                        (view_key, sort_stat, season, rank, player_id, stat_value, refreshed_at)
                    VALUES %s
                """, [
                    (view_key, sort_stat, season, i + 1, r["player_id"], float(r["stat_value"]), now)
                    for i, r in enumerate(rows)
                ])
                total += len(rows)
        log.info("leaderboard rebuilt: season=%d rows=%d", season, total)
        return total

    # ── Public API ───────────────────────────────────────────────────────────

    def refresh(self, *, season: int) -> RefreshResult:
        now = datetime.now(UTC)
        errors: list[str] = []

        log.info("season_stats refresh start: season=%d", season)
        try:
            splits = self._fetch_hitting_splits(season)
            log.info("fetched %d hitting splits", len(splits))
        except Exception as exc:
            return RefreshResult(season=season, players_upserted=0,
                                 stats_upserted=0, leaderboard_rows=0,
                                 errors=[f"MLB API fetch failed: {exc}"])

        expected = self._fetch_expected_stats(season)
        savant   = self._fetch_savant(season)
        team_map = self._fetch_team_map(season)

        try:
            players, stats, err_count = self._write_to_db(
                season, splits, expected, savant, team_map, now
            )
            if err_count:
                errors.append(f"{err_count} stat write errors (see debug log)")
        except Exception as exc:
            return RefreshResult(season=season, players_upserted=0,
                                 stats_upserted=0, leaderboard_rows=0,
                                 errors=[f"DB write failed: {exc}"])

        log.info("season_stats refresh done: season=%d players=%d stats=%d",
                 season, players, stats)
        return RefreshResult(
            season=season,
            players_upserted=players,
            stats_upserted=stats,
            leaderboard_rows=0,
            errors=errors,
        )
