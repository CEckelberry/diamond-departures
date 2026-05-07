# Packet P0-03-RED — MLB mock tests first (TDD)

## Goal

Write failing tests first for Task 0.3 (MLB mock service contracts).

## Required context

- `TASKS.md` Task 0.3
- `DATA.md` stat source section
- `ARCHITECTURE.md` ingest flow references to MLB endpoints

## Scope (tests only)

Create contract tests for these endpoints (served at localhost:8090):

- `/api/v1/schedule?date=today`
- `/api/v1/game/{id}/feed/live`
- `/api/v1/people/{id}/stats?group=hitting,pitching`
- `/api/v1/teams/{id}/roster`

## Required outputs

- `tests/mlb_mock/test_contracts.py` (unittest or pytest)
- `tests/mlb_mock/README.md` test assumptions
- Optional test fixtures under `tests/mlb_mock/fixtures/`

## Constraints

- No service implementation in this packet.
- Tests should fail until mock service exists and returns expected shape.
- Validate schema shape, required keys, and replay-speed behavior contract.

## Acceptance checks

- `python -m unittest discover -s tests` runs
- At least one test fails in RED phase due to missing/incorrect implementation

## Deliver back

1. Unified diff
2. Test command output showing RED state
3. Notes for GREEN implementation packet
