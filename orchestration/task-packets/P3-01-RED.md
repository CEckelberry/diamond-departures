# Packet P3-01-RED — split-flap single-cell visual tests first

## Goal

Task 3.1 RED start: force a failing compile/check for missing `Cell.svelte` component contract.

## Scope

1. Add a flap lab page that imports `Cell.svelte` from `src/lib/components/flap/Cell.svelte`.
2. Render a 10-cell sample row using varied characters (`8`, `M`, `I`, etc).
3. Run Svelte static checks and capture failing RED due to missing component.

## Acceptance

`pnpm --filter web check`
