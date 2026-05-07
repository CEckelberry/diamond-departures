# P3-05 verification (flap component test page route)

Date: 2026-05-07

## RED evidence

1. `node --test apps/web/tests/flap-route.test.mjs`
   - Result: FAIL (`ENOENT` for missing `src/routes/test/flap/+page.svelte`).

## GREEN verification

1. `node --test apps/web/tests/flap-route.test.mjs`
   - Result: PASS (2 tests).
2. `pnpm --filter web check`
   - Result: PASS (0 errors, 1 pre-existing warning about node type defs).
3. `node --test apps/web/tests/flap-animation.test.mjs apps/web/tests/flap-word.test.mjs apps/web/tests/flap-sound.test.mjs apps/web/tests/flap-route.test.mjs`
   - Result: PASS (14 tests).

## Notes

- Added dev-gated `/test/flap` route with controls for single/word/storm flips and row-shift audio.
- Added scenario runner and sound controls for fast manual tuning.
