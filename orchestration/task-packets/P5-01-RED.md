# Packet P5-01-RED — player detail panel shell tests first

## Goal

Task 5.1 RED start: add failing checks for player detail panel shell and board selection wiring.

## Scope

1. Add `apps/web/tests/player-panel-shell.test.mjs`.
2. Assert page imports `Panel.svelte` and holds selected player state.
3. Assert board row click selection wiring exists from `Row.svelte` -> `Board.svelte` -> `+page.svelte`.
4. Assert panel shell includes loading, error, and empty states.

## Acceptance

- `node --test apps/web/tests/player-panel-shell.test.mjs` (fails before GREEN)
