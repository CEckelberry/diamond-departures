# Packet P3-04-RED — sound integration tests first

## Goal

Task 3.4 RED start: define failing tests for flap sound debounce + persistence.

## Scope

1. Add tests for sound store defaults + localStorage persistence.
2. Add tests for sound manager debouncing (`single` vs `many`).
3. Add tests that volume default is `0.3`.

## Acceptance

- `node --test apps/web/tests/flap-sound.test.mjs`
- `pnpm --filter web check`
