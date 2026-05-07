# P3-04 verification (sound integration)

Date: 2026-05-07

## RED evidence

1. `node --test apps/web/tests/flap-sound.test.mjs`
   - Result: FAIL (`ERR_MODULE_NOT_FOUND` for `src/lib/stores/sound.mjs`).

## GREEN verification

1. `node --test apps/web/tests/flap-sound.test.mjs`
   - Result: PASS (4 tests).
2. `pnpm --filter web check`
   - Result: PASS (0 errors, 1 pre-existing warning about node type defs).

## Notes

- Added persisted sound preferences store (default off, default volume 0.3).
- Added debounced flap sound manager (`single` vs `many` within 100ms window).
- Wired `Cell.svelte` animation path to `noteFlapFlip()` (reduced-motion path remains silent).
- Added static audio asset paths under `apps/web/static/audio/`.
