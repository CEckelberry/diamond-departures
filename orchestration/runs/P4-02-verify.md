# P4-02 verification (header + status bar)

Date: 2026-05-07

## RED evidence

1. `node --test apps/web/tests/board-header.test.mjs`
   - Result: FAIL (`Header.svelte` missing).

## GREEN verification

1. `node --test apps/web/tests/board-header.test.mjs`
   - Result: PASS (2 tests).
2. `pnpm --filter web check`
   - Result: PASS (0 errors, 1 pre-existing `@types/node` warning).

## Notes

- Added `Header.svelte` with mode pill/status row, freshness summary, debug placeholder panel, and sound toggle.
- Wired periodic fetches to `/api/season-state` and `/api/freshness`.
