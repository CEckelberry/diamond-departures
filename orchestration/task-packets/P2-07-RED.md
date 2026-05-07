# Packet P2-07-RED — season-state + freshness tests first

## Goal

Task 2.7 RED start: define failing tests for transparency endpoints.

## Scope

Create failing tests for:

1. `GET /api/season-state` returns mode, next_game_at, and current_season.
2. `GET /api/season-state` sets cache headers for 5-minute caching.
3. `GET /api/freshness` returns ingest runs, schema drift, and per-stat freshness summary.
4. `GET /api/freshness` sets `Cache-Control: no-store`.

## Constraints

- RED-only start.
- Use in-process test doubles.

## Acceptance

`.venv/bin/pytest apps/api/tests/test_status.py -q`
