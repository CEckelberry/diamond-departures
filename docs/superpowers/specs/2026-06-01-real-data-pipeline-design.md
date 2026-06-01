# Real Data Pipeline — Design Spec
**Date:** 2026-06-01  
**Scope:** Hitters only. Season-to-date stats for the current season + historical backfill (2016–2025). No pitchers, no WAR, no defense metrics in this phase.

---

## 1. Data Sources

### MLB Stats API (existing base URL)
Two endpoints, both public/free, same `MLBApiClient` used by the existing ingest service.

| Purpose | Endpoint |
|---|---|
| Season totals | `GET /api/v1/stats?stats=season&playerPool=qualified&group=hitting&gameType=R&season={year}&sportId=1` |
| Expected stats | `GET /api/v1/stats?stats=expectedStatistics&playerPool=qualified&group=hitting&gameType=R&season={year}&sportId=1` |

Season totals return: G, AB, PA, H, 2B, 3B, HR, R, RBI, BB, IBB, HBP, SO, SB, SF, AVG, OBP, SLG, OPS, plus player identity (id, fullName, currentTeam, primaryPosition).

Expected stats return: xBA, xSLG, xwOBA per player.

### Baseball Savant
Separate base URL. New `SavantClient` using the same retry/backoff pattern as `MLBApiClient`.

| Purpose | Endpoint |
|---|---|
| Statcast leaderboard | `GET https://baseballsavant.mlb.com/leaderboard/expected_statistics?type=batter&year={year}&min=q` |

Returns: barrel_batted_rate, hard_hit_percent, avg_hit_speed (exit velocity), plus xwOBA/xBA cross-check. Matched to MLB player IDs.

---

## 2. Stats Coverage

### Derived stats computed from MLB season totals
- **ISO** = SLG − AVG
- **BABIP** = (H − HR) / (AB − SO − HR + SF)
- **BB%** = BB / PA
- **K%** = SO / PA
- **wOBA** — weighted formula using season wOBA weights (existing `load_woba_weights` in `packages/stats/hitting.py`)
- **wRC+** — existing `wrc_plus()` function with park factors from `park_factors` table

### Stats stored per player per season

| Tab | Stats |
|---|---|
| Traditional | AVG, OBP, SLG, OPS, HR, RBI, SB |
| Sabermetric | wRC+, wOBA, ISO, BABIP, BB%, K% |
| Statcast | xwOBA, xBA, barrel_pct, hard_hit_pct, exit_velocity |

All stored as rows in `player_stats` with `stat_name` varchar(20). No schema changes to the `player_stats` table — it already supports arbitrary stat names with a `season` column.

---

## 3. Schema Changes

### Migration: add `season` to `leaderboard_views`

`leaderboard_views` currently has no season column. Add it and update the unique constraint so multiple seasons can coexist:

```sql
ALTER TABLE leaderboard_views ADD COLUMN season int NOT NULL DEFAULT 2026;
ALTER TABLE leaderboard_views DROP CONSTRAINT leaderboard_views_view_key_sort_stat_rank_key;
ALTER TABLE leaderboard_views ADD CONSTRAINT leaderboard_views_view_key_sort_stat_season_rank_key
    UNIQUE (view_key, sort_stat, season, rank);
CREATE INDEX idx_leaderboard_views_season ON leaderboard_views (view_key, sort_stat, season, rank);
```

### API VALID_SORTS additions

Add to `board.py`:
```python
"xBA", "barrel_pct", "hard_hit_pct", "exit_velocity"
```
(xwOBA already present.)

---

## 4. New Ingest Module: `season_stats.py`

Single class owns the full refresh cycle for one season.

```
SeasonStatsRefresher(mlb_client, savant_client, db_store, season)
  .refresh() → RefreshResult
    1. fetch_season_totals()          MLB API season endpoint
    2. fetch_expected_stats()         MLB API expectedStatistics endpoint
    3. fetch_savant_stats()           Baseball Savant leaderboard
    4. merge_and_derive(raw)          compute ISO, BABIP, BB%, K%, wOBA, wRC+
    5. upsert_players(players)        sync players table (name, team, pos, headshot_url)
    6. upsert_stats(stats, season)    close old valid_to, open new row in player_stats
    7. rebuild_leaderboards(season)   DELETE + INSERT leaderboard_views in one transaction
```

`rebuild_leaderboards` covers all combinations:
- view_keys: `hitters`, `hitters_ss`, `hitters_of` (the three currently in `VALID_VIEWS`; `hitters_1b`, `hitters_2b`, `hitters_3b`, `hitters_c`, `hitters_dh` are deferred — add to `VALID_VIEWS` if needed)
- sort_stats: all stats from the three tabs above

Runs inside a single DB transaction so the board never shows a partially-updated leaderboard.

### New `SavantClient`

Thin wrapper around `urllib` — same interface as `MLBApiClient`. Separate base URL (`https://baseballsavant.mlb.com`), same retry/backoff/timeout config pattern.

---

## 5. Runner Integration

Three new env vars in `IngestSettings`:

| Var | Default | Meaning |
|---|---|---|
| `SEASON_REFRESH_LIVE_SECONDS` | `60` | How often to refresh season stats when live games are active |
| `SEASON_REFRESH_IDLE_SECONDS` | `3600` | How often to refresh when no live games |
| `CURRENT_SEASON` | current calendar year | Which season to keep refreshing |

`run_loop` in `runner.py` tracks a `last_season_refresh` timestamp. On every iteration, after `run_once()`, it checks whether a season refresh is due and calls `SeasonStatsRefresher.refresh(year=CURRENT_SEASON)` if so.

Historical seasons are never refreshed by the runner — they are seeded once by the backfill script.

### Historical backfill script: `backfill.py`

One-time CLI script. Loops 2016 → current_season − 1. For each year, checks whether `player_stats` already has rows for that season; if not, calls `SeasonStatsRefresher.refresh(year=y)` then sleeps 2 seconds (polite to APIs).

```
python -m apps.ingest.app.backfill [--start-year 2016] [--end-year 2025] [--dry-run]
```

---

## 6. API Changes

### Remove simulation loop

The `simulation_loop`, `start_simulation`, and `@app.on_event("startup")` block at the bottom of `main.py` are deleted entirely.

### Add DB-change poller for SSE

Replaces the simulation loop. Runs as a background asyncio task on startup:

```
db_poll_loop (every SSE_POLL_SECONDS, default 30):
  for each (view, sort, season) with active SSE connections:
    rows = board_loader(view, sort, season)
    latest_refreshed_at = rows[0]['refreshed_at']
    if different from last_seen[(view, sort, season)]:
        hub.publish_snapshot(view, sort, entries)
        update last_seen
```

When ingest writes new `leaderboard_views` rows, the API detects the changed `refreshed_at` within 30 seconds and fires a snapshot to all connected clients.

`SSE_POLL_SECONDS` is a new env var, default 30.

Past-season SSE requests: the stream connects but the poller skips publishing updates for any season < `CURRENT_SEASON` (closed seasons never change).

### Board reader `season` param

`GET /api/board?view=hitters&sort=wRC+&season=2026`  
`GET /api/board/sse?view=hitters&sort=wRC+&season=2026`

`season` defaults to `CURRENT_SEASON` if omitted. The `postgres_board_reader` adds `AND lv.season = %s` to the query.

---

## 7. Web Changes

### Season selector

Compact selector in the top bar, years 2016 → current. Current year shows a pulsing `LIVE` dot. Selecting a year sets `?season=YYYY` in the URL. Past seasons disable SSE (no live updates) and hide the freshness indicator.

### Statcast tab

Third style tab alongside Traditional and Sabermetric. `StatPicker` updated with:

```
statcast → [xwOBA, xBA, barrel%, hard_hit%, exit_velocity]
```

URL param: `?style=statcast`

Stat formatting: xwOBA/xBA as 3-decimal (.000), barrel%/hard_hit% as percentage (00.0%), exit_velocity as float with one decimal (mph).

### No changes to

Board layout, Row structure, Cell animation, flap components — they animate whatever values come in.

---

## 8. What's Explicitly Out of Scope

- Pitchers, defense, WAR
- Statcast pitch-level data (spin rate, pitch mix, etc.)
- Player search / autocomplete
- Real-time per-pitch game updates (separate future phase — the live game feed scanner already exists for this)
- Auth, rate limiting, caching layer
