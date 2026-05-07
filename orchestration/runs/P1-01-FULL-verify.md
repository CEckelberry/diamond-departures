# P1-01 FULL verification (hitting complete)

Date: 2026-05-07

## RED evidence
- Command: `.venv/bin/pytest packages/stats/hitting/tests -q`
- Result: import errors for missing `packages.stats.hitting.woba` and `packages.stats.hitting.wrc` before GREEN implementation.

## GREEN verification
1. `.venv/bin/pytest packages/stats/hitting/tests -q`
   - Result: PASS (15 passed)
2. `.venv/bin/pytest packages/stats/hitting/tests --cov=packages/stats/hitting --cov-report=term-missing --cov-fail-under=90 -q`
   - Result: PASS, total coverage 97.32% (threshold 90% satisfied)

## Reviewer-style self-check
- Formula alignment: wOBA and wRC+ implemented exactly per STATS.md formula text.
- Context modeling: `LeagueContext` carries league-adjustment inputs and is required in wRC+.
- Data contract: `woba_weights_2026.json` year-keyed file exists and loader enforces shape.
- Risk note: wOBA numerator currently uses total BB value (STATS formula literal), not uBB-specific weighting variant.
