# P3-01 verification (split-flap single-cell visual)

Date: 2026-05-07

## RED evidence

- Command: `pnpm --filter web check`
- Result: RED failed with missing module error for `$lib/components/flap/Cell.svelte` imported by `src/routes/flap-lab/+page.svelte`.

## GREEN verification

1. `pnpm --filter web check`
   - Result: PASS (0 errors, 1 pre-existing warning about missing `@types/node`).

## Notes

- Added `Cell.svelte` static split-flap cell with top/bottom faces and 1px hairline.
- Added props: `value` (required), `width` default `28`, `height` default `36`.
- Added flap lab page rendering 10 cells (`8`, `M`, `I`, etc.) for visual QA.
