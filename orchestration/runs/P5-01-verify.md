# P5-01 verification

## RED

- `node --test apps/web/tests/player-panel-shell.test.mjs`
- Result: FAIL before implementation (no player panel component, no row selection wiring).

## GREEN

- `node --test apps/web/tests/player-panel-shell.test.mjs`
- Result: PASS (3 tests).

## Additional

- `pnpm --filter web check`
- Result: PASS with pre-existing warning (`@types/node` missing).
