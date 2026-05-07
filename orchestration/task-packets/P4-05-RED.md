# Packet P4-05-RED — initial board load tests first

## Goal

Task 4.5 RED start: add failing checks for REST-backed board load.

## Scope

1. Add `apps/web/tests/board-rest-load.test.mjs`.
2. Assert `+page.ts` defines `load` and fetches `/api/board` with `view` + `sort` params.
3. Assert `+page.svelte` consumes `data`, passes `rows` into `Board`, and includes `.board-skeleton` loading UI.

## Acceptance

- `node --test apps/web/tests/board-rest-load.test.mjs` (fails before GREEN)
