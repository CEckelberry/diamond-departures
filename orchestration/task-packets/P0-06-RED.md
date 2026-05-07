# Packet P0-06-RED — web init tests first (TDD)

## Goal

Write failing tests first for Task 0.6 SvelteKit + Tailwind + design tokens placeholder.

## Inputs

- `TASKS.md` Task 0.6
- `DESIGN.md` token names

## Scope (tests only)

Create tests for expected scaffold contract:

- `apps/web/package.json` exists and includes `sveltekit` + `tailwindcss`
- `apps/web/src/app.css` includes Diamond tokens: `--board-bg`, `--cell-bg`, `--cell-text`
- `apps/web/src/routes/+page.svelte` includes placeholder split-flap cell markup
- `apps/web/src/routes/+layout.svelte` includes dark/light toggle hook
- app imports all three fontsource families (Inter, Instrument Serif, JetBrains Mono)

## Required outputs

- `tests/web/test_web_bootstrap.py`

## Constraints

- No web implementation in RED packet.
- Tests should fail before scaffold exists.

## Acceptance checks

- `python3 -m unittest tests/web/test_web_bootstrap.py`
- RED failure present
