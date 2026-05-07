# P4-01 verification (layout shell)

Date: 2026-05-07

## RED evidence

1. `node --test apps/web/tests/layout-shell.test.mjs`
   - Result: FAIL (missing `Nav.svelte`/`Footer.svelte`, layout import assertions failed).

## GREEN verification

1. `node --test apps/web/tests/layout-shell.test.mjs`
   - Result: PASS (2 tests).
2. `pnpm --filter web check`
   - Result: PASS (0 errors, 1 pre-existing `@types/node` warning).

## Notes

- Added global shell components (`Nav`, `Footer`) and composed them in root `+layout.svelte`.
- Layout now uses fixed top nav and footer below route content for all pages.
