# Packet P3-03-RED — flap word component tests first

## Goal

Task 3.3 RED start: define failing tests for multi-character alignment + diff behavior.

## Scope

1. Add tests for fixed-width character mapping.
2. Add tests for right-aligned numeric strings and left-aligned text.
3. Add tests that diff marks only changed cells.

## Acceptance

- `node --test apps/web/tests/flap-word.test.mjs`
- `pnpm --filter web check`
