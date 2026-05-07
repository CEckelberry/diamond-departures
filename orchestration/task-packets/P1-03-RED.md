# Packet P1-03-RED — defensive parsers and qualification tests first

## Goal
If time, execute Task 1.3 RED for defensive stat extraction and noisy-sample qualification tagging.

## Context snippets (TASKS.md / STATS.md)
- Task 1.3 outputs: `packages/stats/defensive/parsers.py`, `qualification.py`, tests.
- STATS defensive notes:
  - DRS and UZR come from sources; main work is extraction/parsing.
  - UZR/150 may need normalization (some sources give per-game).
  - Mark `(noisy)` for sub-1000 inning defensive samples.
  - OAA from Statcast sources.

## RED scope
Create failing tests for:
1. parser extracting DRS/UZR/UZR150/OAA from representative source payload shapes.
2. UZR/150 normalization when source gives per-game value.
3. noisy qualification tag for innings below threshold.
4. stable/no tag for innings at or above threshold.

## Acceptance check
`.venv/bin/pytest packages/stats/defensive/tests -q`
