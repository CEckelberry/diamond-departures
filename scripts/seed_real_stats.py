#!/usr/bin/env python3
"""
Seed real MLB stats from the MLB Stats API for 2025 (and 2026 if in-season).

Usage:
    python3 scripts/seed_real_stats.py

Requires: pip install psycopg2-binary
DATABASE_URL defaults to postgresql://diamond:diamond@localhost:5432/diamond
"""
from __future__ import annotations

import json
import logging
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone
from typing import Any

import psycopg2
from psycopg2.extras import execute_values, RealDictCursor

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("seed")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://diamond:diamond@localhost:5432/diamond")
MLB_API = "https://statsapi.mlb.com/api/v1"
NOW = datetime.now(timezone.utc)
CURRENT_YEAR = NOW.year

# FIP constant approximation (changes slightly year to year, ~3.17 is reasonable)
FIP_CONSTANT = 3.17

# 2026 wRC+ computation constants (FanGraphs-style)
# wOBA weights from packages/stats/hitting/woba_weights_2026.json
WOBA_WEIGHTS = {"bb": 0.69, "hbp": 0.72, "1b": 0.89, "2b": 1.27, "3b": 1.62, "hr": 2.10}
# League-average context (MLB 2026 estimates; update annually)
LEAGUE_WOBA = 0.310
WOBA_SCALE = 1.21
LEAGUE_R_PER_PA = 0.115


def _compute_woba(singles: float, doubles: float, triples: float, hr: float,
                  bb: float, ibb: float, hbp: float, ab: float, sf: float) -> float | None:
    denom = ab + bb - ibb + sf + hbp
    if denom == 0:
        return None
    return (WOBA_WEIGHTS["bb"] * bb + WOBA_WEIGHTS["hbp"] * hbp +
            WOBA_WEIGHTS["1b"] * singles + WOBA_WEIGHTS["2b"] * doubles +
            WOBA_WEIGHTS["3b"] * triples + WOBA_WEIGHTS["hr"] * hr) / denom


def _compute_wrc_plus(singles: float, doubles: float, triples: float, hr: float,
                      bb: float, ibb: float, hbp: float, ab: float, sf: float) -> float | None:
    player_woba = _compute_woba(singles, doubles, triples, hr, bb, ibb, hbp, ab, sf)
    if player_woba is None or WOBA_SCALE == 0 or LEAGUE_R_PER_PA == 0:
        return None
    # Park factor = 1.0 (neutral); adjust if park factors are available
    numerator = ((player_woba - LEAGUE_WOBA) / WOBA_SCALE) + LEAGUE_R_PER_PA
    return round(100 * (numerator / LEAGUE_R_PER_PA))


def _get(path: str) -> dict[str, Any]:
    url = f"{MLB_API}/{path.lstrip('/')}"
    for attempt in range(3):
        try:
            with urllib.request.urlopen(url, timeout=15) as r:  # nosec B310
                return json.loads(r.read())
        except Exception as e:
            if attempt == 2:
                raise
            log.warning("Retrying %s after error: %s", url, e)
            time.sleep(1.5 * (attempt + 1))
    return {}


def fetch_team_map(season: int) -> dict[int, str]:
    """Return {team_id: abbreviation}."""
    data = _get(f"teams?season={season}&sportId=1")
    return {t["id"]: t["abbreviation"] for t in data.get("teams", []) if "abbreviation" in t}


def fetch_stats(group: str, season: int, limit: int = 500) -> list[dict[str, Any]]:
    data = _get(
        f"stats?stats=season&group={group}&season={season}&limit={limit}"
        "&sortStat=homeRuns&playerPool=All&hydrate=person"
    )
    return data.get("stats", [{}])[0].get("splits", [])


def upsert_player(
    cur: Any, player_id: int, full_name: str, short_name: str,
    primary_pos: str, team_abbr: str, headshot_url: str, team_map_db: dict[str, int]
) -> bool:
    team_id = team_map_db.get(team_abbr.upper())
    if team_id is None:
        log.debug("Unknown team abbr %s for %s — skipping", team_abbr, full_name)
        return False
    cur.execute("""
        INSERT INTO players (id, full_name, short_name, primary_pos, team_id, last_seen_at, headshot_url, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, %s, true)
        ON CONFLICT (id) DO UPDATE SET
            full_name = EXCLUDED.full_name, short_name = EXCLUDED.short_name,
            primary_pos = EXCLUDED.primary_pos, team_id = EXCLUDED.team_id,
            last_seen_at = EXCLUDED.last_seen_at, headshot_url = EXCLUDED.headshot_url,
            is_active = true
    """, (player_id, full_name, short_name, primary_pos, team_id, NOW, headshot_url))
    return True


def upsert_stat(cur: Any, player_id: int, stat_name: str, stat_value: float, season: int) -> bool:
    rounded = round(stat_value, 3)
    cur.execute("""
        SELECT id, stat_value FROM player_stats
        WHERE player_id = %s AND stat_name = %s AND season = %s AND valid_to IS NULL
    """, (player_id, stat_name, season))
    existing = cur.fetchone()
    if existing is not None:
        if round(float(existing["stat_value"]), 3) == rounded:
            return False
        cur.execute("UPDATE player_stats SET valid_to = %s WHERE id = %s", (NOW, existing["id"]))
    cur.execute("""
        INSERT INTO player_stats (player_id, stat_name, stat_value, valid_from, valid_to, source, season)
        VALUES (%s, %s, %s, %s, NULL, 'mlb_stats_api', %s)
    """, (player_id, stat_name, rounded, NOW, season))
    return True


def rebuild_leaderboard(cur: Any, season: int) -> None:
    VIEWS = {
        "hitters": [
            ("HR", False), ("RBI", False), ("SB", False), ("AVG", False),
            ("SLG", False), ("OPS", False), ("wRC+", False),
        ],
        "pitchers": [
            ("ERA", True), ("WHIP", True), ("K", False), ("W", False),
            ("L", True), ("SV", False), ("K/9", False), ("BB/9", True),
            ("FIP", True),
        ],
    }

    for view_key, combos in VIEWS.items():
        for sort_stat, reverse in combos:
            cur.execute("""
                SELECT ps.player_id, ps.stat_value
                FROM player_stats ps
                WHERE ps.stat_name = %s AND ps.season = %s AND ps.valid_to IS NULL
                ORDER BY ps.stat_value {dir} NULLS LAST
                LIMIT 100
            """.format(dir="ASC" if reverse else "DESC"), (sort_stat, season))
            rows = cur.fetchall()
            if not rows:
                log.debug("  No data for %s/%s — skipping leaderboard", view_key, sort_stat)
                continue
            cur.execute(
                "DELETE FROM leaderboard_views WHERE view_key = %s AND sort_stat = %s",
                (view_key, sort_stat)
            )
            execute_values(cur, """
                INSERT INTO leaderboard_views (view_key, sort_stat, rank, player_id, stat_value, refreshed_at)
                VALUES %s
            """, [(view_key, sort_stat, i + 1, r["player_id"], float(r["stat_value"]), NOW)
                  for i, r in enumerate(rows)])
            log.info("  leaderboard %s/%s: %d rows", view_key, sort_stat, len(rows))


def seed_season(conn: Any, season: int, team_map_api: dict[int, str], team_map_db: dict[str, int]) -> None:
    hitter_splits = fetch_stats("hitting", season)
    log.info("  Fetched %d hitting splits", len(hitter_splits))
    pitcher_splits = fetch_stats("pitching", season)
    log.info("  Fetched %d pitching splits", len(pitcher_splits))

    saved_players = 0
    saved_stats = 0

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        for split in hitter_splits:
            pa = int(split["stat"].get("plateAppearances", 0))
            if pa < 100:
                continue

            player = split["player"]
            team_id_api = split["team"]["id"]
            team_abbr = team_map_api.get(team_id_api, "")
            if not team_abbr:
                continue

            pid = int(player["id"])
            full_name = player["fullName"]
            short_name = player.get("useLastName") or player.get("lastName") or full_name.split()[-1]
            pos = player.get("primaryPosition", {}).get("abbreviation", "OF")
            headshot = (
                f"https://img.mlbstatic.com/mlb-photos/image/upload/"
                f"d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{pid}/headshot/67/current"
            )

            ok = upsert_player(cur, pid, full_name, short_name, pos, team_abbr, headshot, team_map_db)
            if not ok:
                continue
            saved_players += 1

            stat = split["stat"]
            HITTING_STATS: dict[str, str] = {
                "HR": "homeRuns", "RBI": "rbi", "SB": "stolenBases",
                "AVG": "avg", "OBP": "obp", "SLG": "slg", "OPS": "ops",
            }
            for stat_name, api_key in HITTING_STATS.items():
                val = stat.get(api_key)
                if val is not None and str(val) not in ("", ".---", "-.--"):
                    try:
                        if upsert_stat(cur, pid, stat_name, float(val), season):
                            saved_stats += 1
                    except (ValueError, TypeError):
                        pass

            # Compute derived sabermetric stats from raw components
            try:
                h   = float(stat.get("hits", 0))
                d   = float(stat.get("doubles", 0))
                t   = float(stat.get("triples", 0))
                hr_v = float(stat.get("homeRuns", 0))
                ab_v = float(stat.get("atBats", 0))
                bb_v = float(stat.get("baseOnBalls", 0))
                ibb  = float(stat.get("intentionalWalks", 0))
                hbp  = float(stat.get("hitByPitch", 0))
                sf_v = float(stat.get("sacrificeFlies", 0))
                k_v  = float(stat.get("strikeOuts", 0))
                singles = h - d - t - hr_v

                # BABIP: (H - HR) / (AB - K - HR + SF)
                babip_denom = ab_v - k_v - hr_v + sf_v
                if babip_denom > 0:
                    babip = (h - hr_v) / babip_denom
                    if upsert_stat(cur, pid, "BABIP", babip, season):
                        saved_stats += 1

                # wRC+: FanGraphs-style, computed from raw plate-appearance components
                wrc_plus = _compute_wrc_plus(singles, d, t, hr_v, bb_v, ibb, hbp, ab_v, sf_v)
                if wrc_plus is not None:
                    if upsert_stat(cur, pid, "wRC+", float(wrc_plus), season):
                        saved_stats += 1
            except (ValueError, TypeError):
                pass

        for split in pitcher_splits:
            ip_raw = split["stat"].get("inningsPitched", "0")
            try:
                ip = float(ip_raw)
            except (ValueError, TypeError):
                ip = 0.0
            if ip < 10:
                continue

            player = split["player"]
            team_id_api = split["team"]["id"]
            team_abbr = team_map_api.get(team_id_api, "")
            if not team_abbr:
                continue

            pid = int(player["id"])
            full_name = player["fullName"]
            short_name = player.get("useLastName") or player.get("lastName") or full_name.split()[-1]
            pos = player.get("primaryPosition", {}).get("abbreviation", "P")
            headshot = (
                f"https://img.mlbstatic.com/mlb-photos/image/upload/"
                f"d_people:generic:headshot:67:current.png/w_213,q_auto:best/v1/people/{pid}/headshot/67/current"
            )

            ok = upsert_player(cur, pid, full_name, short_name, pos, team_abbr, headshot, team_map_db)
            if not ok:
                continue
            saved_players += 1

            stat = split["stat"]
            PITCHER_STATS: dict[str, str] = {
                "ERA": "era", "WHIP": "whip", "W": "wins", "L": "losses",
                "SV": "saves", "K": "strikeOuts",
                "K/9": "strikeoutsPer9Inn", "BB/9": "walksPer9Inn",
            }
            for stat_name, api_key in PITCHER_STATS.items():
                val = stat.get(api_key)
                if val is not None and str(val) not in ("", "-.--"):
                    try:
                        if upsert_stat(cur, pid, stat_name, float(val), season):
                            saved_stats += 1
                    except (ValueError, TypeError):
                        pass

            # Compute FIP: (13*HR + 3*(BB+HBP) - 2*K) / IP + FIP_constant
            try:
                hr = float(stat.get("homeRuns", 0))
                bb = float(stat.get("baseOnBalls", 0))
                hbp = float(stat.get("hitByPitch", 0))
                k = float(stat.get("strikeOuts", 0))
                if ip > 0:
                    fip = (13 * hr + 3 * (bb + hbp) - 2 * k) / ip + FIP_CONSTANT
                    if upsert_stat(cur, pid, "FIP", fip, season):
                        saved_stats += 1
            except (ValueError, TypeError):
                pass

        conn.commit()

    log.info("  Season %d: %d players, %d stats upserted", season, saved_players, saved_stats)

    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        rebuild_leaderboard(cur, season)
    conn.commit()


def main() -> None:
    seasons = [2025]
    if CURRENT_YEAR >= 2026:
        seasons.append(2026)

    log.info("Connecting to DB...")
    try:
        conn = psycopg2.connect(DATABASE_URL)
    except Exception as e:
        log.error("DB connection failed: %s", e)
        sys.exit(1)

    # Build DB team map: abbr → id
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("SELECT id, abbr FROM teams")
        team_map_db = {r["abbr"]: r["id"] for r in cur.fetchall()}
    log.info("Loaded %d teams from DB", len(team_map_db))

    for season in seasons:
        log.info("=== Seeding season %d ===", season)
        team_map_api = fetch_team_map(season)
        log.info("Fetched %d teams from MLB API for %d", len(team_map_api), season)
        seed_season(conn, season, team_map_api, team_map_db)

    conn.close()
    log.info("Done.")


if __name__ == "__main__":
    main()
