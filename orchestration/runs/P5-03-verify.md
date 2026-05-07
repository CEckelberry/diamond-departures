# P5-03 verification

## RED

- `node --test apps/web/tests/position-filtered-views.test.mjs`
- Result: FAIL before implementation (no view resolution payload + no filtered rows path).

## GREEN

- `node --test apps/web/tests/position-filtered-views.test.mjs apps/web/tests/board-rest-load.test.mjs`
- Result: PASS.
- `node --test apps/web/tests/view-controls.test.mjs apps/web/tests/board-structure.test.mjs apps/web/tests/board-rest-load.test.mjs apps/web/tests/board-sse-wiring.test.mjs apps/web/tests/board-reshuffle-animation.test.mjs apps/web/tests/player-panel-shell.test.mjs apps/web/tests/player-trend-chart.test.mjs apps/web/tests/position-filtered-views.test.mjs`
- Result: PASS (20 tests).

## Additional

- `pnpm --filter web check`
- Result: PASS with pre-existing warning (`@types/node` missing).
