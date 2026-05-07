# P4-03 verification (view tabs + stat picker)

Date: 2026-05-07

## RED evidence

1. `node --test apps/web/tests/view-controls.test.mjs`
   - Result: FAIL (`ViewTabs.svelte` and `StatPicker.svelte` missing).

## GREEN verification

1. `node --test apps/web/tests/view-controls.test.mjs`
   - Result: PASS (2 tests).
2. `pnpm --filter web check`
   - Result: PASS (0 errors, 1 pre-existing `@types/node` warning).

## Notes

- Added URL-synced `ViewTabs.svelte` with third-tab position dropdown and outside-click close handling.
- Added URL-synced `StatPicker.svelte` with hitter/pitcher stat families and horizontal scroll chip row.
