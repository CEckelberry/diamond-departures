# Phase 0 + Phase 1 Execution Schedule (1–3h packets)

Scope: `TASKS.md` Phase 0 and Phase 1 only.
Packet size: 1–3h.
Roles used: `local-coder`, `reviewer`, `verifier`, `syncer`.

## Check-in cadence (explicit)

- **Cadence rule:** check-in every **2 hours or packet completion**, whichever comes first.
- **Daily sync points:** `T+0h` kickoff, `T+2h`, `T+4h`, `T+6h` wrap.
- **At each check-in, syncer posts:**
  1. packets done/in-progress/blocked,
  2. command results (pass/fail only),
  3. next packet + dependency status,
  4. risks needing decision.
- **Gate rule:** no packet starts until dependency packets show reviewer/verifier pass.

---

## Phase 0 packets (Foundation)

| Packet | Est | Owner | File ownership (exclusive in packet) | Depends on | Verification command(s) |
|---|---:|---|---|---|---|
| P0-01 | 2h | local-coder | `pnpm-workspace.yaml`, `package.json`, `Makefile`, `.gitignore`, `.editorconfig`, `LICENSE`, base dirs | none | `pnpm install`; `make dev` |
| P0-02 | 1h | reviewer | review only for P0-01 files | P0-01 | `git diff --name-only` matches Task 0.1 |
| P0-03 | 1h | verifier | verify only | P0-02 | `pnpm install`; `make dev`; `find apps packages infra .github -maxdepth 2 -type d` |
| P0-04 | 3h | local-coder | `apps/api/migrations/001_init.sql`, `packages/content/teams.json` | P0-03 | `make migrate`; `psql "$DATABASE_URL" -c "\\d+ players"` |
| P0-05 | 2h | local-coder | `apps/api/migrations/002_seed_teams.sql`, `apps/api/migrations/003_park_factors.sql`, `packages/content/park-factors-2026.json` | P0-04 | `psql "$DATABASE_URL" -c "SELECT count(*) FROM teams;"` |
| P0-06 | 1h | reviewer | review only for P0-04/05 files | P0-05 | migration SQL + numeric type checks |
| P0-07 | 1h | verifier | verify only | P0-06 | `make migrate`; `migrate down`; `make migrate` |
| P0-08 | 3h | local-coder | `apps/mlb-mock/cmd/server/main.go`, `apps/mlb-mock/Dockerfile` | P0-07 | `go run ./apps/mlb-mock/cmd/server --replay-speed=300x` |
| P0-09 | 3h | local-coder | `apps/mlb-mock/internal/data/schedule*.json`, `.../game-feed*.json` fixtures | P0-08 | `curl localhost:8090/api/v1/schedule?date=today` |
| P0-10 | 2h | local-coder | `apps/mlb-mock/internal/data/people-stats*.json`, `.../roster*.json` fixtures | P0-09 | `curl localhost:8090/api/v1/people/{id}/stats?group=hitting,pitching` |
| P0-11 | 1h | reviewer | review only for P0-08/09/10 files | P0-10 | response shape parity checklist |
| P0-12 | 1h | verifier | verify only | P0-11 | schedule/feed/people/roster curls + replay timing check |
| P0-13 | 2h | local-coder | `docker-compose.yml` (`db`, `mlb-mock`, placeholders `api`/`ingest`/`web`) | P0-12 | `docker compose up -d`; `docker compose ps` |
| P0-14 | 1h | local-coder | Makefile targets: `make dev`, `make dev-clean`, db-init wiring | P0-13 | `make dev`; `make dev-clean` |
| P0-15 | 1h | verifier | verify only | P0-14 | port checks: `5432`, `8090`, `5173` reachable |
| P0-16 | 2h | local-coder | `.github/workflows/ci.yml`, `.github/workflows/README.md` | P0-15 | `actionlint` |
| P0-17 | 1h | reviewer | review only for P0-16 | P0-16 | path-filter + fail-fast checks |
| P0-18 | 3h | local-coder | `apps/web/*` init + Tailwind v4 + token scaffold (`src/app.css`) | P0-17 | `pnpm --filter web dev` |
| P0-19 | 2h | local-coder | `apps/web/src/routes/+page.svelte` placeholder split-flap cell + fonts setup | P0-18 | browser check: tokens + fonts + dark/light |
| P0-20 | 1h | verifier | verify only | P0-19 | `pnpm --filter web dev`; visual acceptance checklist |
| P0-21 | 1h | syncer | `orchestration/task-board.yaml`, `orchestration/checkins/*` status update | P0-20 | phase report posted; blockers list empty/non-empty |

---

## Phase 1 packets (Data pipeline)

| Packet | Est | Owner | File ownership (exclusive in packet) | Depends on | Verification command(s) |
|---|---:|---|---|---|---|
| P1-01 | 3h | local-coder | `packages/stats/hitting/basic.go`, tests | P0-21 | `go test ./packages/stats/hitting -run Basic` |
| P1-02 | 3h | local-coder | `packages/stats/hitting/woba.go`, `woba_weights_2026.json`, tests | P1-01 | `go test ./packages/stats/hitting -run WOBA` |
| P1-03 | 2h | local-coder | `packages/stats/hitting/wrc.go`, LeagueContext wiring, tests/docs | P1-02 | `go test ./packages/stats/hitting`; `go test -cover ./packages/stats/hitting` |
| P1-04 | 1h | reviewer | review only for P1-01..03 | P1-03 | formula/source citation review vs `STATS.md` |
| P1-05 | 1h | verifier | verify only | P1-04 | curated sample assertions + coverage >90% |
| P1-06 | 3h | local-coder | `packages/stats/pitching/basic.go`, tests | P1-05 | `go test ./packages/stats/pitching -run Basic` |
| P1-07 | 3h | local-coder | `packages/stats/pitching/fip.go`, `cfip_2026.json`, tests | P1-06 | `go test ./packages/stats/pitching -run FIP` |
| P1-08 | 2h | local-coder | `packages/stats/pitching/siera.go`, `era_plus.go`, tests | P1-07 | `go test ./packages/stats/pitching` |
| P1-09 | 1h | reviewer | review only for P1-06..08 | P1-08 | cFIP/ERA parity logic check |
| P1-10 | 1h | verifier | verify only | P1-09 | `go test ./packages/stats/pitching` |
| P1-11 | 2h | local-coder | `packages/stats/defensive/parsers.go`, fixture tests | P1-10 | `go test ./packages/stats/defensive -run Parser` |
| P1-12 | 1h | local-coder | `packages/stats/defensive/qualification.go`, tests | P1-11 | `go test ./packages/stats/defensive` |
| P1-13 | 1h | verifier | verify only | P1-12 | DRS/UZR/UZR150/noisy-tag checks |
| P1-14 | 2h | local-coder | `packages/stats/verify/data.json` curation | P1-13 | dataset doc completeness check |
| P1-15 | 2h | local-coder | `packages/stats/verify/verify_test.go`, CI hook | P1-14 | `go test ./packages/stats/verify` |
| P1-16 | 1h | reviewer | review only for P1-14/15 | P1-15 | diff reporting quality check |
| P1-17 | 3h | local-coder | `apps/ingest/cmd/job/main.go`, `internal/config/config.go`, `internal/store/postgres.go` | P1-16 | `cd apps/ingest && go run ./cmd/job` |
| P1-18 | 2h | local-coder | `apps/ingest/internal/mlb/client.go`, retry/429 behavior | P1-17 | ingest run against mock; retry log check |
| P1-19 | 1h | verifier | verify only | P1-18 | prod JSON logging + image size check |
| P1-20 | 2h | local-coder | `internal/schedule/schedule.go`, integration tests | P1-19 | `go test ./apps/ingest/internal/schedule` |
| P1-21 | 3h | local-coder | `internal/games/processor.go`, `internal/state/diff.go`, tests | P1-20 | idempotency + 5-event diff test |
| P1-22 | 1h | verifier | verify only | P1-21 | run ingest twice; second run no updates |
| P1-23 | 3h | local-coder | `internal/players/updater.go`, `internal/store/player_stats.go` | P1-22 | SQL checks on `valid_from/valid_to` |
| P1-24 | 2h | local-coder | `internal/leaderboards/recompute.go` + affected-view mapper | P1-23 | top-100 recompute query checks |
| P1-25 | 2h | local-coder | `internal/drift/hasher.go`, `internal/drift/detector.go`, migration `004_drift_signatures.sql` | P1-24 | drift add/remove-key simulations |
| P1-26 | 2h | local-coder | `internal/positions/classify.go` + qualification logic | P1-25 | manual SP/RP/eligible-pos cases |
| P1-27 | 1h | reviewer | review only for P1-23..26 | P1-26 | append-only + view consistency + drift safety |
| P1-28 | 2h | verifier | end-to-end verify | P1-27 | `make dev`; ingest against mock; SQL acceptance checklist for Tasks 1.6–1.10 |
| P1-29 | 1h | syncer | `orchestration/task-board.yaml`, `orchestration/checkins/*` phase closure | P1-28 | Phase 1 completion note + open risks |

---

## Dependency chain summary (critical path)

`P0-01 -> P0-03 -> P0-07 -> P0-12 -> P0-15 -> P0-17 -> P0-20 -> P0-21 -> P1-01 -> P1-05 -> P1-10 -> P1-13 -> P1-16 -> P1-19 -> P1-22 -> P1-26 -> P1-28 -> P1-29`

## Practical sequencing notes

- Keep **one active code owner per file set** to avoid merge collisions.
- Run reviewer/verifier packets as hard gates, not optional.
- If a packet fails verification, reopen same packet ID with suffix `-R1`, keep dependencies unchanged.
