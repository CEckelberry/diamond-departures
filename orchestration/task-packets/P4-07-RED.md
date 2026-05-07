# Packet P4-07-RED — row reshuffle animation tests first

## Goal

Task 4.7 RED start: add failing checks for FLIP reshuffle + row-shift audio integration.

## Scope

1. Add `apps/web/tests/board-reshuffle-animation.test.mjs`.
2. Assert `Board.svelte` imports `flip` and applies `animate:flip` on keyed row wrappers (`row.playerId`).
3. Assert stagger logic (`index * 30`) and reduced-motion guard are present.
4. Assert row order change detection calls `playRowShift()` once per reshuffle.

## Acceptance

- `node --test apps/web/tests/board-reshuffle-animation.test.mjs` (fails before GREEN)
