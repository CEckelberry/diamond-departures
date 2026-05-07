# Packet P2-06-RED — player detail endpoint tests first

## Goal

Task 2.6 RED start: define failing tests for player detail and player history endpoint contracts.

## Scope

Create failing tests for:

1. `GET /api/players/{id}` returns player metadata, season totals, stat line, and recent games.
2. `GET /api/players/{id}/history?stat=...` returns time-ordered points for the requested stat.
3. Unknown player id returns 404 for both endpoints.
4. Missing/invalid `stat` query returns 400 for history endpoint.

## Constraints

- RED-only start.
- Use in-process test doubles; no external DB.

## Acceptance

`.venv/bin/pytest apps/api/tests/test_players.py -q`
