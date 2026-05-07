# P2-02 verification (leaderboard REST endpoint)

Date: 2026-05-07

## RED evidence
- Command: `.venv/bin/pytest apps/api/tests/test_board.py -q`
- Result: `TypeError` because `create_app` lacked `board_reader` and `/api/board` contract.

## GREEN verification
1. `.venv/bin/pytest apps/api/tests/test_board.py -q`
   - Result: PASS (3 passed)
2. `.venv/bin/pytest apps/api/tests -q`
   - Result: PASS (9 passed)

## Notes
- Added `/api/board` with `view` and `sort` validation (400 on invalid query values).
- Response includes rank, player metadata, stat value, and freshness (`timestamp`, `age_category`).
- Payload capped to top 100 rows.
