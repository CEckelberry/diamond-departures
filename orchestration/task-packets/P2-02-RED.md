# Packet P2-02-RED — leaderboard REST tests first

## Goal

Task 2.2 RED: define failing tests for `/api/board` query validation and response contract.

## Scope

Create failing tests for:

1. `GET /api/board?view=hitters&sort=wRC+` returns <=100 ranked entries with player metadata.
2. Invalid `view` returns 400 with clear error.
3. Invalid `sort` returns 400 with clear error.
4. Freshness object includes timestamp and age category (`live|recent|stale|old`).

## Constraints

- RED only.
- No real DB access.

## Acceptance

`.venv/bin/pytest apps/api/tests/test_board.py -q`
