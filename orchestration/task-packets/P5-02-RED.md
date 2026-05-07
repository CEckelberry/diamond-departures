# Packet P5-02-RED — player trend chart integration tests first

## Goal

Task 5.2 RED start: failing tests for trend chart integration in player panel.

## Scope

1. Add `apps/web/tests/player-trend-chart.test.mjs`.
2. Assert `Panel.svelte` fetches `/api/players/{id}/history?stat=...`.
3. Assert `TrendChart.svelte` exists and renders SVG/polyline sparkline shell.
4. Assert panel passes history points + selected stat into chart.

## Acceptance

- `node --test apps/web/tests/player-trend-chart.test.mjs` (fails before GREEN)
