# MLB Mock contract tests (RED phase)

These tests define the expected contract for the offline MLB mock service at `http://localhost:8090`.

## Endpoints covered

- `GET /api/v1/schedule?date=today`
- `GET /api/v1/game/{id}/feed/live`
- `GET /api/v1/people/{id}/stats?group=hitting,pitching`
- `GET /api/v1/teams/{id}/roster`

## Assumptions

- Tests hit a running service at `localhost:8090`.
- Response shape should follow MLB Stats API-style objects (top-level object, expected nested keys, arrays where expected).
- For replay behavior, the service is started in accelerated replay mode (`--replay-speed`, e.g. `300x`).
- In replay mode, repeated polls of a live game feed should show progress markers changing over short intervals.

## RED intent

This packet is intentionally test-only. No service implementation is included.

Expected state now: `python -m unittest discover -s tests` fails until `apps/mlb-mock` is implemented and serving contract-compliant JSON.

## GREEN packet notes

Service implementation should satisfy all assertions in `test_contracts.py`, especially:

- Required keys and nested shape on all four endpoints.
- Presence of both `hitting` and `pitching` groups on people stats when `group=hitting,pitching`.
- At least one live game in today's replay schedule.
- Observable feed progression between rapid polls in replay mode.
