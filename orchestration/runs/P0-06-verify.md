# P0-06 verification (SvelteKit init + tokens)

Date: 2026-05-07

## Assumptions
- Svelte CLI `sv create` output is accepted scaffold baseline.
- Tailwind v4 via `@tailwindcss/vite` is valid for this phase.
- Light mode changes app chrome only; board tokens remain dark defaults.

## RED -> GREEN evidence
- RED: `python3 -m unittest tests/web/test_web_bootstrap.py -v` failed with missing `apps/web` files.
- GREEN: same test passes after scaffold + token/theme/page updates.

## Verification commands + outcomes
1. `python3 -m unittest tests/web/test_web_bootstrap.py -v` -> PASS
2. `pnpm --filter web dev -- --host 0.0.0.0 --port 5173` -> START PASS (`VITE ready`, localhost 5173 served; command terminated by timeout for smoke test)

## Result
- Packet P0-06 accepted.
