# Packet P1-02-RED — pitching stats tests first

## Goal
Execute RED for Task 1.2 with tests for basic pitching rates, FIP/xFIP constants, SIERA, and ERA+.

## Context snippets (TASKS.md / STATS.md)
- Task 1.2 outputs: `packages/stats/pitching/basic.py`, `fip.py`, `siera.py`, `era_plus.py`, `cfip_2026.json`, and tests.
- STATS formulas:
  - ERA `(ER * 9) / IP`
  - WHIP `(BB + H) / IP`
  - K/9 `(K * 9) / IP`
  - BB/9 `(BB * 9) / IP`
  - K-BB% `(K - BB) / TBF`
  - FIP `((13*HR + 3*(BB+HBP) - 2*K) / IP) + cFIP`
  - xFIP uses league-average HR/FB instead of pitcher HR
  - ERA+ `100 * (lgERA / ERA) * PF`

## RED scope
Add failing tests for:
1. basic rates module with zero-denominator guards.
2. constants loader from `cfip_2026.json` (year + cFIP + league HR/FB).
3. FIP and xFIP formula checks using hand-computed samples.
4. SIERA deterministic sample + zero guards.
5. ERA+ sample + zero guards.

## Acceptance check
`.venv/bin/pytest packages/stats/pitching/tests -q`
