# Packet P4-02-RED — header + status bar tests first

## Goal

Task 4.2 RED start: add failing checks for board header/status bar component.

## Scope

1. Add tests for `apps/web/src/lib/components/board/Header.svelte` existence.
2. Assert mode pill mapping (live/between/off-game/off-season) with live pulse class.
3. Assert freshness summary, last-update text, debug-panel placeholder toggle.
4. Assert sound toggle plumbing via `$lib/stores/sound`.

## Acceptance

- `node --test apps/web/tests/board-header.test.mjs`
- `pnpm --filter web check`
