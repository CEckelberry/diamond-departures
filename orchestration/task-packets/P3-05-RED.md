# Packet P3-05-RED — flap component test page tests first

## Goal

Task 3.5 RED start: create failing checks for `/test/flap` route and control surface.

## Scope

1. Add route import references for missing flap test page.
2. Add checks for control IDs (`single`, `word`, `storm`, `row-shift`).
3. Add dev-flag gating expectation.

## Acceptance

- `node --test apps/web/tests/flap-route.test.mjs`
- `pnpm --filter web check`
