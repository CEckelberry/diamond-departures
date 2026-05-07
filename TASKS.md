# Tasks

Phased build plan for Diamond Departures. Same shape as the portfolio's and Bake-off's TASKS.md — self-contained tasks with goal, inputs, outputs, and acceptance criteria. Hand them to Claude Code one at a time.

**Reference docs.** Pin `README.md`, `DATA.md`, `ARCHITECTURE.md`, and `STATS.md` for any task that touches the backend or pipeline. Pin `DESIGN.md` for any frontend task.

**Critical rule.** Every stat the system displays must trace back to either MLB Stats API raw data or a formula in `STATS.md`. If a task is producing a stat with no source, stop and update STATS.md first.

**Estimated build time.** ~10 weeks of evening-and-weekend work. The split-flap component alone is probably 1-1.5 weeks of careful frontend work — don't underestimate it. The data pipeline is another 2-3 weeks. The remaining 5-6 weeks cover everything else.

**Timing recommendation.** Aim to finish Phase 4 (the live board working with real data) before mid-September, so you have at least 4-6 weeks of regular-season visibility before the playoffs. If you're going to slip past September, plan to launch with preview-mode prominently featured and re-launch in March when the next season opens.

## 2026 stack update (authoritative)

Backend implementation standard for this project is now:

- **API**: Python **FastAPI**
- **Ingest**: Python worker/job (Cloud Run job)
- **Frontend**: SvelteKit

When older task bullets mention Go/chi/pgx file paths, map them to Python/FastAPI equivalents:

- `apps/api/cmd/server/main.go` -> `apps/api/app/main.py`
- `apps/api/internal/...` -> `apps/api/app/...`
- `apps/ingest/cmd/job/main.go` -> `apps/ingest/app/job.py`
- `apps/ingest/internal/...` -> `apps/ingest/app/...`
- `go test ...` -> `pytest ...`

Use this stack update over any conflicting wording below.

---

## Phase overview

- **Phase 0 — Foundation** (1 week): repo, Postgres schema, MLB API mock, design tokens
- **Phase 1 — Data pipeline** (2-3 weeks): ingest service, stats library, drift detection
- **Phase 2 — API + SSE** (1-1.5 weeks): the FastAPI backend, leaderboard cache, SSE broadcast
- **Phase 3 — Split-flap component** (1-1.5 weeks): the heart of the project, deserves its own phase
- **Phase 4 — The board (frontend v0)** (1.5 weeks): hero board with live data flowing
- **Phase 5 — Player detail + position filtering** (1 week): the side panel, position views
- **Phase 6 — Off-season + preview mode** (1 week): season-state handling, replay
- **Phase 7 — Polish + case study** (1 week): perf, accessibility, sound, write the case study, deploy
- **Phase 8 — v2 stretch** (open): more stats, multi-position eligibility, mobile refinement

---

# Phase 0 — Foundation

Goal: a working monorepo with the database schema in place, a mock MLB API for offline development, and the SvelteKit frontend bootstrapped with the Diamond design tokens.

- [ ] Task 0.1 — Monorepo scaffold
- [ ] Task 0.2 — Database schema + migrations
- [ ] Task 0.3 — MLB API mock
- [ ] Task 0.4 — Local dev compose
- [ ] Task 0.5 — CI scaffold
- [ ] Task 0.6 — SvelteKit project + design tokens

---

## Task 0.1 — Monorepo scaffold

**Goal.** Create the repository structure described in `README.md`.

**Outputs.**

- `pnpm-workspace.yaml`, root `package.json`, `Makefile` stubs
- `.gitignore`, `.editorconfig`, MIT `LICENSE`
- Empty directory tree per `README.md`'s layout
- All five reference docs (`README.md`, `DATA.md`, `ARCHITECTURE.md`, `DESIGN.md`, `STATS.md`) at the repo root

**Acceptance criteria.**

- `pnpm install` runs cleanly at the root
- `make dev` exists (prints "not yet implemented" is fine)
- The required directory tree entries from `README.md` are present (additional operational directories are allowed)

---

## Task 0.2 — Database schema + migrations

**Goal.** All five tables (`teams`, `players`, `player_stats`, `leaderboard_views`, `games`, `ingest_runs`) created via `golang-migrate` against Postgres 18.

**Inputs.** `ARCHITECTURE.md` (the Database schema section)

**Outputs.**

- `apps/api/migrations/001_init.up.sql` + `001_init.down.sql` — core tables and rollback
- `apps/api/migrations/002_seed_teams.up.sql` + `002_seed_teams.down.sql` — 30 MLB teams seed and rollback
- `apps/api/migrations/003_park_factors.up.sql` + `003_park_factors.down.sql` — current-season park factors (manually refreshed annually)
- `packages/content/teams.json` — canonical team data (id, name, abbr, division, league)
- `packages/content/park-factors-2026.json` — placeholder for the current year
- A `make migrate` Makefile target that runs `migrate up` against `$DATABASE_URL`

**Acceptance criteria.**

- `make migrate` against a fresh Postgres 18 creates all tables
- `\d+ players` shows all columns with the right types
- `SELECT count(*) FROM teams` returns 30
- `migrate down` succeeds and removes all tables cleanly
- All numeric stat columns are `numeric(8, 3)`, never `float`

---

## Task 0.3 — MLB API mock

**Goal.** A Python FastAPI service that mimics the MLB Stats API endpoints we use, returning canned responses for a recent week of games. Lets us develop offline.

**Inputs.** `DATA.md` (the stat sources section), real MLB Stats API documentation at `statsapi.mlb.com`

**Outputs.**

- `apps/mlb-mock/app/main.py`
- `apps/mlb-mock/internal/data/` — JSON fixtures for:
  - `/api/v1/schedule?date=*` (week of games)
  - `/api/v1/game/{id}/feed/live` (full game feed for ~10 games)
  - `/api/v1/people/{id}/stats?group=hitting,pitching` (~50 representative players)
  - `/api/v1/teams/{id}/roster` (active rosters)
- A `--replay-speed` flag that lets the mock cycle through "today's" games at variable speed (e.g., `--replay-speed=300x` runs an hour of games per real second, useful for accelerated dev)
- `apps/mlb-mock/Dockerfile`

**Acceptance criteria.**

- `curl localhost:8090/api/v1/schedule?date=today` returns realistic JSON matching the real API's shape
- The fixtures cover at least 5 live games, 100 games total in the week
- Response shapes match real API responses (validate against schemas captured from real API)
- Replay speed flag works: at `300x`, the same game completes in ~24 seconds instead of 3 hours

---

## Task 0.4 — Local dev compose

**Goal.** A `docker-compose.yml` that brings up Postgres 18, the MLB mock, and placeholder api/ingest/frontend services so the rest of the monorepo can develop against a realistic local environment.

**Outputs.**

- `docker-compose.yml` with services: `db` (postgres:18-alpine), `mlb-mock`, `api` (placeholder), `ingest` (placeholder), `web` (SvelteKit dev mode)
- A `db-init` one-shot job that runs migrations
- Volumes for Postgres data
- A `make dev` Makefile target

**Acceptance criteria.**

- `make dev` brings everything up cleanly
- Postgres is reachable at localhost:5432
- MLB mock is reachable at localhost:8090 and serves the fixtures
- Frontend (placeholder) is reachable at localhost:5173
- `make dev-clean` removes everything including volumes

---

## Task 0.5 — CI scaffold

**Goal.** GitHub Actions workflow that runs on every push: lint, test, build images, conditional deploy on push-to-main.

**Outputs.**

- `.github/workflows/ci.yml` with paths-filter to detect changed apps
- Jobs for each app: lint, test, build container
- Skipped deploy stage at this point (filled in during Phase 7)
- `.github/workflows/README.md` documenting expected secrets

**Acceptance criteria.**

- A push triggers all relevant jobs based on which paths changed
- The workflow file passes `actionlint`
- A test failure in any app fails the workflow

---

## Task 0.6 — SvelteKit project + design tokens

**Goal.** SvelteKit app initialized with Tailwind v4, Diamond design tokens (including the split-flap colors), and all three font families loaded.

**Inputs.** `DESIGN.md`, the portfolio's `DESIGN.md` for inherited tokens

**Outputs.**

- `apps/web/` initialized via `pnpm create svelte@latest`
- Tailwind v4 installed
- `apps/web/src/app.css` with full token system, including the Diamond-specific tokens (`--board-bg`, `--cell-bg`, `--cell-text`, etc.)
- Three font families loaded via `@fontsource/*`
- A placeholder home page that renders a single split-flap-styled cell to verify tokens work

**Acceptance criteria.**

- `pnpm --filter web dev` works, page loads
- The placeholder cell renders amber-on-deep-purple correctly
- All three font families load (verify in network tab)
- Dark/light mode toggle works (cotton candy palette in light mode adjusts surrounding chrome but the board stays dark)

---

# Phase 1 — Data pipeline

Goal: the ingest service can pull from the MLB mock, compute derived stats correctly, and write to Postgres. The stat library has verified implementations of every stat in `STATS.md`. Drift detection works.

This is the most algorithmically careful phase. Don't rush it.

- [ ] Task 1.1 — Stats library: hitting stats
- [ ] Task 1.2 — Stats library: pitching stats
- [ ] Task 1.3 — Stats library: defensive stats
- [ ] Task 1.4 — Stats library: verification suite
- [ ] Task 1.5 — Ingest skeleton + MLB client
- [ ] Task 1.6 — Ingest: schedule + game feed processing
- [ ] Task 1.7 — Ingest: player stat updates + derived stats
- [ ] Task 1.8 — Ingest: leaderboard view materialization
- [ ] Task 1.9 — Schema drift detection
- [ ] Task 1.10 — Position taxonomy + qualification rules

---

## Task 1.1 — Stats library: hitting stats

**Goal.** A Python package `packages/stats/hitting/` implementing every hitting stat in `STATS.md`, with unit tests.

**Inputs.** `STATS.md` (every hitting stat entry)

**Outputs.**

- `packages/stats/go.mod`
- `packages/stats/hitting/basic.go` — AVG, OBP, SLG, OPS, ISO, BABIP
- `packages/stats/hitting/woba.go` — wOBA with year-keyed weights
- `packages/stats/hitting/wrc.go` — wRC+
- `packages/stats/hitting/woba_weights_2026.json` — current-year weights
- `packages/stats/hitting/*_test.go` — table-driven tests for each stat with hand-verified values
- A `LeagueContext` struct that holds league-average stats + park factors, passed to wRC+ and similar adjusted stats

**Acceptance criteria.**

- All hitting stats compute correctly for a curated set of 20 player-seasons (verified against FanGraphs)
- `go test ./packages/stats/hitting` passes
- Coverage above 90% on the stat functions
- Each stat function has a doc comment explaining the formula and citing the source

---

## Task 1.2 — Stats library: pitching stats

**Goal.** Same as 1.1 but for pitching stats.

**Inputs.** `STATS.md` (every pitching stat entry)

**Outputs.**

- `packages/stats/pitching/basic.go` — ERA, WHIP, K/9, BB/9, K-BB%
- `packages/stats/pitching/fip.go` — FIP, xFIP, with cFIP constants
- `packages/stats/pitching/siera.go` — SIERA
- `packages/stats/pitching/era_plus.go` — ERA+
- `packages/stats/pitching/cfip_2026.json` — annual league constants
- `packages/stats/pitching/*_test.go` — verified against ~20 pitcher-seasons

**Acceptance criteria.**

- All pitching stats compute correctly for the curated set
- `go test ./packages/stats/pitching` passes
- The cFIP constant is correctly applied so league-average FIP equals league-average ERA

---

## Task 1.3 — Stats library: defensive stats

**Goal.** Defensive stat handling. Less computation needed (DRS and UZR come pre-computed from sources); more about parsing and storing.

**Inputs.** `STATS.md` (the Defensive stats section)

**Outputs.**

- `packages/stats/defensive/parsers.go` — extracts DRS, UZR, UZR/150, OAA from MLB Stats API and Statcast responses
- `packages/stats/defensive/qualification.go` — handles the "noisy" tag for sub-1000-inning samples
- Tests against a fixture set

**Acceptance criteria.**

- DRS values extracted correctly from sample API responses
- UZR/150 normalized correctly (some sources give per-game; we want per-150)
- The "noisy" tag is correctly applied to small samples

---

## Task 1.4 — Stats library: verification suite

**Goal.** A test harness that compares the library's computations to known-good values from FanGraphs and Baseball Reference, surfacing discrepancies clearly.

**Outputs.**

- `packages/stats/verify/data.json` — 50 hand-curated player-seasons with stats from FanGraphs (manually copied as ground truth)
- `packages/stats/verify/verify_test.go` — runs every stat function against every entry, reports diffs > 0.5%
- A CI job that runs the verification on every push

**Acceptance criteria.**

- The full verification passes (every computed stat within 0.5% of the source)
- A test failure clearly identifies which player, which stat, expected vs actual
- The verification dataset is documented (where each player's data came from, when captured)

---

## Task 1.5 — Ingest skeleton + MLB client

**Goal.** The ingest service's basic structure: non-HTTP CLI/job, env config, structured logging, MLB Stats API client wrapper.

**Inputs.** `ARCHITECTURE.md` (the Ingest section)

**Outputs.**

- `apps/ingest/cmd/job/main.go` — entrypoint, runs once and exits
- `apps/ingest/internal/config/config.go` — env vars (`MLB_API_URL`, `DATABASE_URL`, `LOG_LEVEL`, etc.)
- `apps/ingest/internal/mlb/client.go` — wrapper around `net/http` for MLB Stats API
- `apps/ingest/internal/store/postgres.go` — pgxpool init
- `apps/ingest/Dockerfile`

**Acceptance criteria.**

- `cd apps/ingest && go run ./cmd/job` exits cleanly with the mock running locally
- Logs are JSON when `ENVIRONMENT=production`, plain text otherwise
- MLB client correctly handles rate limits (sleeps and retries on 429)
- Container size under 30MB

---

## Task 1.6 — Ingest: schedule + game feed processing

**Goal.** The ingest job can read today's MLB schedule, identify live games, fetch each live game's feed, and identify which players had stat-changing events.

**Outputs.**

- `apps/ingest/internal/schedule/schedule.go` — fetches and processes the daily schedule
- `apps/ingest/internal/games/processor.go` — for each live game, fetches the feed and identifies player events
- `apps/ingest/internal/state/diff.go` — compares current game state to last seen, identifies players with changes
- Integration tests against the mock

**Acceptance criteria.**

- Running the ingest against the mock identifies live games correctly
- For a game where the mock has 5 stat-changing events, the diff produces exactly 5 player records to update
- Idempotency: running the ingest twice in a row produces no new updates the second time (because nothing changed)

---

## Task 1.7 — Ingest: player stat updates + derived stats

**Goal.** For each player flagged as needing an update, fetch their season stats, compute derived stats via `packages/stats/`, and write to Postgres using the append-only `valid_from`/`valid_to` pattern.

**Outputs.**

- `apps/ingest/internal/players/updater.go` — orchestrates per-player updates
- `apps/ingest/internal/store/player_stats.go` — append-only writer
- A method that for each (player_id, stat_name) pair: checks if the new value differs from the current `valid_to IS NULL` row; if so, updates the old row's `valid_to` and inserts a new row

**Acceptance criteria.**

- After ingesting a single game, the affected players have new rows in `player_stats`
- The old rows have `valid_to` set correctly
- A query for `SELECT stat_value FROM player_stats WHERE player_id=X AND stat_name='wRC+' AND valid_to IS NULL` returns exactly one row
- Stats that didn't change don't get new rows (verify by counting before/after with no changes)

---

## Task 1.8 — Ingest: leaderboard view materialization

**Goal.** After updating player stats, the ingest service recomputes any affected `leaderboard_views` rows.

**Outputs.**

- `apps/ingest/internal/leaderboards/recompute.go`
- For each (view_key × sort_stat) combo that contains an updated player, re-query the top-100 from `player_stats` (joined with `players` for filters), then DELETE + INSERT the new rows in `leaderboard_views`
- A small "what views are affected" function that maps player IDs to potentially-affected views

**Acceptance criteria.**

- A player whose wRC+ improved enough to enter the top-100 appears in `leaderboard_views WHERE view_key='hitters' AND sort_stat='wRC+'` after the next ingest
- The full top-100 is correctly ordered (verified by querying directly)
- Each (view × sort) combo has exactly 100 rows after recomputation
- Position filtering works (the SS view contains only SS-eligible players)

---

## Task 1.9 — Schema drift detection

**Goal.** The ingest service hashes the shape of every MLB API response it parses, compares to the last known hash, and logs/alerts on drift.

**Inputs.** `DATA.md` (the Schema drift section)

**Outputs.**

- `apps/ingest/internal/drift/hasher.go` — recursive JSON-shape hasher (keys at every level)
- `apps/ingest/internal/drift/detector.go` — compares hashes against last-known, stored in a `drift_signatures` table
- New migration: `004_drift_signatures.sql`
- Logs at WARN level on any drift detected; logs at ERROR if drift caused a parse failure

**Acceptance criteria.**

- Adding a new top-level key to a mock response produces a drift log entry
- Removing a key the ingest depends on produces an ERROR log
- The signature is stable across runs when the schema doesn't change
- Manually running `gcloud logging read` shows the drift entries cleanly

---

## Task 1.10 — Position taxonomy + qualification rules

**Goal.** The ingest service correctly classifies each player by primary position, computes their position-eligibility list, and flags qualification status.

**Inputs.** `DATA.md` (the Position taxonomy section), `STATS.md` (the qualification thresholds)

**Outputs.**

- `apps/ingest/internal/positions/classify.go`
- Logic from DATA.md: primary position = most games played; eligibility = positions with ≥5 games; SP vs RP based on % of starts
- Updates the `players.primary_pos`, `players.eligible_pos`, and `players.is_qualified` fields
- A `(just qualified)` flag stored as a timestamp so the API can tell whether a player crossed the line in the last 24h

**Acceptance criteria.**

- Manual test cases: a player with 80 games at 2B and 25 at SS gets `primary_pos='2B'` and `eligible_pos=['2B','SS']`
- A reliever with 60 IP across 25 appearances is `is_qualified=true` and classified `RP`
- A starter with 70 IP is `is_qualified=false` (below the 80 IP threshold) but still has `primary_pos='SP'`
- The `just_qualified_at` timestamp is set correctly when a player first qualifies

---

# Phase 2 — API + SSE

Goal: the FastAPI service serves leaderboard data via REST and pushes live updates via SSE. The frontend can render initial state from REST and animate updates from SSE.

- [ ] Task 2.1 — API skeleton
- [ ] Task 2.2 — Leaderboard REST endpoints
- [ ] Task 2.3 — In-memory leaderboard cache
- [ ] Task 2.4 — Pub/Sub subscriber for ingest notifications
- [ ] Task 2.5 — SSE endpoint
- [ ] Task 2.6 — Player detail endpoints
- [ ] Task 2.7 — Season-state and freshness endpoints

---

## Task 2.1 — API skeleton

**Goal.** Standard FastAPI service with structured logging, env config, and health endpoint.

**Outputs.**

- `apps/api/cmd/server/main.go`
- `apps/api/internal/config/`, `internal/http/`, `internal/store/`, `internal/observability/`
- A health endpoint that checks DB reachability
- `apps/api/Dockerfile` (distroless static, ~25MB)

**Acceptance criteria.**

- Service starts, binds to PORT, serves /api/health
- Graceful shutdown on SIGINT
- Container size under 30MB
- `go vet` and `go test` pass

---

## Task 2.2 — Leaderboard REST endpoints

**Goal.** `GET /api/board?view=...&sort=...` returns the top-100 with player metadata joined in.

**Outputs.**

- `apps/api/internal/http/handlers/board.go` — handler implementation
- `apps/api/internal/store/board.go` — query against `leaderboard_views` joined with `players` and `teams`
- Response schema: array of entries, each with rank, player (id, name, team_abbr, headshot_url, position), stat_value, freshness signature

**Acceptance criteria.**

- `curl /api/board?view=hitters&sort=wRC+` returns 100 entries with full player metadata
- Response time under 50ms (it's a single SELECT against a sorted table)
- Invalid `view` or `sort` returns 400 with a clear error
- Each entry includes a freshness field with timestamp + age category (live/recent/stale/old)

---

## Task 2.3 — In-memory leaderboard cache

**Goal.** The API service holds a cached copy of every active leaderboard view in memory, refreshed on Pub/Sub notifications. SSE broadcasts read from this cache.

**Outputs.**

- `apps/api/internal/cache/leaderboards.go`
- `sync.RWMutex`-protected map keyed by (view × sort_stat)
- Cache loaded on startup from `leaderboard_views`
- Cache invalidation hook that re-reads from Postgres on demand

**Acceptance criteria.**

- Cache is populated on startup; verify by triggering REST endpoint and confirming sub-millisecond response
- Manual cache invalidation produces a fresh read
- Concurrent reads don't block each other (RWMutex)
- Memory footprint under 5MB at full population

---

## Task 2.4 — Pub/Sub subscriber for ingest notifications

**Goal.** The API service subscribes to a Pub/Sub topic. When ingest publishes a message, the API service refreshes the affected views.

**Outputs.**

- `apps/api/internal/pubsub/subscriber.go`
- Background goroutine that reads from Pub/Sub and triggers cache invalidation
- Handles dead-letter, retries, message acknowledgment correctly

**Acceptance criteria.**

- Manually publishing a Pub/Sub message refreshes the matching cache entries
- Service restarts gracefully (in-flight messages handled correctly)
- Logs are clear about which views were refreshed and why

---

## Task 2.5 — SSE endpoint

**Goal.** `GET /api/board/sse?view=...&sort=...` opens a long-lived SSE connection that pushes deltas to the client.

**Inputs.** `ARCHITECTURE.md` (the SSE event format section)

**Outputs.**

- `apps/api/internal/http/handlers/sse.go`
- Connection management: track all open connections by (view × sort_stat) for efficient broadcast
- Broadcast logic: when cache for a view refreshes, compute delta and send to all subscribers
- Heartbeat every 30s
- Initial event sends the full snapshot
- Graceful close on client disconnect or request context cancellation

**Acceptance criteria.**

- Opening an SSE connection sends the initial snapshot within 100ms
- Triggering a cache refresh sends a delta event to all open connections within 100ms
- Heartbeat events arrive every 30s
- Closing the connection client-side cleans up server-side resources (verified by checking goroutine count)
- 100 concurrent connections work without resource exhaustion

---

## Task 2.6 — Player detail endpoints

**Goal.** `GET /api/players/{id}` returns full player detail; `GET /api/players/{id}/history?stat=...` returns time-series for one stat.

**Outputs.**

- `apps/api/internal/http/handlers/players.go`
- Player detail: full stat line across all stats, recent games, season totals
- History: time-ordered `player_stats` rows for the given stat across the season

**Acceptance criteria.**

- Player detail returns within 100ms
- History returns ~50-200 data points per player-stat for a full season, time-ordered
- Invalid player ID returns 404

---

## Task 2.7 — Season-state and freshness endpoints

**Goal.** Two transparency endpoints used by the frontend.

**Outputs.**

- `GET /api/season-state` — returns `{"mode": "live"|"between"|"off-game"|"off-season", "next_game_at": "...", "current_season": 2026}`
- `GET /api/freshness` — returns the last 10 ingest_runs, current schema-drift status, per-stat freshness summary

**Acceptance criteria.**

- Season state correctly identifies all four modes (test by manipulating `games` table fixtures)
- Freshness endpoint returns within 50ms
- Both endpoints have appropriate cache headers (season-state cached 5 min; freshness no-store)

---

# Phase 3 — Split-flap component

Goal: a production-quality split-flap component. This is the heart of the project. Don't ship until it feels right.

- [ ] Task 3.1 — Single-cell flap component (visual only)
- [ ] Task 3.2 — Single-cell flap animation
- [ ] Task 3.3 — Multi-character flap word component
- [ ] Task 3.4 — Sound integration
- [ ] Task 3.5 — Component test page

---

## Task 3.1 — Single-cell flap component (visual only)

**Goal.** A static Svelte component that renders a single cell in the split-flap style. No animation yet — just the visual.

**Inputs.** `DESIGN.md` (the Anatomy of a flap section)

**Outputs.**

- `apps/web/src/lib/components/flap/Cell.svelte`
- Props: `value: string` (single character), `width?: number` (default 28), `height?: number` (default 36)
- Renders top half + hairline + bottom half with the amber-on-deep-purple styling
- Uses CSS variables from `app.css` so dark/light mode adjustments work

**Acceptance criteria.**

- A Storybook (or simple test page) renders 10 cells with different characters cleanly
- The hairline is exactly 1px and visible
- Cell sizes are consistent
- The character is centered horizontally and vertically (test with "8", "M", and "I" — narrow chars often look off)

---

## Task 3.2 — Single-cell flap animation

**Goal.** When the cell's `value` prop changes, animate the three-phase flip described in DESIGN.md.

**Outputs.**

- `apps/web/src/lib/components/flap/Cell.svelte` updated to detect prop changes and run the animation
- Three CSS keyframes (top-down, pause, bottom-down) totaling 450ms
- Uses `view-transition` API where supported, falls back to manual CSS animation
- Honors `prefers-reduced-motion: reduce` (instant change with brief background flash)

**Acceptance criteria.**

- Changing `value` from "8" to "5" runs the full 450ms animation
- Multiple rapid changes (a → b → c) queue correctly without breaking
- The animation is smooth at 60fps (verify in devtools Performance tab)
- With reduced-motion, the cell snaps to the new value with a 200ms background flash
- The animation looks identical in Chrome, Firefox, and Safari (the touchiest cross-browser bit of this project)

---

## Task 3.3 — Multi-character flap word component

**Goal.** A component that renders a string as multiple flap cells, with intelligent diffing so only the cells that need to change actually flip.

**Outputs.**

- `apps/web/src/lib/components/flap/Word.svelte`
- Props: `value: string`, `width: number` (number of cells, default = max length expected)
- Right-aligns numbers (so "98" → "172" flips on the leading cell smoothly), left-aligns text
- Diffing: when `value` changes, only the cells whose character differs animate

**Acceptance criteria.**

- Rendering "Judge, A." in a 12-character word looks identical to a static label
- Changing "98" to "172" flips only the cells that differ
- Right-alignment for numbers is correct (no flipping on the trailing space)
- The word as a whole stays at fixed width (no layout shift on length change)

---

## Task 3.4 — Sound integration

**Goal.** The flap animation triggers the appropriate sound effect when sound is enabled.

**Inputs.** `DESIGN.md` (the Sound section)

**Outputs.**

- `apps/web/src/lib/audio/flap.ts` — sound manager with debouncing
- Three audio files in `apps/web/static/audio/`: `flap-single.mp3`, `flap-many.mp3`, `flap-row-shift.mp3`
- A Svelte store `apps/web/src/lib/stores/sound.ts` for sound on/off state, persisted to localStorage
- Cell.svelte calls into the sound manager on each animation; manager debounces to play `flap-many` instead of multiple `flap-single` sounds

**Acceptance criteria.**

- A single cell flip plays one `flap-single` sound when sound is on
- 30 cells flipping within 100ms plays one `flap-many` sound, not 30 individual sounds
- Sound is off by default
- Toggling sound persists across reloads
- No sound at all when reduced-motion is on (the flap animation skips, so the sound should too)
- Volume default is 30%

---

## Task 3.5 — Component test page

**Goal.** A standalone test page (not the main board) where the flap components can be exercised in isolation. Useful for tuning the animation.

**Outputs.**

- `apps/web/src/routes/test/flap/+page.svelte` — a page with controls to trigger flips, sound, and stress scenarios
- Buttons: flip a single cell to a random value; flip a word; flip 30 cells simultaneously; play row-shift sound
- A "scenarios" section that runs predefined test sequences

**Acceptance criteria.**

- Visiting `/test/flap` renders the test page
- Each button works
- The page is removed from production builds (or behind a flag)

---

# Phase 4 — The board

Goal: the main `/` page renders the live leaderboard with the split-flap mechanic working against real (mock) data.

- [ ] Task 4.1 — Layout shell
- [ ] Task 4.2 — Header + status bar
- [ ] Task 4.3 — View tabs + stat picker
- [ ] Task 4.4 — Board structure (rank, rows, cells)
- [ ] Task 4.5 — Initial load via REST
- [ ] Task 4.6 — SSE wiring + delta application
- [ ] Task 4.7 — Row reshuffle animation

---

## Task 4.1 — Layout shell

**Goal.** The `+layout.svelte` for the main app: nav, footer, room for the board.

**Outputs.**

- `apps/web/src/routes/+layout.svelte`
- `apps/web/src/lib/components/shell/Nav.svelte` — back-to-portfolio, GitHub, case-study links
- `apps/web/src/lib/components/shell/Footer.svelte` — methodology link, GitHub, about

**Acceptance criteria.**

- Nav and footer render on every page
- Nav is fixed-position at the top, footer is below content
- The layout works at every viewport from 320px to 1920px

---

## Task 4.2 — Header + status bar

**Goal.** The header above the board: title, status pills, sound toggle.

**Inputs.** `DESIGN.md` (the Header status bar component)

**Outputs.**

- `apps/web/src/lib/components/board/Header.svelte`
- Subscribes to season-state and freshness endpoints
- Renders the mode pill (live/between/off-game/off-season), game count, freshness summary, last-update time
- Sound toggle integrated

**Acceptance criteria.**

- During a live game (verified via mock), the mode pill is teal and pulsing
- Freshness counts update live as the page receives SSE events
- Sound toggle works and persists
- Clicking the freshness summary opens a debug panel (Task 5.6 covers full panel; for now, a placeholder modal is fine)

---

## Task 4.3 — View tabs + stat picker

**Goal.** The controls above the board: three view tabs and the stat picker.

**Outputs.**

- `apps/web/src/lib/components/board/ViewTabs.svelte` — three tabs, the third opens a position dropdown
- `apps/web/src/lib/components/board/StatPicker.svelte` — horizontal scrolling list of stats with active highlighting
- Both write to URL search params so views are shareable
- Stat picker shows hitting stats when on hitter views, pitching stats on pitcher views

**Acceptance criteria.**

- Switching tabs updates URL to `?view=hitters` etc.
- Clicking a stat updates URL to `?sort=wRC+`
- Refreshing the page restores the view from URL
- The position dropdown closes correctly on outside-click

---

## Task 4.4 — Board structure (rank, rows, cells)

**Goal.** The HTML/CSS structure of the board: column headers, 100 rows, each row composed of flap cells.

**Outputs.**

- `apps/web/src/lib/components/board/Board.svelte` — top-level board component
- `apps/web/src/lib/components/board/Row.svelte` — single row with rank, player, team, position, stat cells
- Composes `Word` from Task 3.3 for each cell

**Acceptance criteria.**

- Rendering 100 rows of static placeholder data shows the board correctly
- Performance: 100 rows × 6 cells render in under 200ms
- Rows are exactly 36px tall; columns align consistently
- The board is usable at viewports down to 768px (mobile work is Task 7.x)

---

## Task 4.5 — Initial load via REST

**Goal.** On page load, the board fetches the current state via REST and renders it without animation (this is the initial state, nothing to animate from).

**Outputs.**

- `apps/web/src/routes/+page.svelte` updated to call `/api/board?view=...&sort=...` in the load function
- Renders the initial 100 rows from the response
- A small loading state for slow connections

**Acceptance criteria.**

- First paint shows the board with real data within 1s on a fast connection
- A slow connection shows a skeleton state, not a blank page
- View changes (clicking a tab) re-fetch and re-render without a flash of blank content

---

## Task 4.6 — SSE wiring + delta application

**Goal.** After initial load, the frontend opens an SSE connection. Incoming delta events trigger flap animations.

**Outputs.**

- `apps/web/src/lib/api/sse.ts` — SSE client with reconnect logic (exponential backoff)
- `apps/web/src/lib/stores/board.ts` — Svelte store holding the current board state, mutated by SSE events
- Updates to `Board.svelte` to subscribe to the store and pass values to cells

**Acceptance criteria.**

- Triggering a stat change in the mock causes the matching cell on the board to flip within 200ms
- Multiple concurrent changes flip correctly (each cell gets its own flip, no animation conflicts)
- Disconnecting and reconnecting the network triggers SSE reconnect with backoff
- After reconnect, the full snapshot re-syncs to catch up on missed deltas

---

## Task 4.7 — Row reshuffle animation

**Goal.** When a player's rank changes, the row slides to its new position with the staggered timing described in DESIGN.md.

**Inputs.** `DESIGN.md` (When a row changes rank section)

**Outputs.**

- `apps/web/src/lib/components/board/Row.svelte` — uses Svelte's `animate:flip` directive (FLIP technique, fortuitously named) for position animation
- Stagger logic: when 30 rows reshuffle, each animation starts 30ms after the previous
- Plays `flap-row-shift.mp3` once per reshuffle
- Honors reduced-motion (rows snap to position instead of sliding)

**Acceptance criteria.**

- Switching the sort stat reshuffles the board with a visible cascade
- Each affected row's rank cell flips during the slide
- The full reshuffle (100 rows) takes ~3 seconds and is the most beautiful thing on the site
- Reduced-motion: rows snap, no slide

---

# Phase 5 — Player detail + position filtering

Goal: clicking a player opens a detail panel; position filtering produces meaningful sub-views.

- [ ] Task 5.1 — Player detail panel
- [ ] Task 5.2 — Player season trend chart
- [ ] Task 5.3 — Position-filtered views
- [ ] Task 5.4 — URL routing for player detail
- [ ] Task 5.5 — Just-qualified animation
- [ ] Task 5.6 — Freshness debug panel

---

## Task 5.1 — Player detail panel

**Goal.** A side-panel modal that opens when a row is clicked, showing player detail.

**Inputs.** `DESIGN.md` (the Player detail modal section)

**Outputs.**

- `apps/web/src/lib/components/player/Panel.svelte` — slide-in side panel (40% viewport on desktop, full on mobile)
- Header with headshot, name, team, position
- "Hot stats" section using larger flap cells (6-8 stats)
- Full stat table below
- Recent games table (last 5)
- Close on click-outside, Esc, or close button

**Acceptance criteria.**

- Clicking a row opens the panel with that player's detail
- Panel slides in over 300ms
- All keyboard navigation works (Tab cycles through interactive elements, Esc closes)
- The hot stats use flap cells that animate when values update via SSE

---

## Task 5.2 — Player season trend chart

**Goal.** Inside the player panel, a line chart of the currently-active stat over the season.

**Outputs.**

- `apps/web/src/lib/components/player/TrendChart.svelte` — Chart.js wrapper
- Fetches data from `GET /api/players/{id}/history?stat=wRC+`
- X-axis: dates across the season; Y-axis: stat value
- Highlights the current value with a labeled dot

**Acceptance criteria.**

- The chart renders within 200ms of the player panel opening
- Switching the stat picker (in the main board) updates the chart's stat
- The chart is responsive to panel width changes
- Tooltips on hover show date + value

---

## Task 5.3 — Position-filtered views

**Goal.** Selecting a position from the View tabs dropdown filters the board to that position.

**Outputs.**

- Updates to the API to handle position-filtered queries (`?view=ss&sort=wRC+`)
- Updates to the leaderboard cache to include position-filtered views
- Frontend: position-filtered URL renders correctly, position chip visible in header

**Acceptance criteria.**

- `?view=ss&sort=wRC+` returns only SS-eligible players
- The board layout adapts (position column hidden when filtered to a position)
- All ~15 position views work (C, 1B, 2B, 3B, SS, LF, CF, RF, OF, DH, UT, SP, RP, plus the two "all" views)

---

## Task 5.4 — URL routing for player detail

**Goal.** The player panel state is reflected in the URL: `/player/judge-aaron` opens Aaron Judge's panel directly.

**Outputs.**

- A new route `/player/[slug]/+page.svelte` that opens the player panel with the rest of the board behind it
- A URL slug computed from player name (kebab-case, lowercase)
- Browser back button closes the panel correctly
- Sharing the URL opens the panel directly

**Acceptance criteria.**

- Visiting `/player/judge-aaron` shows the panel open with Judge's data, board visible behind
- Browser back button closes the panel and returns to the main board
- Refreshing the page on the URL re-opens the panel correctly

---

## Task 5.5 — Just-qualified animation

**Goal.** When a player crosses the qualification threshold mid-game, their row enters from below the visible area with a small `(just qualified)` badge that fades after 24 hours.

**Outputs.**

- The api delta event includes a `newly_qualified` flag for any player who first appeared in the leaderboard since the last delta
- Frontend handles the slide-in animation
- `(just qualified)` badge added to the player name cell, faded out via CSS at 24h

**Acceptance criteria.**

- Manually triggering a qualification event in the mock causes the row to slide in from below over 800ms
- The badge appears and is visible
- The badge fades automatically over a CSS animation set to 24h (verify with a 24-second test)

---

## Task 5.6 — Freshness debug panel

**Goal.** The "nerd-mode" panel that opens from the header status bar showing ingest history, schema drift, per-stat freshness.

**Inputs.** `DESIGN.md` (the Freshness debugging panel section)

**Outputs.**

- `apps/web/src/lib/components/board/FreshnessPanel.svelte`
- Fetches from `/api/freshness`
- Renders the last 10 ingest runs with timestamps and outcomes
- Per-stat freshness summary with color-coded dots
- Schema drift log if any drift is detected

**Acceptance criteria.**

- Clicking the freshness summary in the header opens the panel
- All data is from real API endpoints, not mocked
- The panel is fully accessible (keyboard navigable, screen-reader friendly)

---

# Phase 6 — Off-season + preview mode

Goal: the site handles the off-season honestly and provides preview mode for off-season visitors.

- [ ] Task 6.1 — Off-season banner + state handling
- [ ] Task 6.2 — Preview mode (replay)
- [ ] Task 6.3 — Between-games and no-games-today states

---

## Task 6.1 — Off-season banner + state handling

**Goal.** When the season-state endpoint returns `off-season`, the banner replaces the live status.

**Inputs.** `DESIGN.md` (the Off-season presentation section)

**Outputs.**

- Updates to `Header.svelte` to handle the off-season state
- Banner shows "[Year] regular season · final" with a countdown to next season
- SSE connection is not opened in off-season mode (saves API resources)
- Stat picker still works (re-sorting triggers split-flap animation)

**Acceptance criteria.**

- Manually setting season-state to off-season shows the banner correctly
- No SSE connection is opened (verify in network tab)
- Re-sorting still animates correctly
- The countdown updates daily

---

## Task 6.2 — Preview mode (replay)

**Goal.** A "preview mode" button that triggers a replay of a recent week's games at accelerated speed, so off-season visitors can see the split-flap mechanic.

**Outputs.**

- Backend: a new ingest mode that reads from a saved fixture set (last week of regular-season games) and replays them at 5min:1week speed
- Backend: a new SSE endpoint `/api/board/preview-sse` that emits the same delta format
- Frontend: a "Preview mode" button in the off-season banner; clicking starts the replay
- Frontend: a "preview running" indicator visible while in preview mode; an "exit" button to return to static off-season view

**Acceptance criteria.**

- Starting preview mode causes the board to begin animating with realistic deltas
- The preview clearly indicates it's a replay, not live
- Exiting preview returns to the final-season view cleanly
- Multiple visitors can run preview simultaneously without interfering with each other

---

## Task 6.3 — Between-games and no-games-today states

**Goal.** Handle the in-season-but-no-current-games state gracefully.

**Outputs.**

- Header banner shows "No games until [next game] · in [N hours]" when no games are live
- SSE still opens (in case a game starts) but at a slower heartbeat (2 minutes)
- Stat picker still works for re-sorting

**Acceptance criteria.**

- A day with no scheduled games shows the appropriate banner
- A day with games but none currently live shows the "next game in" banner
- When a game starts, the banner switches automatically to "live" within 60 seconds

---

# Phase 7 — Polish + case study

Goal: the site is fast, accessible, and feels finished. Case study written. Public launch.

- [ ] Task 7.1 — Performance pass
- [ ] Task 7.2 — Accessibility pass
- [ ] Task 7.3 — Mobile experience
- [ ] Task 7.4 — SEO + Open Graph
- [ ] Task 7.5 — Methodology page
- [ ] Task 7.6 — Write the case study
- [ ] Task 7.7 — Launch

---

## Task 7.1 — Performance pass

**Goal.** The board renders smoothly during high-activity moments (multiple games live, many concurrent deltas).

**Outputs.**

- A Playwright perf script that simulates a busy ingest period
- Optimization of the flap animation to use compositor-only transforms
- Lazy loading of player detail content
- Image optimization for headshots

**Acceptance criteria.**

- 60fps maintained during a 50-cell simultaneous flap (verify in Performance tab)
- Lighthouse Performance ≥ 90 on desktop and ≥ 80 on mobile (mobile is harder due to animation)
- Initial board render under 1.5s on a fast connection
- INP under 200ms for stat-picker switches (the highest-load interaction)

---

## Task 7.2 — Accessibility pass

**Goal.** Lighthouse Accessibility 100. Site usable with screen reader.

**Outputs.**

- A Playwright + axe-core script
- Fixes for any violations
- ARIA labels on flap cells (`aria-label="rank 1, Aaron Judge, NYY, OF, wRC plus 198"`)
- The flap animation has `aria-live="polite"` so updates are announced (but throttled — too many announcements is its own accessibility issue)
- Keyboard navigation: Tab through rows, Enter to open detail, Esc to close

**Acceptance criteria.**

- axe-core: 0 violations on every page
- Lighthouse Accessibility: 100
- Site fully usable with keyboard
- Screen reader announces stat changes meaningfully (test with VoiceOver)

---

## Task 7.3 — Mobile experience

**Goal.** The site works on mobile. The board becomes a vertical card list; the split-flap still flips on cards.

**Inputs.** `DESIGN.md` (the Responsive behavior section)

**Outputs.**

- Mobile breakpoint adaptations for Board, Row, ViewTabs, StatPicker
- Card layout: vertical stack of player cards
- Touch interactions: tap to open detail panel, swipe to dismiss

**Acceptance criteria.**

- Site is usable at 375px width
- Tap targets are ≥ 44px
- The split-flap flip works on cards
- No horizontal scroll
- Performance still 60fps on a mid-range Android (Pixel 5 or similar)

---

## Task 7.4 — SEO + Open Graph

**Goal.** Real metadata, dynamic OG image generation showing the current top 3 players.

**Outputs.**

- `apps/web/src/lib/components/shell/SEO.svelte`
- An OG image generator that renders a 1200x630 image with the current top 3 hitters (regenerated daily)
- robots.txt, sitemap.xml

**Acceptance criteria.**

- Each page has unique title and description
- OG image previews correctly on Twitter/X, LinkedIn (test via opengraph.xyz)
- The OG image shows real recent top players
- A new top-3 entry triggers an OG image regeneration within 24 hours

---

## Task 7.5 — Methodology page

**Goal.** A public `/methodology` page that explains the data sources, formulas, and limits.

**Outputs.**

- `apps/web/src/routes/methodology/+page.svelte`
- Renders content from `DATA.md` (or a curated subset) as a nicely typeset page
- Links to `STATS.md` for the stat formulas
- Visible link from the footer

**Acceptance criteria.**

- The page is readable and well-organized
- All claims about data sources are accurate
- The page links back to the GitHub repo for the full docs

---

## Task 7.6 — Write the case study

**Goal.** A 2500-3500 word case study for the portfolio site.

**Outputs.**

- `packages/content/case-studies/diamond.md` (in the portfolio site's repo)
- Sections: pitch, why, architecture (with diagram), the split-flap engineering (with code excerpt of the animation), the data pipeline (with diagram), decisions (why MLB Stats API not FanGraphs, why not Statcast for catchers, why no WAR), lessons, adjacent projects

**Acceptance criteria.**

- The case study reads as a piece of writing
- Voice matches the portfolio's voice and tone
- Decisions are owned, not justified by appeals to authority
- Links to live site, GitHub repo, methodology doc

---

## Task 7.7 — Launch

**Goal.** Site is live, monitored, the portfolio links to it.

**Outputs.**

- Update portfolio's project metadata to point at live URL
- Replace case-study placeholder with live demo embed
- Cloud Monitoring alert policies (uptime, error rate, ingest staleness, cost projection)
- Status page

**Acceptance criteria.**

- Live site reachable from portfolio
- All alerts verified by manually inducing then resolving each condition
- Initial social posts queued

---

# Phase 8 — v2 stretch

Open-ended.

- More Statcast stats (xBA, xSLG, xwOBA on the main board)
- Catcher framing if a data source becomes available
- Multi-position eligibility view (fantasy-friendly)
- Historical mode (show top 100 by wRC+ for any past season)
- "Sound on by default" experiment (probably no, but worth testing)
- Mobile board redesign (cards aren't quite right; maybe horizontal scroll with frozen rank+name columns)
- A `/widgets` API for embedding leaderboards on other sites
