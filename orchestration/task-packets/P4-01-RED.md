# Packet P4-01-RED — layout shell tests first

## Goal

Task 4.1 RED start: add failing checks for global app shell with nav + footer.

## Scope

1. Add tests expecting `Nav.svelte` and `Footer.svelte` components.
2. Assert `+layout.svelte` imports and renders nav/footer around page content.
3. Assert nav is fixed-top and footer stays after main content flow.

## Acceptance

- `node --test apps/web/tests/layout-shell.test.mjs`
- `pnpm --filter web check`
