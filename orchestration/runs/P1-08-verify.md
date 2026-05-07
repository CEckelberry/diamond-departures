# P1-08 verification (leaderboard materialization)

Date: 2026-05-07

## RED evidence
- Command: `.venv/bin/pytest apps/ingest/tests/test_leaderboards.py -q`
- Result: import error for missing `leaderboards` module.

## GREEN verification
1. `.venv/bin/pytest apps/ingest/tests/test_leaderboards.py -q`
   - Result: PASS (3 passed)

## Notes
- Affected-view mapper covers base hitter view plus position-specific hitter views.
- Recompute operation replaces rows per `(view_key, sort_stat)` and emits top-100 sorted rows.
- Position filter enforces eligibility (SS view excludes non-SS players).
