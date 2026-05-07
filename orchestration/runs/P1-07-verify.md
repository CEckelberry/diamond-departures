# P1-07 verification (player stat updates + derived stats)

Date: 2026-05-07

## RED evidence
- Command: `.venv/bin/pytest apps/ingest/tests/test_player_stats_store.py apps/ingest/tests/test_player_updater.py -q`
- Result: import errors for missing `player_stats_store` and `player_updater` modules.

## GREEN verification
1. `.venv/bin/pytest apps/ingest/tests/test_player_stats_store.py apps/ingest/tests/test_player_updater.py -q`
   - Result: PASS (5 passed)

## Notes
- Append-only valid window behavior verified (`valid_to` closes previous row, one current row remains).
- Derived stat update includes `OPS` and `wRC+` writes.
- Repeating same input skips inserts for unchanged values.
