# Architecture

How the system is wired. The data rules in `DATA.md` are the constraints; this document is how those constraints translate into infrastructure.

---

## System diagram

```
                          ┌─────────────────────────────┐
                          │  diamond.ce.dev             │
                          │  (Cloud DNS + Cloud LB)     │
                          └──────────────┬──────────────┘
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  │                                             │
                  ▼                                             ▼
    ┌──────────────────────────┐               ┌──────────────────────────┐
    │  Frontend (Cloud Run)    │               │  API (Cloud Run)         │
    │  - SvelteKit             │   ── /api ──> │  - Python (FastAPI)      │
    │  - Split-flap board      │               │  - SSE channels          │
    │  - Player detail         │               │  - Leaderboard query     │
    │  - Stat picker           │               │  - Cache layer           │
    └──────────────────────────┘               └────────────┬─────────────┘
                                                            │
                                                            │
                                                            ▼
                                                ┌──────────────────────────┐
                                                │  Cloud SQL Postgres 18   │
                                                │  - players               │
                                                │  - player_stats (TS)     │
                                                │  - leaderboard_views     │
                                                │  - games, teams          │
                                                └─────────▲────────────────┘
                                                          │
                                                          │ writes
                                                          │
                       ┌──────────────────────────────────┴────────────────┐
                       │                                                    │
                       ▼                                                    ▼
        ┌──────────────────────────┐                       ┌──────────────────────────┐
        │  Ingest (Cloud Run job)  │  ── triggered by ──>  │  Cloud Scheduler         │
        │  - Python worker         │                       │  - 60s during games      │
        │  - Pulls MLB Stats API   │                       │  - 15min between         │
        │  - Computes derived      │                       │  - 1h off-game           │
        │  - Detects schema drift  │                       │  - 24h off-season        │
        └────────┬─────────────────┘                       └──────────────────────────┘
                 │
                 │ HTTPS
                 ▼
        ┌──────────────────────────┐
        │  MLB Stats API           │
        │  statsapi.mlb.com        │
        │  + Baseball Savant       │
        └──────────────────────────┘
```

---

## Components

### Frontend (Cloud Run)

A SvelteKit app, statically prerendered for the index/about pages, dynamically rendered for the live board. Connects to the API via SSE for real-time updates and via REST for initial loads, player detail, and historical queries.

Why Cloud Run: stateless, scales to zero (idle traffic on a niche site is fine), simple deploy. The split-flap animation runs entirely client-side once the data arrives.

### API (Cloud Run)

A Python FastAPI service. Two responsibilities:

1. **REST endpoints** for initial page load, player detail, historical queries
2. **SSE channels** for live updates — one channel per active leaderboard view (e.g., "hitters by wRC+" is one channel; "SS by OPS" is another)

When a visitor lands on the board, the frontend opens an SSE connection scoped to the view they're looking at. The API holds the connection open and pushes deltas as they happen. When the visitor switches views (e.g., from hitters-by-wRC+ to SS-by-OPS), the frontend closes the old SSE and opens a new one.

The API maintains an in-memory leaderboard cache keyed by `(view, sort_stat)`. On startup it loads the current state from Postgres; on each ingest cycle it re-reads and broadcasts deltas to subscribed clients.

Why Cloud Run for SSE: Cloud Run gen2 supports long-lived connections (up to 60 minutes per connection — we ping every 30s and reconnect on disconnect, plenty of room). The "scales to zero" model is fine here because when no visitors are connected, there's nothing to broadcast anyway.

### Ingest (Cloud Run job)

A Python worker service that runs to completion on each invocation. Triggered by Cloud Scheduler. Steps:

1. Determine season state (in-season / off-season / off-game day)
2. Fetch live games from MLB Stats API (`/api/v1/schedule?date=today`)
3. For each live game, fetch the latest box score and pitch-by-pitch deltas
4. For each player who appeared in a game, fetch their season stats and recompute derived stats (wRC+, FIP, etc.) using the shared `packages/stats/` library
5. Compute drift detection: hash schema, compare to last known
6. Write updates to Postgres in a transaction (with `valid_from`/`valid_to` for rollback support)
7. Trigger a "leaderboard refresh" message via Cloud Pub/Sub that the API service consumes
8. Exit

Why Cloud Run job (not always-on): the work is bursty. 60-second intervals during games is fine for a job; always-on would waste compute between intervals.

### Database (Cloud SQL)

Postgres 18, `db-custom-1-3840` (1 vCPU, 3.75GB). Private IP only, in the same VPC as the api and ingest services.

Schema details in the next section. Key design choices:

- `player_stats` is **append-only with versioning**. We never UPDATE a stat row; we INSERT a new row with the new value, and the old row gets `valid_to = NOW()`. This enables rollback of bad ingest runs and supports the "stat history" feature for player detail views.
- `leaderboard_views` is a **materialized cache table** of pre-sorted top-100 lists per (view × sort_stat). Re-computed on every ingest. Queries against this are fast (a single SELECT with ORDER BY id, since the table is already sorted).
- All stat values stored as `numeric(8, 3)` for stats with decimals, `int` for counting stats. We don't use `float` — small-fraction errors compound badly when you're sorting by 4th-decimal differences.

### Cloud Scheduler + Pub/Sub

Cloud Scheduler triggers the ingest job at the appropriate cadence (handled by the job's first action: it checks current season state and exits if it shouldn't run yet).

Pub/Sub carries "leaderboard refresh" messages from ingest to api. The api service holds a single subscription; on each message, it re-reads the relevant leaderboard view from Postgres and broadcasts the delta to subscribed SSE clients.

---

## Database schema

Five tables. All in a single Postgres database, single schema.

### `teams`

```sql
CREATE TABLE teams (
    id          int PRIMARY KEY,            -- MLB team ID
    abbr        varchar(3) NOT NULL UNIQUE,  -- e.g. "NYY"
    name        text NOT NULL,
    division    text NOT NULL,
    league      text NOT NULL,
    ballpark_id int
);
```

Static data, ~30 rows. Refreshed once a year when MLB publishes the new season.

### `players`

```sql
CREATE TABLE players (
    id              int PRIMARY KEY,           -- MLB player ID
    full_name       text NOT NULL,
    short_name      text NOT NULL,             -- "Judge, A."
    bats            char(1),                   -- L, R, S
    throws          char(1),
    primary_pos     varchar(3),                -- "OF", "SS", "SP"
    eligible_pos    varchar(3)[] DEFAULT '{}', -- {"SS", "2B"}
    team_id         int REFERENCES teams(id),
    is_active       bool NOT NULL DEFAULT true,
    is_qualified    bool NOT NULL DEFAULT false,
    last_seen_at    timestamptz NOT NULL,
    headshot_url    text
);
```

The active player pool. Refreshed daily and on roster transactions. ~750 active rows during the season.

### `player_stats`

```sql
CREATE TABLE player_stats (
    id          bigserial PRIMARY KEY,
    player_id   int NOT NULL REFERENCES players(id),
    stat_name   varchar(20) NOT NULL,           -- "wRC+", "FIP", "AVG"
    stat_value  numeric(8, 3) NOT NULL,
    valid_from  timestamptz NOT NULL,
    valid_to    timestamptz,                    -- NULL = currently valid
    source      varchar(40) NOT NULL,           -- "mlb-stats-api", "computed:wRC+"
    season      int NOT NULL,
    sample_size int                             -- e.g. PA for hitters, IP for pitchers
);

CREATE INDEX idx_player_stats_current ON player_stats (player_id, stat_name, season)
    WHERE valid_to IS NULL;

CREATE INDEX idx_player_stats_history ON player_stats (player_id, stat_name, valid_from);
```

Append-only. Each ingest writes new rows; old rows get `valid_to` set. The partial index on `valid_to IS NULL` keeps "current value" queries fast.

Expected size: ~750 players × 25 stats × ~10 changes per day = ~190K rows per day during the season. With 6-month retention before archival, we're looking at ~30M rows. Postgres handles this trivially with the right indexes.

### `leaderboard_views`

```sql
CREATE TABLE leaderboard_views (
    id              bigserial PRIMARY KEY,
    view_key        varchar(40) NOT NULL,       -- "hitters", "ss", "sp"
    sort_stat       varchar(20) NOT NULL,
    rank            int NOT NULL,
    player_id       int NOT NULL REFERENCES players(id),
    stat_value      numeric(8, 3) NOT NULL,
    refreshed_at    timestamptz NOT NULL,
    UNIQUE (view_key, sort_stat, rank)
);

CREATE INDEX idx_leaderboard_views_lookup ON leaderboard_views (view_key, sort_stat, rank);
```

Materialized cache. On each ingest, the rows for each (view × sort_stat) are recomputed: `DELETE FROM leaderboard_views WHERE view_key = $1 AND sort_stat = $2`, then `INSERT` the new top-100. The api service queries this table directly for the initial page load.

### `games`

```sql
CREATE TABLE games (
    id          int PRIMARY KEY,                -- MLB game ID
    home_team   int NOT NULL REFERENCES teams(id),
    away_team   int NOT NULL REFERENCES teams(id),
    scheduled   timestamptz NOT NULL,
    state       varchar(20) NOT NULL,           -- "scheduled", "live", "final", "postponed"
    season      int NOT NULL,
    final_score_home int,
    final_score_away int
);

CREATE INDEX idx_games_state ON games (state, scheduled DESC);
```

Used by ingest to know which games are live and need pitch-by-pitch ingestion, and by the api to determine "no games today" state.

### `ingest_runs`

```sql
CREATE TABLE ingest_runs (
    id              bigserial PRIMARY KEY,
    started_at      timestamptz NOT NULL,
    completed_at    timestamptz,
    status          varchar(20) NOT NULL,       -- "running", "success", "failed", "drift_detected"
    games_processed int,
    stats_updated   int,
    error_message   text,
    schema_hash     varchar(64)
);
```

Audit trail of every ingest invocation. Used for monitoring (alert if last successful run > 1h ago during the season) and for drift detection (compare schema_hash across runs).

---

## Data flow

### Live game ingest (60-second cycle)

```
Cloud Scheduler fires at 12:34:00
    ↓
Ingest job starts
    ↓
Read season state: in-season, games today
    ↓
Query games table: 4 games currently "live"
    ↓
For each live game:
  Fetch /game/{id}/feed/live  ← MLB Stats API
  Diff against last known state for this game
  Identify players whose stats changed
    ↓
For each changed player:
  Fetch /people/{id}/stats?group=hitting,pitching
  Recompute derived stats via packages/stats/
  Compare to current player_stats
  If changed: INSERT new player_stats row, UPDATE old to valid_to=now
    ↓
Recompute affected leaderboard_views:
  Identify which (view × sort_stat) combos contain changed players
  Re-query the leaderboard for those combos (Postgres ORDER BY)
  DELETE + INSERT in leaderboard_views
    ↓
Publish to Pub/Sub: {"affected_views": [...]}
    ↓
API service receives message
    ↓
API service queries refreshed leaderboard_views
    ↓
API service computes deltas vs in-memory cache
    ↓
API service broadcasts deltas to subscribed SSE clients
    ↓
Frontend receives delta, animates split-flap cells
```

End-to-end latency from game event to screen: 15-90 seconds (most of which is waiting for the next 60s ingest tick).

### Initial page load

```
Visitor lands on /
    ↓
Frontend SSR loads with the default view (hitters by wRC+)
    ↓
Frontend SSR fetches GET /api/board?view=hitters&sort=wRC+ from API
    ↓
API queries leaderboard_views (single SELECT, sub-millisecond)
    ↓
API returns top-100 with player metadata joined in
    ↓
Frontend renders the board (no animation; this is the initial state)
    ↓
Frontend opens SSE: GET /api/board/sse?view=hitters&sort=wRC+
    ↓
API holds connection open, sends heartbeat every 30s
    ↓
On any leaderboard refresh, API sends deltas via SSE
    ↓
Frontend animates the changes
```

### View switch (visitor changes the sort or position filter)

```
Visitor clicks "OPS" in the stat picker
    ↓
Frontend closes current SSE
    ↓
Frontend fetches GET /api/board?view=hitters&sort=OPS
    ↓
Frontend animates from current state to new state
    (every row that changed position, every cell that changed value)
    ↓
Frontend opens new SSE: GET /api/board/sse?view=hitters&sort=OPS
```

The "animate from current state to new state" is the moneyshot of the project — every cell flips visibly, rank changes cause row slides. This is purely client-side animation; the data was already on screen.

---

## API design

### REST endpoints

```
GET  /api/board?view={view}&sort={stat}
       Returns top-100 for the view. Includes player metadata.

GET  /api/board/sse?view={view}&sort={stat}
       Server-Sent Events stream. Initial event = full snapshot.
       Subsequent events = deltas.

GET  /api/players/{id}
       Player detail: full stat line, recent games, season trend.

GET  /api/players/{id}/history?stat={stat}
       Time-series of one stat across the season. For trend charts.

GET  /api/games?date={date}
       Games on a date. Used for the "no games today" state.

GET  /api/season-state
       Returns current mode: "live" | "between" | "off-game" | "off-season"

GET  /api/health
       Returns 200 if DB is reachable. Used by Cloud Run health check.

GET  /api/freshness
       Returns last successful ingest time + recent ingest run history.
       Visible on the site for debugging/transparency.
```

### SSE event format

```
event: snapshot
data: {"view":"hitters","sort":"wRC+","entries":[...100 entries...]}

event: delta
data: {"changes":[
  {"player_id":12345,"old_rank":3,"new_rank":1,"changed_stats":[
    {"name":"wRC+","old":172,"new":174}
  ]},
  ...
]}

event: heartbeat
data: {"ts":1730000000}
```

Heartbeat every 30s keeps the connection alive through proxies and lets the client detect stale connections.

---

## Caching strategy

Three layers:

### 1. In-memory cache (api service)

The api service holds a hot copy of every active leaderboard_views snapshot. Refreshed on Pub/Sub messages. SSE broadcasts read from this cache, not Postgres.

Memory footprint: ~50 views × 100 entries × ~500 bytes per entry = ~2.5MB. Trivial.

### 2. Postgres `leaderboard_views` table

Pre-computed top-100 per (view × sort_stat). Avoids running the full ranking query on every page load. Updated on every ingest tick.

### 3. CDN edge cache (Cloud CDN)

Static assets (fonts, JS bundles) cached at the edge. The board page itself is `Cache-Control: no-store` because the data is meant to be fresh; the SSE handles freshness.

Player detail pages cache for 60 seconds at the edge. Rapid clicking through players doesn't hammer the api.

---

## Deployment

### Container builds

Two Python service images:

- **api**: FastAPI + uvicorn image (~120-180MB depending on deps)
- **ingest**: Python worker image (~120-180MB depending on deps)

The frontend builds to a SvelteKit Node adapter, distroless nodejs, ~85MB.

### CI pipeline

GitHub Actions on push:

1. Build all three images in parallel
2. Run unit tests + the formula verification suite (the wRC+ test data, etc.)
3. Push to Artifact Registry
4. Run a smoke test against a staging Cloud Run revision: hit `/api/health`, `/api/season-state`, render the board
5. Deploy to production via blue-green Cloud Run revision split
6. Run a post-deploy ingest verification: trigger one ingest run, verify it completes successfully

### Cloud Scheduler

Three jobs:

- `ingest-frequent`: every 60s, weekday 12pm-12am ET (active baseball hours). Mostly Apr-Oct.
- `ingest-occasional`: every 15min, weekday 7am-12pm ET and 12am-2am ET
- `ingest-daily`: 4am UTC daily. Always runs.

The ingest job itself decides whether to do real work based on season state. If a 60s scheduler invocation finds it's the off-season, the job exits in <1 second.

---

## Cost model

Approximate monthly cost during the season (April-October):

| Resource | Monthly | Notes |
|---|---|---|
| Cloud SQL (db-custom-1-3840) | ~$35 | Always-on |
| Cloud Run (frontend + api + ingest) | ~$8 | Scales to zero outside game hours |
| Cloud Scheduler (3 jobs) | <$1 | Minimal |
| Cloud Pub/Sub | <$1 | Tiny message volume |
| Cloud CDN + LB + DNS | ~$15 | Required for custom domain |
| Cloud Logging + Monitoring | ~$3 | Mostly free tier |
| Egress | ~$2 | |
| Artifact Registry | ~$1 | |
| **Total in-season** | **~$65/month** | |

In off-season (November-March), Cloud Run usage drops further because the ingest runs only daily:

| Resource | Off-season | Notes |
|---|---|---|
| Cloud SQL | ~$35 | Same — DB stays up |
| Cloud Run | ~$2 | Mostly idle |
| Other | ~$15 | Same |
| **Total off-season** | **~$50/month** | |

**Wait — this is higher than the README target of $25-35/month.** That target was optimistic. Realistic is $50-65/month. Two paths to bring it down:

**Option A — accept ~$60/month.** Still cheaper than Bake-off, no methodology compromise. Recommended.

**Option B — drop Cloud SQL to Neon serverless Postgres.** Neon scales to zero compute and bills by usage. For our load pattern (intense for 60 seconds, idle for 60 seconds), Neon could cost $5-10/month. The downside: Neon is in AWS, so we'd add cross-cloud network latency (~30-50ms) on every DB query from Cloud Run. For a leaderboard view that's already 60-second-stale, that latency doesn't matter — but it's an architecture wrinkle. **Skip this at v1; consider for v2 if cost matters more than architectural cleanliness.**

**Option C — pause Cloud SQL during off-season.** Cloud SQL supports `gcloud sql instances patch --activation-policy=NEVER` which stops the instance and bills only storage (~$2/month). Resume in March. Saves ~$35/month × 5 months = ~$175/year. Worth it. The case study can mention this seasonal cost optimization as a deliberate choice.

**Hard cap: $50/month.** Same auto-pause mechanism as Bake-off. If the bill projects over $50, the api goes into a degraded mode that serves cached snapshots only and the ingest job is suspended.

---

## Local development

A `docker-compose.yml` brings up:
- Postgres 18
- A "MLB API mock" — a small Python FastAPI service that returns canned responses for a recent week of games. Lets us develop offline.
- The api service
- The ingest service (configured to point at the mock)
- The frontend (in dev mode)

`make dev` brings everything up. `make seed` runs a seed ingest against the mock to populate the DB. `make replay` runs the mock through a recent week of game data at accelerated speed (5min real = 1 day game).

---

## Failure modes

### MLB Stats API is down

Ingest runs fail. The DB still has the last known state. The frontend shows: "Live updates paused — checking back in [N seconds]". Once the API recovers, the next ingest catches up automatically.

### Schema drift detected

Ingest run completes if it can; logs the drift. Alert fires. Manual review required. The site continues serving stale-but-correct data until the drift is resolved.

### A bad ingest writes wrong values

The append-only `player_stats` table makes rollback possible: mark all rows from the bad run with `valid_to = bad_run.completed_at` and update the previous rows' `valid_to` back to NULL. Manual at v1.

### SSE connection drops

The frontend reconnects automatically with exponential backoff (1s, 2s, 4s, 8s, max 30s). On reconnect, it re-fetches the full snapshot to catch up on any deltas missed during the disconnect.

### Postgres becomes unresponsive

`/api/health` fails, the load balancer routes traffic away from any unhealthy api instance. New revisions can't start. Site degrades gracefully — the last cached snapshot in browser memory keeps showing, just doesn't update.

### Cost cap reached

Auto-pause kicks in. Site shows "Hit my monthly budget — back next month." Not a great look but honest. Resets on the 1st.
