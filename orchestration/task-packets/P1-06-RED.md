# Packet P1-06-RED — schedule + game feed tests first

## Goal

Task 1.6 RED: tests for schedule scanning, live game feed extraction, diff/idempotency.

## Scope

Create failing tests for:

1. schedule loader returns only live game IDs from mock schedule fixture.
2. game feed processor extracts stat-changing player events from mock feed fixture.
3. state diff helper identifies new updates vs previous snapshot.
4. idempotency: second run with same feed yields no new updates.

## Constraints

- RED only.
- Use mlb-mock fixture payloads (existing + new under tests fixtures).
- No external API calls.

## Acceptance

`.venv/bin/pytest apps/ingest/tests/test_schedule.py apps/ingest/tests/test_game_processor.py apps/ingest/tests/test_state_diff.py -q`
