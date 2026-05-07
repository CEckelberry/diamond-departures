# Packet P4-06-RED — SSE wiring tests first

## Goal

Task 4.6 RED start: add failing checks for SSE client/store wiring and delta application hooks.

## Scope

1. Add `apps/web/tests/board-sse-wiring.test.mjs`.
2. Assert `src/lib/api/sse.ts` exposes stream opener using `EventSource('/api/board/sse?...')` with snapshot/delta handlers and reconnect backoff.
3. Assert `src/lib/stores/board.ts` exposes `applySnapshot` and `applyDelta` with rank/stat updates.
4. Assert `+page.svelte` opens/closes stream in lifecycle and forwards events into store mutators.

## Acceptance

- `node --test apps/web/tests/board-sse-wiring.test.mjs` (fails before GREEN)
