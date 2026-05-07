# P1-04 verification (stats verify suite)

Date: 2026-05-07

## RED evidence
- Command: `.venv/bin/pytest packages/stats/verify/tests -q`
- Result: failed on missing `packages.stats.verify.harness` and missing CI verification hook.

## GREEN verification
1. `.venv/bin/pytest packages/stats/verify/tests -q`
   - Result: PASS (7 passed)

## Notes
- Curated dataset contract added at `packages/stats/verify/data.json` with source metadata.
- Harness reports per-stat mismatch lines with player/stat/expected/actual/%diff.
- CI now runs `pytest packages/stats/verify/tests -q` in `stats-verify` job.
