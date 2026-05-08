# P7-01 verification (performance pass)

Date: 2026-05-08

## RED evidence
- Command: `node --test apps/web/tests/performance-pass.test.mjs`
- Result: FAIL before implementation (no stream churn guard state, no compositor transform hints, no deferred TrendChart loading path, no Playwright perf script contract).

## GREEN verification
1. `node --test apps/web/tests/performance-pass.test.mjs`
   - Result: PASS (4 passed)
2. `node --test apps/web/tests/*.test.mjs`
   - Result: PASS (61 passed)
3. `pnpm --filter web check`
   - Result: PASS (warnings only)

## Performance-oriented implementation notes
- Page split seed/update effect from stream effect to reduce unnecessary re-seed/stream churn.
- Board row shell now includes compositor hints (`transform: translateZ(0)`, `contain: paint`).
- Player panel headshots now use `decoding="async"` + `fetchpriority="low"` and deferred chart hydration (`await import('./TrendChart.svelte')`).
- Added perf script contract file: `apps/web/tests/perf-busy-ingest.spec.ts`.

## GPU usage sample during local model generation
- Captured in `orchestration/runs/P7-01-gpu-usage.csv` while running `coder-fast`.
- Observed spikes into high utilization band (e.g. card0 ~86-90%).
