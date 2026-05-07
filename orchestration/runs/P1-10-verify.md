# P1-10 verification (position taxonomy + qualification)

Date: 2026-05-07

## RED evidence
- Command: `.venv/bin/pytest apps/ingest/tests/test_positions.py -q`
- Result: `ModuleNotFoundError: No module named 'apps.ingest.app.positions'`.

## GREEN verification
1. `.venv/bin/pytest apps/ingest/tests/test_positions.py -q`
   - Result: PASS (5 passed)
2. `.venv/bin/pytest apps/ingest/tests -q`
   - Result: PASS (26 passed)

## Notes
- Non-pitcher primary position, OF tie collapse, UT multi-position behavior implemented.
- SP/RP split uses `starts / appearances > 0.5`.
- Qualification thresholds: hitter `ceil(2.7 * team_games)`, SP `1.0 * team_games IP`, RP `25 appearances`.
- `just_qualified_at` set on first crossing and preserved while qualified.
