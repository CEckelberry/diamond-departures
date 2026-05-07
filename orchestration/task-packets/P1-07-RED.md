# Packet P1-07-RED — player stat updates tests first

## Goal

Task 1.7 RED: verify append-only player stat updates and derived stat writes.

## Scope

Create failing tests for:

1. append-only upsert for `(player_id, stat_name, season)` closes prior `valid_to IS NULL` row and inserts new current row.
2. unchanged stat values do not create a new row.
3. derived stat computation includes `wRC+` and `OPS` and is written for affected players.

## Constraints

- RED only.
- No external API calls.
- Time handling deterministic in tests.

## Acceptance

`.venv/bin/pytest apps/ingest/tests/test_player_stats_store.py apps/ingest/tests/test_player_updater.py -q`
