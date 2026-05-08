# P6-01 verification (off-season banner + stream suppression)

Date: 2026-05-08

## RED evidence

- Command: `node --test apps/web/tests/offseason-state.test.mjs`
- Result: FAIL before implementation (missing off-season banner copy and no `/api/season-state` guard in board page).

## GREEN verification

1. `node --test apps/web/tests/offseason-state.test.mjs`
   - Result: PASS (3 passed)
2. `node --test apps/web/tests/*.test.mjs`
   - Result: PASS (51 passed)
3. `pnpm --filter web check`
   - Result: PASS (warnings only, no errors)

## Implementation notes

- Header now renders off-season banner: `[Year] regular season · final` + `next season ...` countdown text.
- Board page polls `/api/season-state` and suppresses `openBoardStream(...)` when `seasonMode === 'off-season'`.
- Stat picker remains active in page layout for off-season sorting interactions.
