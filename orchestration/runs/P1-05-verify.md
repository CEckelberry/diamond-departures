# P1-05 verification (ingest skeleton + MLB client)

Date: 2026-05-07

## RED evidence
- Command: `.venv/bin/pytest apps/ingest/tests/test_config.py apps/ingest/tests/test_mlb_client.py apps/ingest/tests/test_store.py apps/ingest/tests/test_job.py -q`
- Result: collection failures for missing `apps.ingest.app.*` modules.

## GREEN verification
1. `.venv/bin/pytest apps/ingest/tests/test_config.py apps/ingest/tests/test_mlb_client.py apps/ingest/tests/test_store.py apps/ingest/tests/test_job.py -q`
   - Result: PASS (7 passed)

## Notes
- Added env config loader, retrying MLB client with 429 handling, store init wrapper, and one-shot job entrypoint.
- Added ingest Dockerfile for job runtime skeleton.
