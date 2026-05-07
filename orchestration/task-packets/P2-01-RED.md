# Packet P2-01-RED — API skeleton tests first

## Goal

Task 2.1 RED: define failing tests for FastAPI skeleton config/logging/health behavior.

## Scope

Create failing tests for:

1. App factory mounts `/api/health`.
2. Health returns `ok` when DB checker succeeds.
3. Health returns `degraded` + HTTP 503 when DB checker fails.
4. Config loader reads `PORT`, `LOG_LEVEL`, and `DATABASE_URL` env values.

## Constraints

- RED only.
- No real DB dependency.
- Tests must run with pytest only.

## Acceptance

`.venv/bin/pytest apps/api/tests/test_health.py apps/api/tests/test_config.py -q`
