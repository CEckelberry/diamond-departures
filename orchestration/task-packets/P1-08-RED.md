# Packet P1-08-RED — leaderboard materialization tests first

## Goal

Task 1.8 RED: verify affected-view mapping and leaderboard materialization behavior.

## Scope

Create failing tests for:

1. mapping updated stats to impacted `(view_key, sort_stat)` combos.
2. materialization replacing a combo with exactly top-100 ordered rows.
3. position-filtered views include only eligible players (example: SS).

## Constraints

- RED only.
- In-memory fixtures only.
- Deterministic ordering for ties.

## Acceptance

`.venv/bin/pytest apps/ingest/tests/test_leaderboards.py -q`
