# P1-06 verification (schedule + game feed processing)

Date: 2026-05-07

## RED evidence
- Command: `.venv/bin/pytest apps/ingest/tests/test_schedule.py apps/ingest/tests/test_game_processor.py apps/ingest/tests/test_state_diff.py -q`
- Result: collection failures for missing `schedule`, `game_processor`, `state_diff` modules.

## GREEN verification
1. `.venv/bin/pytest apps/ingest/tests/test_schedule.py apps/ingest/tests/test_game_processor.py apps/ingest/tests/test_state_diff.py -q`
   - Result: PASS (3 passed)
2. `.venv/bin/pytest apps/ingest/tests -q`
   - Result: PASS (10 passed)

## Notes
- Live schedule parsing now returns only in-progress games.
- Game feed extraction returns 5 stat-changing player events from fixture.
- State diff snapshot prevents duplicate updates on second run (idempotency).
