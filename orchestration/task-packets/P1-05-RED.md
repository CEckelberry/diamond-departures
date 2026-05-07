# Packet P1-05-RED — ingest skeleton + MLB client tests first

## Goal

Task 1.5 RED: create failing tests for Python ingest skeleton paths.

## Scope

Create failing tests for:

1. config loader (`apps/ingest/app/config.py`) env parsing + defaults.
2. MLB HTTP client wrapper (`apps/ingest/app/mlb_client.py`) retry policy for transient failures and 429 backoff handling.
3. DB init wrapper (`apps/ingest/app/store.py`) engine/session creation API.
4. ingest job entrypoint smoke (`apps/ingest/app/job.py`) calls wiring pieces.

## Constraints

- RED only.
- Tests deterministic (mock HTTP + sleep).
- No network calls in tests.

## Acceptance

`.venv/bin/pytest apps/ingest/tests/test_config.py apps/ingest/tests/test_mlb_client.py apps/ingest/tests/test_store.py apps/ingest/tests/test_job.py -q`
