# Packet P4-03-RED — view tabs + stat picker tests first

## Goal

Task 4.3 RED start: add failing checks for shareable URL-driven view and stat controls.

## Scope

1. Add tests for `ViewTabs.svelte` and `StatPicker.svelte`.
2. Assert URL search param writes for `view`, `sort`, and optional `position`.
3. Assert position dropdown outside-click close handling.
4. Assert stat picker list switches by hitter/pitcher view families.

## Acceptance

- `node --test apps/web/tests/view-controls.test.mjs`
- `pnpm --filter web check`
