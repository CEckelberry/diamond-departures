# Packet P5-04-RED — Player detail URL routing tests first

## Goal

Create failing tests for `/player/[slug]` routing behavior and wiring.

## Scope (RED only)

- Add `apps/web/tests/player-route.test.mjs` with assertions for:
  1. route files exist: `src/routes/player/[slug]/+page.svelte` and `+page.ts`
  2. board remains visible behind panel (imports Board + Panel)
  3. selected player is derived from slug + entries
  4. a back/close navigation path to `/` exists

## Constraints

- RED only, no route implementation.
- Keep tests static/contract style (string/shape assertions).

## Acceptance

- `node --test apps/web/tests/player-route.test.mjs` fails before GREEN implementation.
