# Packet P1-04-RED — verification suite tests first

## Goal
Task 1.4 RED: lock verification dataset contract and failing harness tests under `packages/stats/verify`.

## Scope
Create failing tests + fixtures contract for:
1. `packages/stats/verify/data.json` shape with curated player-season rows.
2. verify harness loads dataset and runs each stat function against row inputs.
3. mismatch reporting includes player id/name, stat key, expected, actual, pct diff.
4. tolerance behavior (`<= 0.5%` pass, `> 0.5%` fail).
5. CI hook presence for verification run.

## Constraints
- RED only. No harness implementation.
- Keep deterministic fixture values.
- Use Python stack + `pytest`.

## Acceptance check
`.venv/bin/pytest packages/stats/verify/tests -q`
