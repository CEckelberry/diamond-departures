# Packet P2-05-RED — SSE snapshot/delta/heartbeat tests first

## Goal

Task 2.5 RED start: define failing tests for SSE stream behavior and connection management.

## Scope

Create failing tests for:

1. `GET /api/board/sse` sends immediate `snapshot` event for requested `(view, sort)`.
2. Publishing a refreshed snapshot emits a `delta` event with rank/stat changes.
3. Idle connection emits `heartbeat` events on cadence.
4. Disconnect removes server-side connection registration.

## Constraints

- RED-only start.
- Use in-process test doubles; no external broker.

## Acceptance

`.venv/bin/pytest apps/api/tests/test_sse.py -q`
