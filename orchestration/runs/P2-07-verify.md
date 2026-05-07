# P2-07 verification (season-state + freshness endpoints)

Date: 2026-05-07

## RED evidence

- Command: `.venv/bin/pytest apps/api/tests/test_status.py -q`
- Result: RED failed with `TypeError: create_app() got an unexpected keyword argument 'season_state_reader'`.

## GREEN verification

1. `.venv/bin/pytest apps/api/tests/test_status.py -q`
   - Result: PASS (2 passed)
2. `.venv/bin/pytest apps/api/tests -q`
   - Result: PASS (25 passed)

## Notes

- Added `/api/season-state` endpoint and enforced valid mode domain (`live|between|off-game|off-season`).
- Added `/api/freshness` endpoint returning ingest/drift/stat freshness payload.
- Added cache semantics: `Cache-Control: public, max-age=300` for season-state and `Cache-Control: no-store` for freshness.
