# Packet P1-01-FULL — complete hitting stats package (GREEN)

## Goal
Close Task 1.1 fully for current scope: add wOBA weights file, weight loader, LeagueContext, wRC+, tests passing, and coverage >= 90 for `packages/stats/hitting`.

## Context snippets (TASKS.md / STATS.md)
- Task 1.1 outputs include `woba.py`, `wrc.py`, `woba_weights_2026.json`, table-driven tests, LeagueContext passed into wRC+ and similar adjusted stats.
- STATS wOBA formula: `(0.69*BB + 0.72*HBP + 0.89*1B + 1.27*2B + 1.62*3B + 2.10*HR) / (AB + BB - IBB + SF + HBP)`
- STATS wRC+ formula: `100 * ((wOBA - lgwOBA) / wOBAScale + lgRuns/PA + (lgRuns/PA - PF * lgRuns/PA)) / (lgRuns/PA)`
- Yearly weights drift and should be stored in a 2026 JSON file.

## Required implementation
1. Add `packages/stats/hitting/woba_weights_2026.json` with year and explicit weight keys used by loader.
2. Add `packages/stats/hitting/woba.py`:
   - `WOBAWeights` dataclass
   - `load_woba_weights(year: int = 2026) -> WOBAWeights`
   - `woba(...)` function matching STATS formula with denominator guard
3. Add `packages/stats/hitting/wrc.py`:
   - `LeagueContext` dataclass with league_woba, woba_scale, league_runs_per_pa, park_factor
   - `wrc_plus(...)` consuming context + weights and matching STATS formula
   - zero guard when context denominator terms are 0
4. Update package exports in `packages/stats/hitting/__init__.py`.
5. Keep/adjust tests so RED suite now passes.
6. Ensure public functions have formula docstrings.

## Acceptance checks
- `.venv/bin/pytest packages/stats/hitting/tests -q`
- `.venv/bin/pytest packages/stats/hitting/tests --cov=packages/stats/hitting --cov-report=term-missing --cov-fail-under=90 -q`
