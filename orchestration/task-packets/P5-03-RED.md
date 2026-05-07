# Packet P5-03-RED — position-filtered views end-to-end tests first

## Goal

Task 5.3 RED start: add failing checks for position-filtered views from URL controls to rendered rows.

## Scope

1. Add `apps/web/tests/position-filtered-views.test.mjs`.
2. Assert `+page.ts` resolves position queries into stable API view + position mode.
3. Assert `+page.svelte` applies client-side position filtering for unsupported backend slices.
4. Assert filter state remains URL-driven (`view=positions&position=...`).

## Acceptance

- `node --test apps/web/tests/position-filtered-views.test.mjs` (fails before GREEN)
