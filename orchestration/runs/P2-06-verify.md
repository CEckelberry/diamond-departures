# P2-06 verification (player detail endpoints)

Date: 2026-05-07

## RED evidence

- Command: `.venv/bin/pytest apps/api/tests/test_players.py -q`
- Result: RED failed with `TypeError: create_app() got an unexpected keyword argument 'player_detail_reader'`.

## GREEN verification

1. `.venv/bin/pytest apps/api/tests/test_players.py -q`
   - Result: PASS (6 passed)
2. `.venv/bin/pytest apps/api/tests -q`
   - Result: PASS (23 passed)

## Notes

- Added `/api/players/{player_id}` endpoint returning player metadata + stat sections.
- Added `/api/players/{player_id}/history?stat=...` endpoint with stat validation, player 404 handling, and ascending timestamp points.
- Reader dependencies are injectable for tests; defaults are in-memory placeholders for now.
