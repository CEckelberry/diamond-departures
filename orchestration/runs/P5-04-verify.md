# P5-04 verification (player detail URL routing)

Date: 2026-05-08

## RED evidence

- Command: `node --test apps/web/tests/player-route.test.mjs`
- Result: FAIL before implementation (`ENOENT` for `/player/[slug]/+page.ts` and `+page.svelte`).

## GREEN verification

1. `node --test apps/web/tests/player-route.test.mjs`
   - Result: PASS (3 passed)
2. `pnpm --filter web check`
   - Result: PASS (0 errors; pre-existing warnings only)

## Notes

- Added route loader `apps/web/src/routes/player/[slug]/+page.ts`.
- Loader fetches `/api/board`, slug-matches entries via `slugify`, and exposes `selectedPlayerId`.
- Added route page `apps/web/src/routes/player/[slug]/+page.svelte`.
- Page renders board context and open player panel, with back/close link to `/`.
