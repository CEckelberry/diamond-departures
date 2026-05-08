# P6-03 verification (between-games / no-games-today states)

Date: 2026-05-08

## RED evidence

- Command: `node --test apps/web/tests/between-games-state.test.mjs`
- Result: FAIL before implementation (missing idle-state header copy and missing idle-mode SSE policy hooks).

## GREEN verification

1. `node --test apps/web/tests/between-games-state.test.mjs apps/web/tests/offseason-state.test.mjs apps/web/tests/preview-mode.test.mjs apps/web/tests/board-sse-wiring.test.mjs`
   - Result: PASS
2. `node --test apps/web/tests/*.test.mjs`
   - Result: PASS (57 passed)
3. `pnpm --filter web check`
   - Result: PASS (warnings only, no errors)

## Implementation notes

- Header now renders idle-state copy for `between` / `off-game`:
  - `No games until ... · in N hours`
  - `No games today` fallback for long/no ETA windows.
- Board page keeps stream open for non-off-season states and forwards `idleMode` to SSE.
- SSE client now accepts `idleMode` option and applies slower reconnect backoff in idle states.
