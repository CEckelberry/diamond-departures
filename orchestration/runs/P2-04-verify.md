# P2-04 verification (Pub/Sub subscriber invalidation flow)

Date: 2026-05-07

## RED evidence
- Command: `.venv/bin/pytest apps/api/tests/test_pubsub.py -q`
- Result: `ModuleNotFoundError: No module named 'apps.api.app.pubsub'`.

## GREEN verification
1. `.venv/bin/pytest apps/api/tests/test_pubsub.py -q`
   - Result: PASS (4 passed)

## Notes
- Added `RefreshSubscriber` with message parsing for single and batched `(view, sort)` targets.
- Added ACK/NACK behavior and refresh-context logging (`view`, `sort`, `reason`).
