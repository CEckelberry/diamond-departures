# P0-02 run artifact

## Local model runs

1) `python3 scripts/local_llm_task.py --model coder-fast --task-file orchestration/task-packets/P0-02.md --out orchestration/runs/P0-02-coder-fast.txt`
- Result: wrote `orchestration/runs/P0-02-coder-fast.txt`
- Review: output schema diverged from `ARCHITECTURE.md` (wrong tables/columns), truncated park-factors SQL.

2) `python3 scripts/local_llm_task.py --model coder-accurate --task-file orchestration/task-packets/P0-02.md --out orchestration/runs/P0-02-coder-accurate.txt`
- Result: wrote `orchestration/runs/P0-02-coder-accurate.txt`
- Review: output still diverged from required tables (`player_stats`, `leaderboard_views`, `ingest_runs`) and naming constraints.

## Applied changes

Implemented packet outputs manually to match task + architecture:
- `apps/api/migrations/001_init.sql`
  - Created `teams`, `players`, `player_stats`, `leaderboard_views`, `games`, `ingest_runs`.
  - Added required indexes/constraints from architecture.
  - Enforced decimal stat columns as `numeric(8, 3)`.
  - Included up/down blocks in migration-tool comment convention.
- `apps/api/migrations/002_seed_teams.sql`
  - Seeded canonical MLB 30 teams.
  - Added idempotent `ON CONFLICT (id) DO UPDATE` behavior.
- `apps/api/migrations/003_park_factors.sql`
  - Added `park_factors` table + season seed rows for all 30 teams.
- `packages/content/teams.json`
  - Canonical 30-team dataset (`id`, `name`, `abbr`, `division`, `league`).
- `packages/content/park-factors-2026.json`
  - Placeholder 2026 park-factor dataset (30 teams).
- `Makefile`
  - Added `migrate` target using `$DATABASE_URL` + `migrate ... up`.
  - Added `migrate-down` helper target using `migrate ... down -all`.

## Verification commands and results

### 1) Make target wiring
Command:
`make -n migrate | head -n 3`

Result:
- `test -n "$DATABASE_URL" || { echo "DATABASE_URL is required"; exit 1; }`
- `migrate -database "$DATABASE_URL" -path apps/api/migrations up`

### 2) Guard when env missing
Command:
`make migrate`

Result:
- `DATABASE_URL is required`
- make exits non-zero as expected.

### 3) Content file sanity
Command:
`python3 - <<'PY' ... PY`

Result:
- `teams 30`
- `parks 30`
- `team_ids_match True`

### 4) Numeric type check in SQL
Command:
`rg -n "numeric\(|float|double precision" apps/api/migrations/*.sql`

Result:
- `numeric(8, 3)` present on decimal stat columns.
- No `float`/`double precision` found.

## Blockers / assumptions

- Blocker: local environment has no `migrate` binary (`command -v migrate` => `no`).
- Blocker: no Postgres instance / `$DATABASE_URL` provided in this run.
- Therefore full acceptance checks (`make migrate` against DB, `\d+ players`, `SELECT count(*) FROM teams`, down/up cycle) could not be executed here.

## Files changed in this run

- `Makefile`
- `apps/api/migrations/001_init.sql`
- `apps/api/migrations/002_seed_teams.sql`
- `apps/api/migrations/003_park_factors.sql`
- `packages/content/teams.json`
- `packages/content/park-factors-2026.json`
- `orchestration/runs/P0-02-coder-fast.txt`
- `orchestration/runs/P0-02-coder-accurate.txt`
- `orchestration/runs/P0-02-run.md`
