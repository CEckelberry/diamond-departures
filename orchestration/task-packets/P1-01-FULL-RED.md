# Packet P1-01-FULL-RED — complete hitting package tests first

## Goal

Finish Task 1.1 gaps with tests-first: wOBA weights file loading, LeagueContext, wRC+, doc-comment expectations, and coverage gate.

## Context snippets (TASKS.md / STATS.md)

- TASKS 1.1 outputs require: `woba.py`, `wrc.py`, `woba_weights_2026.json`, tests, `LeagueContext` passed into adjusted stats, and coverage >90%.
- STATS wOBA formula: `(0.69*BB + 0.72*HBP + 0.89*1B + 1.27*2B + 1.62*3B + 2.10*HR) / (AB + BB - IBB + SF + HBP)`
- STATS wRC+ formula: `100 * ((wOBA - lgwOBA) / wOBAScale + lgRuns/PA + (lgRuns/PA - PF * lgRuns/PA)) / (lgRuns/PA)`
- STATS note: weights drift yearly; update annually.

## Scope (RED only)

Add failing tests for:

1. `woba()` with explicit weights object and denominator/IBB edge guards.
2. weight loading from `woba_weights_2026.json`.
3. `LeagueContext` required fields and usage in `wrc_plus()`.
4. `wrc_plus()` expected values for a hand-verified sample and zero guards.
5. docstrings present on all public hitting stat functions.
6. pytest coverage gate >= 90% for `packages/stats/hitting`.

## Constraints

- RED only. No new implementation logic.
- Keep existing `test_basic.py` passing style.
- Use deterministic, hand-computed expected values.

## Acceptance check

`.venv/bin/pytest packages/stats/hitting/tests -q`
