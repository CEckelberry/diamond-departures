# Real Data Pipeline Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the fake seed data and simulation loop with real MLB season stats (Traditional + Sabermetric + Statcast tabs) for hitters, updated every minute during games and every hour otherwise, with a season selector (2016–current) and a LIVE indicator on the current season.

**Architecture:** A new `SeasonStatsRefresher` class in the ingest service fetches data from two sources (MLB Stats API + Baseball Savant), computes derived stats, upserts to `player_stats`, and rebuilds `leaderboard_views`. The existing runner loop calls this on an adaptive timer. The API drops its fake simulation loop and instead polls `leaderboard_views.refreshed_at` every 30 s to fire SSE updates.

**Tech Stack:** Python/psycopg2 (ingest + API), FastAPI (API), SvelteKit/Svelte 5 (web), PostgreSQL, MLB Stats API (free/public), Baseball Savant (free/public).

**Reference:** `scripts/seed_real_stats.py` already implements the core DB patterns for player/stat upsert and leaderboard rebuild. Every task in this plan builds on or replaces patterns from that file — read it before starting.

---

## File Map

| Action | Path | Responsibility |
|---|---|---|
| Create | `apps/api/migrations/007_leaderboard_season.up.sql` | Add `season` column to `leaderboard_views` |
| Create | `apps/api/migrations/007_leaderboard_season.down.sql` | Rollback |
| Create | `apps/ingest/app/savant_client.py` | HTTP client for Baseball Savant |
| Create | `apps/ingest/app/season_stats.py` | `SeasonStatsRefresher` class |
| Create | `apps/ingest/app/backfill.py` | One-time CLI for 2016–2025 |
| Create | `apps/ingest/tests/test_savant_client.py` | Unit tests for SavantClient |
| Create | `apps/ingest/tests/test_season_stats.py` | Unit tests for SeasonStatsRefresher |
| Create | `apps/web/src/lib/components/board/SeasonPicker.svelte` | Season selector UI |
| Modify | `apps/ingest/app/config.py` | Add 3 new env vars |
| Modify | `apps/ingest/app/runner.py` | Season refresh on adaptive timer |
| Modify | `apps/ingest/app/store.py` | Add `season` to leaderboard DELETE/INSERT |
| Modify | `apps/api/app/config.py` | Add `sse_poll_seconds`, `current_season` |
| Modify | `apps/api/app/board.py` | Add Statcast to `VALID_SORTS` |
| Modify | `apps/api/app/store.py` | `season` param on `postgres_board_reader` |
| Modify | `apps/api/app/main.py` | Remove simulation; add DB poller; `season` query param |
| Modify | `apps/web/src/lib/components/board/ViewTabs.svelte` | Add Statcast style tab |
| Modify | `apps/web/src/lib/components/board/StatPicker.svelte` | Statcast stat list |
| Modify | `apps/web/src/routes/+page.ts` | `season` param + Statcast in `VALID_SORTS`/`resolveSort` |
| Modify | `apps/web/src/routes/+page.svelte` | Render `SeasonPicker` |

---

## Task 1: DB Migration — add `season` to `leaderboard_views`

**Files:**
- Create: `apps/api/migrations/007_leaderboard_season.up.sql`
- Create: `apps/api/migrations/007_leaderboard_season.down.sql`

- [ ] **Step 1: Write the up migration**

```sql
-- apps/api/migrations/007_leaderboard_season.up.sql
ALTER TABLE leaderboard_views ADD COLUMN season int NOT NULL DEFAULT 2026;

ALTER TABLE leaderboard_views
    DROP CONSTRAINT leaderboard_views_view_key_sort_stat_rank_key;

ALTER TABLE leaderboard_views
    ADD CONSTRAINT leaderboard_views_view_key_sort_stat_season_rank_key
    UNIQUE (view_key, sort_stat, season, rank);

DROP INDEX IF EXISTS idx_leaderboard_views_lookup;
CREATE INDEX idx_leaderboard_views_lookup
    ON leaderboard_views (view_key, sort_stat, season, rank);
```

- [ ] **Step 2: Write the down migration**

```sql
-- apps/api/migrations/007_leaderboard_season.down.sql
DROP INDEX IF EXISTS idx_leaderboard_views_lookup;

ALTER TABLE leaderboard_views
    DROP CONSTRAINT leaderboard_views_view_key_sort_stat_season_rank_key;

ALTER TABLE leaderboard_views DROP COLUMN season;

ALTER TABLE leaderboard_views
    ADD CONSTRAINT leaderboard_views_view_key_sort_stat_rank_key
    UNIQUE (view_key, sort_stat, rank);

CREATE INDEX idx_leaderboard_views_lookup
    ON leaderboard_views (view_key, sort_stat, rank);
```

- [ ] **Step 3: Apply the migration**

```bash
make migrate
```

Expected: `migrate: 1/u 007_leaderboard_season (Xms)`

- [ ] **Step 4: Verify**

```bash
docker exec diamond-db psql -U diamond -d diamond -c "\d leaderboard_views"
```

Expected: `season` column present with `integer not null default 2026`.

- [ ] **Step 5: Commit**

```bash
git add apps/api/migrations/007_leaderboard_season.up.sql \
        apps/api/migrations/007_leaderboard_season.down.sql
git commit -m "feat(db): add season column to leaderboard_views"
```

---

## Task 2: SavantClient

**Files:**
- Create: `apps/ingest/app/savant_client.py`
- Create: `apps/ingest/tests/test_savant_client.py`

- [ ] **Step 1: Write failing tests**

```python
# apps/ingest/tests/test_savant_client.py
from __future__ import annotations
from unittest.mock import MagicMock
from apps.ingest.app.savant_client import SavantClient


def _mock_client(payload: dict, status: int = 200) -> SavantClient:
    response = MagicMock()
    response.status_code = status
    response.payload = payload
    client = SavantClient(base_url="https://baseballsavant.mlb.com")
    client._mlb_client.request_fn = MagicMock(return_value=response)
    return client


def test_fetch_statcast_returns_list():
    client = _mock_client({"players": [
        {"player_id": "660271", "barrel_batted_rate": 0.15,
         "hard_hit_percent": 0.52, "avg_hit_speed": 95.2,
         "xwoba": 0.410, "xba": 0.285}
    ]})
    result = client.fetch_statcast(year=2026)
    assert len(result) == 1
    assert result[0]["player_id"] == 660271
    assert result[0]["barrel_pct"] == 0.15


def test_fetch_statcast_empty_on_missing_key():
    client = _mock_client({})
    result = client.fetch_statcast(year=2026)
    assert result == []
```

- [ ] **Step 2: Run to verify failure**

```bash
cd /path/to/diamond-departures
python -m pytest apps/ingest/tests/test_savant_client.py -v
```

Expected: `ImportError` or `ModuleNotFoundError` — `savant_client` doesn't exist yet.

- [ ] **Step 3: Implement SavantClient**

```python
# apps/ingest/app/savant_client.py
from __future__ import annotations

from .mlb_client import MLBApiClient


class SavantClient:
    """Thin wrapper around Baseball Savant's leaderboard endpoint.

    Uses the same MLBApiClient retry/backoff pattern, different base URL.
    The Savant leaderboard returns a JSON object with a top-level key
    that varies by endpoint; we normalise the response to a list of dicts
    with snake_case keys matching our stat_name conventions.
    """

    def __init__(
        self,
        base_url: str = "https://baseballsavant.mlb.com",
        timeout_seconds: int = 15,
        max_retries: int = 3,
    ) -> None:
        self._mlb_client = MLBApiClient(
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            max_retries=max_retries,
        )

    def fetch_statcast(self, *, year: int) -> list[dict]:
        """Return list of Statcast batting metrics for all qualified hitters.

        Each dict has keys: player_id (int), barrel_pct, hard_hit_pct,
        exit_velocity, xwoba, xba (all float).
        """
        path = (
            f"/leaderboard/expected_statistics"
            f"?type=batter&year={year}&position=&team=&min=q"
        )
        response = self._mlb_client.get_json(path)
        raw = response.payload

        players = raw.get("players") or raw.get("leaderboard") or []
        if not players:
            return []

        result = []
        for item in players:
            try:
                result.append({
                    "player_id": int(item["player_id"]),
                    "barrel_pct": float(item.get("barrel_batted_rate") or 0),
                    "hard_hit_pct": float(item.get("hard_hit_percent") or 0),
                    "exit_velocity": float(item.get("avg_hit_speed") or 0),
                    "xwoba": float(item.get("xwoba") or 0),
                    "xba": float(item.get("xba") or 0),
                })
            except (KeyError, TypeError, ValueError):
                continue
        return result
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest apps/ingest/tests/test_savant_client.py -v
```

Expected: 2 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add apps/ingest/app/savant_client.py apps/ingest/tests/test_savant_client.py
git commit -m "feat(ingest): add SavantClient for Baseball Savant leaderboard"
```

---

## Task 3: SeasonStatsRefresher — fetch and compute

**Files:**
- Create: `apps/ingest/app/season_stats.py`
- Create: `apps/ingest/tests/test_season_stats.py` (partial — extended in Task 4)

The logic here is extracted and refactored from `scripts/seed_real_stats.py`. Read that file thoroughly before starting — especially `fetch_stats`, `_compute_woba`, `_compute_wrc_plus`, and the stat key mappings.

- [ ] **Step 1: Write failing tests for fetch and compute**

```python
# apps/ingest/tests/test_season_stats.py
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
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest apps/ingest/tests/test_season_stats.py -v
```

Expected: `ImportError` — `season_stats` doesn't exist yet.

- [ ] **Step 3: Implement SeasonStatsRefresher fetch + compute**

```python
# apps/ingest/app/season_stats.py
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

# wOBA weights — use 2026 coefficients as a reasonable approximation for all years.
# Update per-year if precision matters.
_WOBA_WEIGHTS = {"bb": 0.69, "hbp": 0.72, "1b": 0.89, "2b": 1.27, "3b": 1.62, "hr": 2.10}
_LEAGUE_WOBA = 0.310
_WOBA_SCALE = 1.21
_LEAGUE_R_PER_PA = 0.115

# Minimum plate appearances for a player to be included
_MIN_PA = 100

# Which views to populate and whether the stat sorts ascending (True) or descending (False)
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

    # ── Data fetching ────────────────────────────────────────────────────────

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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
python -m pytest apps/ingest/tests/test_season_stats.py -v
```

Expected: 4 tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add apps/ingest/app/season_stats.py apps/ingest/tests/test_season_stats.py
git commit -m "feat(ingest): add SeasonStatsRefresher fetch + compute"
```

---

## Task 4: SeasonStatsRefresher — DB writes and full refresh

**Files:**
- Modify: `apps/ingest/app/season_stats.py` (add `refresh()` and DB write methods)
- Modify: `apps/ingest/app/store.py` (add `season` to leaderboard DELETE/INSERT)
- Modify: `apps/ingest/tests/test_season_stats.py` (add integration-style test)

- [ ] **Step 1: Add integration test for full refresh cycle**

Add to `apps/ingest/tests/test_season_stats.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure (method not yet implemented)**

```bash
python -m pytest apps/ingest/tests/test_season_stats.py::test_refresh_result_fields -v
```

Expected: `AttributeError: 'SeasonStatsRefresher' object has no attribute '_write_to_db'`

- [ ] **Step 3: Implement DB write methods and refresh() on SeasonStatsRefresher**

Append to `apps/ingest/app/season_stats.py` (inside the class, after `_fetch_team_map`):

```python
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
                # Load DB team map: abbr → id
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

                    # Upsert player row
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

                    # Build raw stat dict for derived-stat computation
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

                    # Direct API stats
                    all_stats: dict[str, float] = {}
                    for stat_name, api_key in _HITTING_API_KEYS.items():
                        val = split["stat"].get(api_key)
                        if val is not None and str(val) not in ("", ".---", "-.--"):
                            try:
                                all_stats[stat_name] = float(val)
                            except (ValueError, TypeError):
                                pass

                    # Derived stats
                    all_stats.update(_compute_derived(raw))

                    # Expected stats (xwOBA, xBA) from MLB API
                    if pid in expected:
                        all_stats.update(expected[pid])

                    # Statcast (barrel_pct, hard_hit_pct, exit_velocity) from Savant
                    if pid in savant:
                        sv = savant[pid]
                        all_stats["barrel_pct"]    = sv["barrel_pct"]
                        all_stats["hard_hit_pct"]  = sv["hard_hit_pct"]
                        all_stats["exit_velocity"] = sv["exit_velocity"]

                    # Write stats
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

                # Rebuild leaderboards for this season
                self._rebuild_leaderboards(cur, season=season, now=now)
                conn.commit()

        return players_upserted, stats_upserted, error_count

    def _rebuild_leaderboards(self, cur: Any, *, season: int, now: datetime) -> int:
        """DELETE + INSERT leaderboard_views for all hitter (view, sort) pairs. Returns row count."""
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
```

Also add `from typing import Any` at the top of `season_stats.py` if not already present.

- [ ] **Step 3b: Update `in_memory_board_reader` to accept optional season**

In `apps/api/app/board.py`, update the stub so existing tests that call `board_reader(view, sort)` still work after the signature change:

```python
def in_memory_board_reader(view: str, sort: str, season: int = 2026) -> list[dict[str, Any]]:
    del view, sort, season
    return []
```

- [ ] **Step 4: Update `store.py` — add season to leaderboard DELETE/INSERT**

The existing `save_leaderboard_rows` in `apps/ingest/app/store.py` omits `season`. Update it to be season-aware (this also fixes the live-game path if it ever writes leaderboard rows):

```python
# In apps/ingest/app/store.py — replace save_leaderboard_rows

    def save_leaderboard_rows(self, rows: list[Any]) -> None:
        if not rows:
            return
        try:
            with psycopg2.connect(self.database_url) as conn:
                with conn.cursor() as cur:
                    targets = set((row.view_key, row.sort_stat, getattr(row, 'season', 2026)) for row in rows)
                    for vk, ss, season in targets:
                        cur.execute(
                            "DELETE FROM leaderboard_views WHERE view_key=%s AND sort_stat=%s AND season=%s",
                            (vk, ss, season),
                        )
                    execute_values(
                        cur,
                        """
                        INSERT INTO leaderboard_views
                            (view_key, sort_stat, season, rank, player_id, stat_value, refreshed_at)
                        VALUES %s
                        """,
                        [
                            (r.view_key, r.sort_stat, getattr(r, 'season', 2026),
                             r.rank, r.player_id, r.stat_value, r.refreshed_at)
                            for r in rows
                        ],
                    )
        except Exception as e:
            logging.getLogger("apps.ingest.store").error("failed to save leaderboard: %s", e)
```

- [ ] **Step 5: Run all season_stats tests**

```bash
python -m pytest apps/ingest/tests/test_season_stats.py -v
```

Expected: all tests PASSED.

- [ ] **Step 6: Smoke test against local stack (optional but recommended)**

```bash
docker exec diamond-api python -c "
from apps.ingest.app.season_stats import SeasonStatsRefresher
r = SeasonStatsRefresher(
    database_url='postgresql://diamond:diamond@db:5432/diamond',
    mlb_api_url='http://mlb-mock:8090',
)
result = r.refresh(season=2026)
print(result)
"
```

Expected: `RefreshResult(season=2026, players_upserted=..., ...)` with no fatal errors.

- [ ] **Step 7: Commit**

```bash
git add apps/ingest/app/season_stats.py apps/ingest/app/store.py \
        apps/ingest/tests/test_season_stats.py
git commit -m "feat(ingest): SeasonStatsRefresher DB writes + leaderboard rebuild"
```

---

## Task 5: IngestSettings new config vars

**Files:**
- Modify: `apps/ingest/app/config.py`
- Modify: `apps/ingest/tests/test_config.py`

- [ ] **Step 1: Write failing test**

Add to `apps/ingest/tests/test_config.py`:

```python
def test_season_refresh_defaults():
    from apps.ingest.app.config import load_settings
    settings = load_settings()
    assert settings.season_refresh_live_seconds == 60
    assert settings.season_refresh_idle_seconds == 3600
    assert settings.current_season >= 2026
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest apps/ingest/tests/test_config.py::test_season_refresh_defaults -v
```

Expected: `AttributeError: 'IngestSettings' object has no attribute 'season_refresh_live_seconds'`

- [ ] **Step 3: Add the three new fields to IngestSettings**

In `apps/ingest/app/config.py`, add to `IngestSettings` dataclass and `load_settings()`:

```python
# Add to IngestSettings dataclass
season_refresh_live_seconds: int
season_refresh_idle_seconds: int
current_season: int
```

```python
# Add to load_settings() return value
season_refresh_live_seconds=max(10, int(os.getenv("SEASON_REFRESH_LIVE_SECONDS", "60"))),
season_refresh_idle_seconds=max(60, int(os.getenv("SEASON_REFRESH_IDLE_SECONDS", "3600"))),
current_season=int(os.getenv("CURRENT_SEASON", str(datetime.now(UTC).year))),
```

Add `from datetime import UTC, datetime` at the top of `config.py` if not already present.

- [ ] **Step 4: Run tests**

```bash
python -m pytest apps/ingest/tests/test_config.py -v
```

Expected: all tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add apps/ingest/app/config.py apps/ingest/tests/test_config.py
git commit -m "feat(ingest): add season refresh config vars"
```

---

## Task 6: Runner integration

**Files:**
- Modify: `apps/ingest/app/runner.py`
- Modify: `apps/ingest/tests/test_runner.py`

- [ ] **Step 1: Write failing test**

Add to `apps/ingest/tests/test_runner.py`:

```python
def test_season_refresh_called_when_due():
    """run_loop calls season refresh when interval has elapsed."""
    from unittest.mock import MagicMock, patch
    from datetime import UTC, datetime, timedelta
    from apps.ingest.app.runner import run_loop
    from apps.ingest.app.config import IngestSettings

    settings = IngestSettings(
        mlb_api_url="http://mock",
        database_url="postgresql://x",
        log_level="INFO",
        environment="test",
        request_timeout_seconds=5,
        max_http_retries=0,
        retry_backoff_seconds=0,
        provider_source="mlb_stats",
        live_scanner_mode="all",
        game_changes_lookback_seconds=30,
        scanner_checkpoint_path="/tmp/cp.json",
        reconcile_every_n_scans=10,
        scan_interval_live_seconds=15,
        scan_interval_idle_seconds=60,
        scanner_report_path="/tmp/report.json",
        season_refresh_live_seconds=60,
        season_refresh_idle_seconds=3600,
        current_season=2026,
    )

    mock_run_once = MagicMock(return_value={"status": "ok", "live_games": [], "snapshot": set()})
    mock_refresh = MagicMock()
    mock_sleep = MagicMock()

    with patch("apps.ingest.app.runner.SeasonStatsRefresher") as MockRefresher:
        MockRefresher.return_value.refresh = mock_refresh
        run_loop(
            max_iterations=2,
            settings=settings,
            run_once_fn=mock_run_once,
            sleep_fn=mock_sleep,
        )

    assert mock_refresh.called
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest apps/ingest/tests/test_runner.py::test_season_refresh_called_when_due -v
```

Expected: failure — `SeasonStatsRefresher` not imported in runner.

- [ ] **Step 3: Update runner.py**

Replace the contents of `apps/ingest/app/runner.py` with:

```python
from __future__ import annotations

import json
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable

from .config import IngestSettings, load_settings
from .job import run_once
from .season_stats import SeasonStatsRefresher


def _iso_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace('+00:00', 'Z')


def _write_report(path: str, payload: dict[str, Any]) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + '.tmp')
    tmp.write_text(json.dumps(payload, indent=2) + '\n', encoding='utf-8')
    tmp.replace(target)


def run_loop(
    *,
    max_iterations: int | None = None,
    settings: IngestSettings | None = None,
    run_once_fn: Callable[..., dict[str, Any]] = run_once,
    sleep_fn: Callable[[float], None] = time.sleep,
) -> None:
    resolved = settings or load_settings()
    refresher = SeasonStatsRefresher(
        database_url=resolved.database_url,
        mlb_api_url=resolved.mlb_api_url,
    )
    previous_snapshot: set[str] | None = None
    last_season_refresh: datetime | None = None
    iteration = 0

    while True:
        result = run_once_fn(previous_snapshot=previous_snapshot)
        iteration += 1
        snapshot = result.get('snapshot')
        if isinstance(snapshot, set):
            previous_snapshot = snapshot

        has_live_games = bool(result.get('live_games'))
        refresh_interval = (
            resolved.season_refresh_live_seconds
            if has_live_games
            else resolved.season_refresh_idle_seconds
        )

        now = datetime.now(UTC)
        since_last = (now - last_season_refresh).total_seconds() if last_season_refresh else None
        if since_last is None or since_last >= refresh_interval:
            try:
                refresh_result = refresher.refresh(season=resolved.current_season)
                if refresh_result.errors:
                    import logging
                    logging.getLogger("apps.ingest.runner").warning(
                        "season refresh errors: %s", refresh_result.errors
                    )
            except Exception as exc:
                import logging
                logging.getLogger("apps.ingest.runner").error("season refresh failed: %s", exc)
            last_season_refresh = now

        report = {
            'iteration': iteration,
            'written_at': _iso_now(),
            'status': result.get('status'),
            'scanner_mode': result.get('scanner_mode'),
            'live_games_count': len(result.get('live_games', [])),
            'changed_games_count': result.get('changed_games_count', 0),
            'event_count': result.get('event_count', 0),
            'update_count': result.get('update_count', 0),
            'scanner_scan_count': result.get('scanner_scan_count', 0),
            'reconcile_triggered': bool(result.get('reconcile_triggered', False)),
            'reconcile_games_count': result.get('reconcile_games_count', 0),
            'error': result.get('error'),
        }
        _write_report(resolved.scanner_report_path, report)

        if max_iterations is not None and iteration >= max_iterations:
            return

        sleep_seconds = (
            resolved.scan_interval_live_seconds
            if has_live_games
            else resolved.scan_interval_idle_seconds
        )
        sleep_fn(float(sleep_seconds))
```

- [ ] **Step 4: Run all runner tests**

```bash
python -m pytest apps/ingest/tests/test_runner.py -v
```

Expected: all tests PASSED (including new one).

- [ ] **Step 5: Commit**

```bash
git add apps/ingest/app/runner.py apps/ingest/tests/test_runner.py
git commit -m "feat(ingest): wire season refresh into run_loop"
```

---

## Task 7: Historical backfill script

**Files:**
- Create: `apps/ingest/app/backfill.py`

- [ ] **Step 1: Create backfill.py**

```python
# apps/ingest/app/backfill.py
"""One-time CLI to backfill season stats for 2016 through last year.

Usage:
    python -m apps.ingest.app.backfill
    python -m apps.ingest.app.backfill --start-year 2020 --end-year 2023
    python -m apps.ingest.app.backfill --dry-run

Skips any year that already has player_stats rows for that season.
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from datetime import UTC, datetime

import psycopg2
from psycopg2.extras import RealDictCursor

from .config import load_settings
from .season_stats import SeasonStatsRefresher

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("backfill")


def _season_has_data(database_url: str, season: int) -> bool:
    try:
        with psycopg2.connect(database_url) as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT 1 FROM player_stats WHERE season = %s LIMIT 1",
                    (season,),
                )
                return cur.fetchone() is not None
    except Exception as exc:
        log.warning("Could not check season %d: %s", season, exc)
        return False


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Backfill historical season stats")
    parser.add_argument("--start-year", type=int, default=2016)
    parser.add_argument("--end-year",   type=int, default=datetime.now(UTC).year - 1)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    settings = load_settings()
    refresher = SeasonStatsRefresher(
        database_url=settings.database_url,
        mlb_api_url=settings.mlb_api_url,
    )

    years = list(range(args.start_year, args.end_year + 1))
    log.info("Backfill plan: %s", years)

    for year in years:
        if _season_has_data(settings.database_url, year):
            log.info("Season %d already has data — skipping", year)
            continue
        if args.dry_run:
            log.info("[dry-run] Would refresh season %d", year)
            continue
        log.info("Refreshing season %d ...", year)
        result = refresher.refresh(season=year)
        log.info(
            "Season %d done: players=%d stats=%d errors=%s",
            year, result.players_upserted, result.stats_upserted, result.errors,
        )
        time.sleep(2)  # be polite to the APIs

    log.info("Backfill complete.")


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Smoke-test the CLI help (no DB needed)**

```bash
python -m apps.ingest.app.backfill --help
```

Expected: usage message printed without error.

- [ ] **Step 3: Commit**

```bash
git add apps/ingest/app/backfill.py
git commit -m "feat(ingest): add historical backfill CLI script"
```

---

## Task 8: API — config, VALID_SORTS, season param on board reader

**Files:**
- Modify: `apps/api/app/config.py`
- Modify: `apps/api/app/board.py`
- Modify: `apps/api/app/store.py`

- [ ] **Step 1: Write failing tests**

Add to `apps/api/tests/test_board.py`:

```python
def test_valid_sorts_includes_statcast():
    from apps.api.app.board import VALID_SORTS
    for stat in ("xBA", "barrel_pct", "hard_hit_pct", "exit_velocity"):
        assert stat in VALID_SORTS, f"{stat} missing from VALID_SORTS"


def test_board_reader_filters_by_season(monkeypatch):
    """postgres_board_reader passes season to the SQL query."""
    from unittest.mock import MagicMock, patch
    from apps.api.app.store import postgres_board_reader
    mock_rows = [{"rank": 1, "player_id": 1, "player_name": "X",
                  "team_abbr": "LAD", "headshot_url": None,
                  "position": "DH", "stat_value": 1.0,
                  "refreshed_at": "2026-06-01T00:00:00+00:00",
                  "additional_stats": {}}]
    with patch("psycopg2.connect") as mock_conn:
        mock_cur = MagicMock()
        mock_cur.__enter__ = lambda s: s
        mock_cur.__exit__ = MagicMock(return_value=False)
        mock_cur.fetchall.return_value = mock_rows
        mock_conn.return_value.__enter__.return_value.cursor.return_value = mock_cur
        reader = postgres_board_reader("postgresql://fake")
        reader("hitters", "wRC+", season=2025)
        call_args = mock_cur.execute.call_args
        assert "2025" in str(call_args) or 2025 in call_args[0][1]
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest apps/api/tests/test_board.py::test_valid_sorts_includes_statcast \
                  apps/api/tests/test_board.py::test_board_reader_filters_by_season -v
```

Expected: FAIL on both — `xBA` not in VALID_SORTS, reader doesn't accept `season`.

- [ ] **Step 3: Update config.py**

```python
# apps/api/app/config.py
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass(frozen=True)
class ApiSettings:
    port: int = 8081
    log_level: str = "INFO"
    database_url: str = "postgresql://diamond:diamond@localhost:5432/diamond"
    sse_poll_seconds: float = 30.0
    current_season: int = field(default_factory=lambda: datetime.now(UTC).year)


def load_settings() -> ApiSettings:
    return ApiSettings(
        port=int(os.getenv("PORT", "8081")),
        log_level=os.getenv("LOG_LEVEL", "INFO").upper(),
        database_url=os.getenv("DATABASE_URL", "postgresql://diamond:diamond@localhost:5432/diamond"),
        sse_poll_seconds=float(os.getenv("SSE_POLL_SECONDS", "30")),
        current_season=int(os.getenv("CURRENT_SEASON", str(datetime.now(UTC).year))),
    )
```

- [ ] **Step 4: Update VALID_SORTS in board.py**

In `apps/api/app/board.py`, add to the `VALID_SORTS` set:

```python
VALID_SORTS = {
    "wRC+", "OPS", "HR", "SB", "WAR", "AVG", "RBI", "SLG", "OPS+", "DRS", "xwOBA", "H",
    "ERA", "FIP", "K%", "WHIP", "W", "SV", "K", "K-BB%", "K/9", "BB/9", "xFIP",
    "OAA", "UZR", "Fielding %", "Def", "E",
    "wOBA", "ISO", "BABIP", "BB%",
    # Statcast
    "xBA", "barrel_pct", "hard_hit_pct", "exit_velocity",
    # Traditional extras
    "OBP",
}
```

- [ ] **Step 5: Update postgres_board_reader in store.py to accept season**

Replace the `postgres_board_reader` function in `apps/api/app/store.py`:

```python
def postgres_board_reader(database_url: str) -> Callable[[str, str, int], list[dict[str, Any]]]:
    def _read(view: str, sort: str, season: int = 2026) -> list[dict[str, Any]]:
        try:
            with psycopg2.connect(database_url) as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT
                            lv.rank,
                            p.id as player_id,
                            p.full_name as player_name,
                            t.abbr as team_abbr,
                            p.headshot_url,
                            p.primary_pos as position,
                            lv.stat_value,
                            lv.refreshed_at,
                            COALESCE(
                                jsonb_object_agg(ps.stat_name, ps.stat_value)
                                    FILTER (WHERE ps.stat_name IS NOT NULL),
                                '{}'::jsonb
                            ) as additional_stats
                        FROM leaderboard_views lv
                        JOIN players p ON lv.player_id = p.id
                        JOIN teams t ON p.team_id = t.id
                        LEFT JOIN player_stats ps
                            ON ps.player_id = p.id
                           AND ps.season = lv.season
                           AND ps.valid_to IS NULL
                        WHERE lv.view_key = %s
                          AND lv.sort_stat = %s
                          AND lv.season = %s
                        GROUP BY lv.rank, p.id, p.full_name, t.abbr,
                                 p.headshot_url, p.primary_pos,
                                 lv.stat_value, lv.refreshed_at
                        ORDER BY lv.rank ASC
                        LIMIT 50
                    """, (view, sort, season))
                    return list(cur.fetchall())
        except Exception as e:
            logging.getLogger("apps.api.store").error("failed to read board: %s", e)
            return []
    return _read
```

- [ ] **Step 6: Run tests**

```bash
python -m pytest apps/api/tests/test_board.py -v
```

Expected: all tests PASSED.

- [ ] **Step 7: Commit**

```bash
git add apps/api/app/config.py apps/api/app/board.py apps/api/app/store.py \
        apps/api/tests/test_board.py
git commit -m "feat(api): season param on board reader + Statcast VALID_SORTS"
```

---

## Task 9: API — remove simulation loop, add DB-change poller, season query param

**Files:**
- Modify: `apps/api/app/main.py`

- [ ] **Step 1: Write failing test for season param**

Add to `apps/api/tests/test_board.py`:

```python
def test_board_endpoint_accepts_season_param(monkeypatch):
    from fastapi.testclient import TestClient
    from unittest.mock import MagicMock, patch

    fake_rows = [{
        "rank": 1, "player_id": 1, "player_name": "Ohtani",
        "team_abbr": "LAD", "headshot_url": None, "position": "DH",
        "stat_value": 1.059, "refreshed_at": "2026-06-01T00:00:00+00:00",
        "additional_stats": {},
    }]
    with patch("apps.api.app.store.postgres_board_reader", return_value=lambda v, s, season=2026: fake_rows), \
         patch("apps.api.app.store.postgres_health_check", return_value=lambda: True):
        from apps.api.app.main import create_app
        app = create_app()
        client = TestClient(app)
        resp = client.get("/api/board?view=hitters&sort=wRC+&season=2025")
        assert resp.status_code == 200
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest apps/api/tests/test_board.py::test_board_endpoint_accepts_season_param -v
```

Expected: FAIL — `/api/board` doesn't accept `season` param yet.

- [ ] **Step 3: Rewrite the bottom of main.py**

Replace everything from the `create_app` function downward in `apps/api/app/main.py`. The key changes: (a) add `season: int` query param to `/api/board` and `/api/board/sse`; (b) remove the entire `simulation_loop`, `start_simulation`, and `@app.on_event("startup")` block; (c) add a `db_poll_loop` background task.

```python
def create_app(
    settings: ApiSettings | None = None,
    db_health_check: Callable[[], bool] | None = None,
    board_reader: BoardReader | None = None,
    sse_hub: BoardSSEHub | None = None,
    sse_heartbeat_seconds: float = 30.0,
    player_detail_reader: PlayerDetailReader | None = None,
    player_history_reader: PlayerHistoryReader | None = None,
    season_state_reader: SeasonStateReader | None = None,
    freshness_reader: FreshnessReader | None = None,
) -> FastAPI:
    resolved_settings = settings or load_settings()
    configure_logging(resolved_settings.log_level)

    app = FastAPI(title="diamond-departures-api")
    app.state.settings = resolved_settings
    logger = logging.getLogger("apps.api")
    checker = db_health_check or postgres_health_check(resolved_settings.database_url)
    board_loader = board_reader or postgres_board_reader(resolved_settings.database_url)
    hub = sse_hub or BoardSSEHub(heartbeat_seconds=sse_heartbeat_seconds)
    detail_loader = player_detail_reader or postgres_player_detail_reader(resolved_settings.database_url)
    history_loader = player_history_reader or postgres_player_history_reader(resolved_settings.database_url)
    season_state_loader = season_state_reader or in_memory_season_state_reader
    freshness_loader = freshness_reader or in_memory_freshness_reader
    app.state.sse_hub = hub

    @app.get("/api/health")
    def health() -> JSONResponse:
        db_ok = checker()
        payload = {
            "status": "ok" if db_ok else "degraded",
            "checks": {"database": "reachable" if db_ok else "unreachable"},
        }
        if not db_ok:
            logger.warning("health check degraded: database unreachable")
        return JSONResponse(status_code=200 if db_ok else 503, content=payload)

    @app.get("/api/board")
    def board(
        view: str = Query(...),
        sort: str = Query(...),
        season: int = Query(default=None),
    ) -> JSONResponse:
        _validate_view_sort(view, sort)
        effective_season = season if season is not None else resolved_settings.current_season
        rows = board_loader(view, sort, effective_season)[:100]
        return JSONResponse(content={
            "view": view, "sort": sort,
            "season": effective_season,
            "entries": _entries_from_rows(rows),
        })

    @app.get("/api/board/sse")
    async def board_sse(
        view: str = Query(...),
        sort: str = Query(...),
        season: int = Query(default=None),
    ) -> StreamingResponse:
        _validate_view_sort(view, sort)
        effective_season = season if season is not None else resolved_settings.current_season
        rows = board_loader(view, sort, effective_season)[:100]
        return StreamingResponse(
            hub.stream(view, sort, _entries_from_rows(rows)),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @app.get("/api/players/{player_id}")
    def player_detail(player_id: int) -> JSONResponse:
        detail = detail_loader(player_id)
        if detail is None:
            raise HTTPException(status_code=404, detail=f"Player '{player_id}' not found")
        return JSONResponse(content=detail)

    @app.get("/api/players/{player_id}/history")
    def player_history(player_id: int, stat: str | None = Query(default=None)) -> JSONResponse:
        if stat is None or stat not in VALID_HISTORY_STATS:
            raise HTTPException(status_code=400, detail="Invalid stat")
        history = history_loader(player_id, stat)
        if history is None:
            raise HTTPException(status_code=404, detail=f"Player '{player_id}' not found")
        sorted_history = sorted(history, key=lambda row: str(row["timestamp"]))
        return JSONResponse(content={"player_id": player_id, "stat": stat, "points": sorted_history})

    @app.get("/api/season-state")
    def season_state() -> JSONResponse:
        payload = season_state_loader()
        if payload.get("mode") not in VALID_SEASON_MODES:
            raise HTTPException(status_code=500, detail="Invalid season mode")
        return JSONResponse(content=payload, headers={"Cache-Control": "public, max-age=300"})

    @app.get("/api/freshness")
    def freshness() -> JSONResponse:
        return JSONResponse(content=freshness_loader(), headers={"Cache-Control": "no-store"})

    @app.on_event("startup")
    async def start_db_poller() -> None:
        import asyncio
        asyncio.create_task(_db_poll_loop(
            hub=hub,
            board_loader=board_loader,
            current_season=resolved_settings.current_season,
            poll_seconds=resolved_settings.sse_poll_seconds,
            logger=logger,
        ))

    return app


async def _db_poll_loop(
    *,
    hub: BoardSSEHub,
    board_loader: BoardReader,
    current_season: int,
    poll_seconds: float,
    logger: logging.Logger,
) -> None:
    import asyncio
    last_seen: dict[tuple, str] = {}

    while True:
        await asyncio.sleep(poll_seconds)
        try:
            with hub._lock:
                active_keys = list(hub._connections.keys())
            for view, sort in active_keys:
                rows = board_loader(view, sort, current_season)
                if not rows:
                    continue
                ts = str(rows[0]["refreshed_at"])
                key = (view, sort)
                if last_seen.get(key) != ts:
                    last_seen[key] = ts
                    entries = _entries_from_rows(rows)
                    hub.publish_snapshot(view, sort, entries)
                    logger.debug("SSE snapshot published: %s/%s", view, sort)
        except Exception as exc:
            logger.warning("db_poll_loop error: %s", exc)


app = create_app()
```

Note: `BoardReader` type signature in `board.py` needs updating to `Callable[[str, str, int], list[dict[str, Any]]]`. Update it there:

```python
# In apps/api/app/board.py
BoardReader = Callable[[str, str, int], list[dict[str, Any]]]
```

- [ ] **Step 4: Run API tests**

```bash
python -m pytest apps/api/tests/ -v
```

Expected: all tests PASSED.

- [ ] **Step 5: Commit**

```bash
git add apps/api/app/main.py apps/api/app/board.py
git commit -m "feat(api): replace simulation with DB-change poller; add season query param"
```

---

## Task 10: Web — Statcast tab

**Files:**
- Modify: `apps/web/src/lib/components/board/ViewTabs.svelte`
- Modify: `apps/web/src/lib/components/board/StatPicker.svelte`
- Modify: `apps/web/src/routes/+page.ts`

- [ ] **Step 1: Add Statcast to ViewTabs style tabs**

In `apps/web/src/lib/components/board/ViewTabs.svelte`, update the `StyleKey` type and add the Statcast button:

Change line 8:
```typescript
type StyleKey = "sabermetric" | "traditional" | "statcast";
```

Add `preloadStyle("statcast")` function (same pattern as the existing ones).

In the template, add after the Traditional button:
```svelte
<button
    class:active={currentStyle === "statcast"}
    role="tab"
    onmouseenter={() => preloadStyle("statcast")}
    onclick={() => chooseStyle("statcast")}
>Statcast</button>
```

- [ ] **Step 2: Add Statcast stat list to StatPicker**

In `apps/web/src/lib/components/board/StatPicker.svelte`, add:

```typescript
const HITTER_STATCAST_STATS = ['xwOBA', 'xBA', 'barrel_pct', 'hard_hit_pct', 'exit_velocity'];
```

Update `derivedStats`:

```typescript
const derivedStats = $derived(
    view.startsWith('pitcher')
        ? (style === 'traditional' ? PITCHER_TRAD_STATS : PITCHER_SABER_STATS)
        : style === 'statcast'
            ? HITTER_STATCAST_STATS
            : style === 'traditional'
                ? HITTER_TRAD_STATS
                : HITTER_SABER_STATS
);
```

- [ ] **Step 3: Update +page.ts — VALID_SORTS and resolveSort**

In `apps/web/src/routes/+page.ts`, add Statcast stats to `VALID_SORTS`:

```typescript
const VALID_SORTS = new Set([
    "wRC+", "OPS", "OPS+", "HR", "SB", "WAR", "AVG", "RBI", "SLG", "H",
    "DRS", "xwOBA", "ERA", "FIP", "K%", "K/9", "WHIP", "W", "SV", "K",
    "K-BB%", "BB/9", "xFIP", "OAA", "UZR", "Fielding %", "Def", "E",
    "wOBA", "ISO", "BABIP", "BB%", "OBP",
    // Statcast
    "xBA", "barrel_pct", "hard_hit_pct", "exit_velocity",
]);
```

Update `resolveSort` default for Statcast style:

```typescript
function resolveSort(params: URLSearchParams, apiView: string): string {
    const fromUrl = params.get("sort") ?? "";
    if (VALID_SORTS.has(fromUrl)) return fromUrl;
    const style = params.get("style") ?? "sabermetric";
    if (apiView === "defense") return style === "sabermetric" ? "OAA" : "Fielding %";
    if (apiView.startsWith("pitchers")) return style === "sabermetric" ? "FIP" : "W";
    if (style === "statcast") return "xwOBA";
    if (style === "traditional") return "AVG";
    return "OPS";
}
```

- [ ] **Step 4: Rebuild and verify in browser**

```bash
docker compose up -d --build web
```

Navigate to the board. Confirm three style tabs appear: Saber, Traditional, Statcast. Click Statcast — confirm stat buttons show `xwOBA`, `xBA`, `barrel_pct`, `hard_hit_pct`, `exit_velocity`.

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/lib/components/board/ViewTabs.svelte \
        apps/web/src/lib/components/board/StatPicker.svelte \
        apps/web/src/routes/+page.ts
git commit -m "feat(web): add Statcast tab to board style selector"
```

---

## Task 11: Web — season selector

**Files:**
- Create: `apps/web/src/lib/components/board/SeasonPicker.svelte`
- Modify: `apps/web/src/routes/+page.svelte`
- Modify: `apps/web/src/routes/+page.ts`

- [ ] **Step 1: Create SeasonPicker component**

```svelte
<!-- apps/web/src/lib/components/board/SeasonPicker.svelte -->
<script lang="ts">
    import { goto } from '$app/navigation';
    import { page } from '$app/stores';

    const CURRENT_YEAR = new Date().getFullYear();
    const YEARS = Array.from({ length: CURRENT_YEAR - 2016 + 1 }, (_, i) => CURRENT_YEAR - i);

    const activeSeason = $derived(
        parseInt($page.url.searchParams.get('season') ?? String(CURRENT_YEAR))
    );

    function chooseSeason(year: number) {
        const params = new URLSearchParams($page.url.searchParams);
        if (year === CURRENT_YEAR) {
            params.delete('season');
        } else {
            params.set('season', String(year));
        }
        const search = params.toString();
        void goto(search ? `${$page.url.pathname}?${search}` : $page.url.pathname, {
            replaceState: false,
            keepFocus: true,
            noScroll: true,
        });
    }
</script>

<div class="season-picker" role="listbox" aria-label="Season selector">
    {#each YEARS as year}
        <button
            role="option"
            aria-selected={year === activeSeason}
            class:active={year === activeSeason}
            onclick={() => chooseSeason(year)}
        >
            {year}
            {#if year === CURRENT_YEAR}
                <span class="live-dot" aria-label="Live season"></span>
            {/if}
        </button>
    {/each}
</div>

<style>
    .season-picker {
        display: flex;
        gap: 0.25rem;
        overflow-x: auto;
        scrollbar-width: none;
    }
    .season-picker::-webkit-scrollbar { display: none; }

    button {
        flex: none;
        display: flex;
        align-items: center;
        gap: 0.3rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.04em;
        padding: 0.2rem 0.5rem;
        border-radius: 0.25rem;
        border: 1px solid color-mix(in oklab, var(--chrome-text) 18%, transparent);
        background: color-mix(in oklab, var(--chrome-bg) 60%, black);
        color: color-mix(in oklab, var(--chrome-text) 60%, transparent);
        cursor: pointer;
    }

    button.active {
        background: var(--mlb-blue);
        border-color: var(--mlb-blue);
        color: white;
    }

    .live-dot {
        display: inline-block;
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #22c55e;
        animation: pulse 1.8s ease-in-out infinite;
        flex-shrink: 0;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; transform: scale(1); }
        50%       { opacity: 0.5; transform: scale(0.8); }
    }
</style>
```

- [ ] **Step 2: Wire season into +page.ts load function**

In `apps/web/src/routes/+page.ts`, pass `season` to the API call:

```typescript
// In the load function, after resolving view/sort:
const season = url.searchParams.get('season');
if (season) params.set('season', season);

// In the return value, add:
return {
    boardView: payload.view,
    boardSort: payload.sort,
    boardStyle,
    boardSeason: payload.season ?? new Date().getFullYear(),
    entries: payload.entries,
    selectedPosition: resolvedView.selectedPosition,
};
```

Also update the `CachedBoard` type and cache key to include season:

```typescript
type CachedBoard = { entries: BoardEntryPayload[]; view: string; sort: string; season: number };
```

And update the cache key:
```typescript
const cacheKey = params.toString();
```
(params already contains season if set, so this is automatic.)

- [ ] **Step 3: Add SeasonPicker to +page.svelte**

In `apps/web/src/routes/+page.svelte`:

Import and render:
```svelte
import SeasonPicker from '$lib/components/board/SeasonPicker.svelte';
```

In the template, add inside `.top-bar` after `<StatPicker>`:
```svelte
<SeasonPicker />
```

Also update SSE to disable for past seasons. Find where `openBoardStream` is called and add a guard:

```typescript
const isCurrent = !$page.url.searchParams.get('season') ||
    parseInt($page.url.searchParams.get('season')!) === new Date().getFullYear();

// Only open SSE for the current season
if (!isCurrent) return;
const stop = openBoardStream(...);
```

- [ ] **Step 4: Rebuild and verify in browser**

```bash
docker compose up -d --build web
```

- Current year shows with a pulsing green dot
- Clicking a past year loads that year's data (or shows empty if not yet backfilled)
- SSE is not active on past seasons (no live updates)

- [ ] **Step 5: Commit**

```bash
git add apps/web/src/lib/components/board/SeasonPicker.svelte \
        apps/web/src/routes/+page.svelte \
        apps/web/src/routes/+page.ts
git commit -m "feat(web): season selector with LIVE indicator for current year"
```

---

## Running the backfill

After all tasks are deployed and the stack is running, execute the one-time historical backfill:

```bash
docker exec diamond-ingest python -m apps.ingest.app.backfill \
    --start-year 2016 --end-year 2025
```

Monitor output — each season takes ~5–10 s (2 s sleep + API fetch + DB writes). Full backfill ~2 minutes.

To re-run a specific year if it failed:
```bash
docker exec diamond-ingest python -m apps.ingest.app.backfill \
    --start-year 2022 --end-year 2022
```

---

---

## Task 12: Export DB for GCP Cloud SQL import

Run this **after the backfill completes** and the board is verified working locally. Cloud SQL uses PostgreSQL, so a standard `pg_dump` works directly.

- [ ] **Step 1: Dump the local database**

```bash
docker exec diamond-db pg_dump \
    -U diamond \
    -d diamond \
    --no-owner \
    --no-acl \
    -Fc \
    -f /tmp/diamond_departures_$(date +%Y%m%d).dump
```

`-Fc` produces a custom-format archive (smaller, supports parallel restore).

- [ ] **Step 2: Copy the dump out of the container**

```bash
docker cp diamond-db:/tmp/diamond_departures_$(date +%Y%m%d).dump ./diamond_departures_$(date +%Y%m%d).dump
```

- [ ] **Step 3: Verify the dump is intact**

```bash
pg_restore --list ./diamond_departures_$(date +%Y%m%d).dump | head -30
```

Expected: table of contents listing `players`, `teams`, `player_stats`, `leaderboard_views`, etc. with row counts.

- [ ] **Step 4: Upload to GCS (Cloud SQL import requires a GCS bucket)**

```bash
gsutil cp ./diamond_departures_$(date +%Y%m%d).dump gs://<your-bucket>/diamond_departures_$(date +%Y%m%d).dump
```

- [ ] **Step 5: Import into Cloud SQL**

```bash
gcloud sql import pg <INSTANCE_NAME> \
    gs://<your-bucket>/diamond_departures_$(date +%Y%m%d).dump \
    --database=diamond \
    --user=diamond
```

Or via the Cloud Console: Cloud SQL → Instance → Import → select the GCS file.

> **Note:** Cloud SQL's import user needs `cloudsql.instances.import` IAM permission. The service account running the import must also have `roles/storage.objectViewer` on the GCS bucket.

- [ ] **Step 6: Verify on Cloud SQL**

```bash
gcloud sql connect <INSTANCE_NAME> --user=diamond --database=diamond
# Then:
SELECT COUNT(*) FROM players;
SELECT COUNT(*) FROM player_stats;
SELECT COUNT(*) FROM leaderboard_views;
```

---

## Verification checklist

- [ ] `leaderboard_views` has `season` column: `\d leaderboard_views` shows it
- [ ] Current season data loads on the board with real player names
- [ ] Statcast tab shows xwOBA, xBA, barrel%, hard_hit%, exit_velocity columns
- [ ] Season selector shows 2016–current with pulsing dot on current year
- [ ] Selecting 2024 loads 2024 leaderboard data (after backfill)
- [ ] SSE is disabled when viewing a past season
- [ ] FPS badge stays green during normal board use
- [ ] `docker logs diamond-ingest` shows season refresh every 60s (live) or 60min (idle)
- [ ] Simulation loop is gone — no fake nudges in API logs
