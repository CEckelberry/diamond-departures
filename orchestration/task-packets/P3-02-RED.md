# Packet P3-02-RED — single-cell flap animation tests first

## Goal

Task 3.2 RED start: create failing tests for animation queueing + reduced-motion behavior.

## Scope

1. Add node tests for flip sequencing helpers (450ms phase timings).
2. Add tests for queued updates (`a -> b -> c`) preserving order.
3. Add tests for reduced-motion shortcut (instant swap + flash signal).

## Acceptance

- `node --test apps/web/tests/flap-animation.test.mjs`
- `pnpm --filter web check`
