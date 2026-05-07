# P4-04 verification (board structure)

Date: 2026-05-07

## RED evidence

1. `node --test apps/web/tests/board-structure.test.mjs`
   - Result: FAIL (`Board.svelte` and `Row.svelte` missing).

## GREEN verification

1. `node --test apps/web/tests/board-structure.test.mjs`
   - Result: PASS (2 tests).
2. `pnpm --filter web check`
   - Result: PASS (0 errors, 1 pre-existing `@types/node` warning).
3. `node --test apps/web/tests/layout-shell.test.mjs apps/web/tests/board-header.test.mjs apps/web/tests/view-controls.test.mjs apps/web/tests/board-structure.test.mjs`
   - Result: PASS (8 tests).

## Notes

- Added `Board.svelte` + `Row.svelte` scaffold with fixed column grid, 36px row height, and 100-row placeholder render path.
- Updated root page to compose Header, ViewTabs, StatPicker, and Board into one board screen.
