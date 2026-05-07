# Packet P4-04-RED — board structure tests first

## Goal

Task 4.4 RED start: add failing checks for board + row composition using flap word cells.

## Scope

1. Add tests for `Board.svelte` and `Row.svelte` existence.
2. Assert board defines consistent column headers and renders 100-row list region.
3. Assert row composes `Word.svelte` for rank/player/team/position/stat cells.
4. Assert row height and grid column alignment styles are present.

## Acceptance

- `node --test apps/web/tests/board-structure.test.mjs`
- `pnpm --filter web check`
